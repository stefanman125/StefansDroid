# About

A simple todo mobile application and server for self-hosting and synchronization.

# Protocol

## Storage

Instead of VTODO, a custom protocol is used to store and manipulate the data.

A single json file is used to store the task data. Below is an example of a task collection named `my-daily-groceries` containing a single task that recurs every 7 days.

`my-daily-groceries.json`

```json
{
  "id": 0,
  "title": "Buy Bread",
  "description": "Buy some bread while grocery shopping. Preferably something sourdough or baguette.",
  "location": "Best Bread Bakery, Vaughan, ON A1A 1A1",
  "category": "Grocery",
  "dueDate": 1711149159,
  "recurrence": {
    "recurrenceRange": "noEnd",
    "interval": 10080,
    "endDate": 1713136359
  },
  "completed": false
}
```

## Syncing

Each collection has a single `dateModified` parameter. This parameter is used to keep track of the latest task collection on each device.

When the mobile app updates a task collection, it will decide to overwrite the local task collection file based on the `dateModified` parameter of the remote task collection. If the `lastModified` value of the remote server's task collection is earlier than the local task collection, the local task collection will be pushed to the remote server. Otherwise, it will update the local task collection with the remote server's task collection.

# Server

## Configuration

Simple Tasks comes with a self-hostable server. Once configured, it will store all the task collections. To configure, simply run `main.py` on a given port and make sure that the web server is accessible from the associated devices.

```shell
$ python3 main.py
```

Once the server is up, add the server in the application. Each added server has its own password that is used in a Basic Authentication header.

[img here showing a server being added in the android app]()

## Backup
