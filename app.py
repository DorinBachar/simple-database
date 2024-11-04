from flask import Flask, request
from google.cloud import datastore
import os
from datetime import datetime

app = Flask(__name__)
client = datastore.Client()

# Save command to history
def save_history(command, name, value, previous_value=None):
    key = client.key("History")
    entity = datastore.Entity(key=key)
    entity.update({
        "command": command,
        "name": name,
        "value": value,
        "previous_value": previous_value,
        "timestamp": datetime.utcnow()
    })
    client.put(entity)

# Save undone command to redo history
def save_redo_history(command, name, value, previous_value=None):
    key = client.key("RedoHistory")
    entity = datastore.Entity(key=key)
    entity.update({
        "command": command,
        "name": name,
        "value": value,
        "previous_value": previous_value,
        "timestamp": datetime.utcnow()
    })
    client.put(entity)

def set_variable_no_history(name, value):
    key = client.key("Variable", name)
    entity = datastore.Entity(key=key)
    entity["value"] = value
    client.put(entity)

def unset_variable_no_history(name):
    key = client.key("Variable", name)
    client.delete(key)

# Get last history entry for a specific variable
def get_last_history():
    query = client.query(kind="History")
    query.order = ["-timestamp"]
    results = list(query.fetch(limit=1))
    return results[0] if results else None

# Delete last command from history
def delete_last_history():
    query = client.query(kind="History")
    query.order = ["-timestamp"]
    results = list(query.fetch(limit=1))
    if results:
        client.delete(results[0].key)

# Get last undone command from redo history
def get_last_redo_history():
    query = client.query(kind="RedoHistory")
    query.order = ["-timestamp"]
    results = list(query.fetch(limit=1))
    return results[0] if results else None

# Delete last undone command from redo history
def delete_last_redo_history():
    query = client.query(kind="RedoHistory")
    query.order = ["-timestamp"]
    results = list(query.fetch(limit=1))
    if results:
        client.delete(results[0].key)

# Clear redo history when a new command is issued
def clear_redo_history():
    redo_query = client.query(kind="RedoHistory")
    redo_keys = [entity.key for entity in redo_query.fetch()]
    client.delete_multi(redo_keys)

# Retrieve the value of a variable
def get_variable(name):
    key = client.key("Variable", name)
    entity = client.get(key)
    return entity["value"] if entity else None

# Unset (delete) a variable
def unset_variable(name):
    value = get_variable(name)
    if value is not None:
        save_history("unset", name, None, value)
        clear_redo_history()  
        key = client.key("Variable", name)
        client.delete(key)

# Count the number of variables with a specific value
def count_variables_by_value(value):
    query = client.query(kind="Variable")
    query.add_filter("value", "=", value)
    return len(list(query.fetch()))

# Set variable with history saving
def set_variable(name, value):
    previous_value = get_variable(name)
    key = client.key("Variable", name)
    entity = datastore.Entity(key=key)
    entity["value"] = value
    client.put(entity)
    save_history("set", name, value, previous_value)
    clear_redo_history()

# Undo the last set/unset command
def undo_last_command():
    last_command = get_last_history()
    if not last_command:
        return "NO COMMANDS"

    command = last_command["command"]
    name = last_command["name"]
    value = last_command["value"]
    previous_value = last_command["previous_value"]
    
    save_redo_history(command, name, value, previous_value)
   
    if command == "set":
        if previous_value is None:
            unset_variable_no_history(name)
            result = f"{name} = None"
        else:
            set_variable_no_history(name, previous_value)
            result = f"{name} = {previous_value}"
    elif command == "unset":
        set_variable_no_history(name, value)
        result = f"{name} = {value}"

    delete_last_history()
    return result

# Redo the last undone command
def redo_last_command():
    last_undone = get_last_redo_history()
    if not last_undone:
        return "NO COMMANDS"

    command = last_undone["command"]
    name = last_undone["name"]
    value = last_undone["value"]
    previous_value = last_undone["previous_value"]

    if command == "set":
        set_variable_no_history(name, value)
    elif command == "unset":
        unset_variable_no_history(name)

    save_history(command, name, value, previous_value)
    delete_last_redo_history()

    return f"{name} = {get_variable(name) if get_variable(name) is not None else 'None'}"

# Clear all data in the datastore, including history
def clear_data():
    query = client.query(kind="Variable")
    keys = [entity.key for entity in query.fetch()]
    client.delete_multi(keys)
    client.delete_multi([entity.key for entity in client.query(kind="History").fetch()])
    client.delete_multi([entity.key for entity in client.query(kind="RedoHistory").fetch()])
    return "CLEANED"

# Retrieve all variables and their values
def get_all_variables():
    query = client.query(kind="Variable")
    results = list(query.fetch())
    variables = {entity.key.name: entity["value"] for entity in results}
    return variables

# Route to display all history entries
@app.route('/history')
def history_handler():
    query = client.query(kind="History")
    query.order = ["timestamp"]
    results = list(query.fetch())
    history_entries = [
        f"{entry['command']} {entry['name']} = {entry['value']} (Previous: {entry['previous_value']})"
        for entry in results
    ]
    return "\n".join(history_entries) if history_entries else "No history available"

# Route handlers and other utility functions
@app.route('/set')
def set_handler():
    name = request.args.get("name")
    value = request.args.get("value")
    if name and value:
        set_variable(name, value)
        return f"{name} = {value}"
    return "Invalid input", 400

# Route for retrieving a variable
@app.route('/get')
def get_handler():
    name = request.args.get("name")
    if name:
        value = get_variable(name)
        return value if value else "None"
    return "Invalid input", 400

# Route for unsetting a variable
@app.route('/unset')
def unset_handler():
    name = request.args.get("name")
    if name:
        unset_variable(name)
        return f"{name} = None"
    return "Invalid input", 400

# Route for counting variables with a specific value
@app.route('/numequalto')
def numequalto_handler():
    value = request.args.get("value")
    if value:
        count = count_variables_by_value(value)
        return str(count)
    return "Invalid input", 400

# Route for undo
@app.route('/undo')
def undo_handler():
    return undo_last_command()

# Route for redo
@app.route('/redo')
def redo_handler():
    return redo_last_command()

# Route for clearing all data
@app.route('/end')
def end_handler():
    return clear_data()

# Route for displaying all variables
@app.route('/variablesStatus')
def all_variables_handler():
    variables = get_all_variables()
    if variables:
        return "\n".join([f"{name} = {value}" for name, value in variables.items()])
    return "No variables set"

@app.route('/')
def home():
    return "New: Welcome to Database API"

# Main entry point
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))


