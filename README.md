# About

A simple todo mobile application and server for self-hosting and synchronization.

# Protocol

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
