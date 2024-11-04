# Task2:Database App on Google App Engine

This project is a simple database application that runs on Google App Engine. The app allows users to send HTTP requests to manage variables, supporting basic commands like setting and unsetting variables, counting by values, and undoing/redoing recent changes.

Home URL: https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app

**Important Notes:**

**Stateful Management:** Each request is stateless by design on Google App Engine, so I use Google Datastore to store data between requests.

**Data Persistence:** All changes and undo/redo history are managed in Datastore, allowing consistent state across requests.

**Graceful Handling of Errors:** The app is designed to handle invalid inputs and unexpected requests smoothly.

**Example Sequences for Testing**

**Sequence 1:**

Set:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/set?name=ex&value=10
Output: ex = 10

Get:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/get?name=ex
Output: 10

Unset:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/unset?name=ex
Output: ex = None

Get:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/get?name=ex
Output: None

End:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/end
Output: CLEANED

**Sequence 2:**

Set:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/set?name=a&value=10
Output: a = 10

Set:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/set?name=b&value=10
Output: b = 10

NumEqualTo:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/numequalto?value=10
Output: 2

NumEqualTo:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/numequalto?value=20
Output: 0

Set:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/set?name=b&value=30
Output: b = 30

NumEqualTo:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/numequalto?value=10
Output: 1

End:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/end
Output: CLEANED


**Sequence 3:**

Set:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/set?name=a&value=10
Output: a = 10

Set:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/set?name=b&value=20
Output: b = 20

Get:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/get?name=a
Output: 10

Get:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/get?name=b
Output: 20

Undo:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/undo
Output: b = None

Get:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/get?name=a
Output: 10

Get:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/get?name=b
Output: None

Set:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/set?name=a&value=40
Output: a = 40

Get:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/get?name=a
Output: 40

Undo:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/undo
Output: a = 10

Get:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/get?name=a
Output: 10

Undo:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/undo
Output: a = None

Get:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/get?name=a
Output: None

Undo:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/undo
Output: NO COMMANDS

Redo:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/redo
Output: a = 10

Redo:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/redo
Output: a = 40

End:
Input:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/end
Output: CLEANED

**Improvement Idea:**
I discovered an improvement that could streamline the workflow and enhance the user experience: adding a command to display a complete list of variables and their current values. This feature would give users a quick database overview without requiring individual GET requests.

URL:  https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/all

**Returns all history. The history is deleted with the end command**

URL: https://dorinbenhur-20-ldweiqy2yq-uc.a.run.app/history











