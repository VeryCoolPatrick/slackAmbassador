# Slack Ambassidor

This is a bot to keep MS Teams users up to date what is going on in Slack channels.

Uses boost API for slack and power automate flow for teams.

## Power Automate Flow
![MS flow example](images/flowPostExample.png)

To get around registering an app with azure, this bot uses MS flows to handle all HTTP requests on teams end.
The flow accepts a JSON payload containing the message formated to HTML and an optional ID number.
If an id is given it will post the message as a reply to the message with the given ID. If the ID is empty it will post a new message. 
```JSON
{
    "message" : "HTML formated message",
    "threadId" : "Optional ID number"
}
```
The flow responds with the with ID of the newly posted teams message.
```JSON
{
    "messageId" : "New teams ID number"
}
```
