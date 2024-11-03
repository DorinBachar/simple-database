from flask import Flask, request
from google.cloud import datastore
import os
from datetime import datetime

app = Flask(__name__)
client = datastore.Client()

def save_history(command, name, value, previous_value=None):
    key = client.key("History")
    entity = datastore.Entity(key=key)
    entity.update({
        "command": command,
        "name": name,
        "value": value,
        "previous_value": previous_value,  # Save previous value for undo
        "timestamp": datetime.utcnow()
    })
    client.put(entity)


def get_last_history():
    query = client.query(kind="History")
    query.order = ["-timestamp"]
    results = list(query.fetch(limit=1))
    return results[0] if results else None

def delete_last_history():
    query = client.query(kind="History")
    query.order = ["-__key__"]
    results = list(query.fetch(limit=1))
    if results:
        client.delete(results[0].key)

# Set a variable
def set_variable(name, value):
    previous_value = get_variable(name)  # Get previous value before setting new one
    key = client.key("Variable", name)
    entity = datastore.Entity(key=key)
    entity["value"] = value
    client.put(entity)
    save_history("set", name, value, previous_value)

# Get a variable's value
def get_variable(name):
    key = client.key("Variable", name)
    entity = client.get(key)
    return entity["value"] if entity else None

# Unset a variable
def unset_variable(name):
    value = get_variable(name)
    if value is not None:
        key = client.key("Variable", name)
        client.delete(key)
        save_history("unset", name, None, value)  # Save the current value as previous
    return value

# Count variables with a specific value
def count_variables_by_value(value):
    query = client.query(kind="Variable")
    query.add_filter("value", "=", value)
    return len(list(query.fetch()))

def undo_or_redo(command_type):
    if command_type == "undo":
        last_command = get_last_history()
        if not last_command:
            return "NO COMMANDS"
        redo_stack.append(last_command)  # Save to redo stack in case of undo
    elif command_type == "redo":
        if not redo_stack:
            return "NO COMMANDS"
        last_command = redo_stack.pop()  # Retrieve last undone command for redo
    else:
        return "Invalid command type"

    command = last_command["command"]
    name = last_command["name"]
    value = last_command["value"] if command_type == "redo" else last_command["previous_value"]

    if command == "set":
        if value is not None:
            set_variable(name, value)
        else:
            unset_variable(name)
    elif command == "unset":
        set_variable(name, value)

    # Save back to history if it's a redo action
    if command_type == "redo":
        save_history(command, name, last_command["value"], last_command.get("previous_value"))
    else:
        client.delete(last_command.key)  # Delete last command in case of undo

    return f"{name} = {get_variable(name) if get_variable(name) is not None else 'None'}"


# Redo last undone command 
# Clear all data
def clear_data():
    query = client.query(kind="Variable")
    keys = [entity.key for entity in query.fetch()]
    client.delete_multi(keys)

    # Clear the history
    history_query = client.query(kind="History")
    history_keys = [entity.key for entity in history_query.fetch()]
    client.delete_multi(history_keys)

    return "CLEANED"

# Handle for setting a variable
@app.route('/set')
def set_handler():
    name = request.args.get("name")
    value = request.args.get("value")
    if name and value:
        set_variable(name, value)
        return f"{name} = {value}"
    return "Invalid input", 400

# Handle for getting a variable
@app.route('/get')
def get_handler():
    name = request.args.get("name")
    if name:
        value = get_variable(name)
        return value if value else "None"
    return "Invalid input", 400

# Handle for unsetting a variable
@app.route('/unset')
def unset_handler():
    name = request.args.get("name")
    if name:
        unset_variable(name)
        return f"{name} = None"
    return "Invalid input", 400

# Handle for counting variables by value
@app.route('/numequalto')
def numequalto_handler():
    value = request.args.get("value")
    if value:
        count = count_variables_by_value(value)
        return str(count)
    return "Invalid input", 400

# Handle for undo
@app.route('/undo')
def undo_handler():
    return undo_or_redo("undo")

# Handle for redo
@app.route('/redo')
def redo_handler():
    return undo_or_redo("redo")

# Handle for end/cleanup
@app.route('/end')
def end_handler():
    return clear_data()

@app.route('/')
def home():
    return "Welcome to Simple Database API"

# Main entry point
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))  
