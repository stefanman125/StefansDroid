# About

An "Everything" mobile application that contains various modules for different types of daily workflows and habits. All data in the app can be synced with a self-hostable server in order to achieve some kind of backup. However, the app can also be used by itself.

Functionality of the app is separated by "modules", allowing the user to reduce UI clutter if all of the modules aren't used (which is most likely the case).

The following modules are either planned, or are being implemented.

## Tasks (being implemented)

Used to track to-do style tasks. Supports single and recurring tasks that can contain a title, description, location, category, and due date. There are no plans to support sub-tasks.

## Feeds (being implemented)

Used to track websites that post blogs/articles.

Can be used with websites that lack an RSS feed by comparing the websites "change-value" with a locally stored "change-value" taken at an ealier date. The change-value that is calculated from the website can be selected by the user when configuring the feed. The currently supported change-values include:

- Web Page Checksum - SHA256 checksum of the retrieved web page.
- Last-Modified HTTP Header - The `Last-Modified` HTTP header value found in an HTTP response.
- document.LastModified JS Function - The `document.LastModified` HTML DOM property.
- HTML Element Regex - A specific HTML element in the website found using a regular expression.

## Notes (planned)

Used to make and store notes using markdown.

## LLM Chat Assistant (planned)

An "AI" chat assistant that will have context about the user by reading their module data.

# Modules

## Tasks

Tasks are used to track to-do style tasks that you have to perform at some point in your life.

These tasks can be created as a one-time thing, or as a recurring task that comes up every day, week, or any other amount of days you want. This can be done by changing the `recurrenceRange` value to one of the following:

- `None` - No recurrence.

- `No End` - Duplicates the task based on the `interval` value. For example, if the `interval` value is set to `3`, then the task is duplicated every 3 days with the respective due date. Or, if the `interval` value is set to `[ 'tuesday', 'thursday' ]`, the task is duplicated twice every week and due every Tuesday and Thursday. Creates tasks in advance for the next 30 days.

- `Until` - Duplicates the task based on the `interval` value until the end date, and then stops. Even if the end date value goes past 30 days, tasks will not be created in advance past 30 days.

The `interval` value can either be an integer (specifying a number of days), or a list of weekdays (specifying which weekdays the task will be created and due).

## Feeds

# Storage

All module data is stored in a json file called a Collection, which can also used to separate data into "profiles".

Each module uses its own JSON structure. The following examples are different module "items" that will be stored in a collection once a user creates them within the app.

## Examples

### Task

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

### Feed

```json
{
  "id": 5,
  "title": "Harvard Health Blog",
  "category": "Health",
  "url": "https://www.health.harvard.edu/blog",
  "dateLastUpdated": 1711149000,
  "isUserUpToDate": false,
  "checksum": "bf0c97708b849de696e7373508b13c5ea92bafa972fc941d694443e494a4b84d"
}
```

### Note

```json
{
  "id": 1,
  "title": "Places I Wanna Visit",
  "category": "Travel",
  "content": "# Paris\n* Galeries Lafayette Haussmann\n# Malaysia\n* FUIYOH! Its Uncle Roger! Restaurant\n# Malmo\n* Disgusting Food Museum"
}
```

# Syncing

Each collection has a single `dateModified` parameter. This parameter is used to keep track of which collection is the latest (the remote collection on the server, or the local collection on the mobile app).

When the mobile app begins a sync, it will decide whether to overwrite the local task collection file (assuming the `dateModified` parameter on the remote collection is higher than the local collection), or update the remote collection with the local one.

# Server

## Configuration/Installation

StefansDroid comes with a self-hostable server. Once configured, it will store all the collections used by the mobile app. The server is written in Python using [Flask](https://flask.palletsprojects.com/en/3.0.x/), so it needs Flask installed, as well as some other Python components.

```shell
$ pip3 install -r requirements.txt
```

A production server should be used to run in a stable environment. Gunicorn can be used to achieve this.

```shell
$ pip3 install gunicorn
```

Then, start the server on the desired port.

```shell
$ gunicorn -b 0.0.0.0:443 app:app
```

Once the server is up and running, configure the server address in the mobile application.

[StefansDroid Settings View](Images/1.png)

# Mobile App

In the app folder you will find the project to build app. The APK will be added as a release as well.

## Building the App

```shell
$ briefcase package android
$ cd dist
dist $ java -jar bundletool-all-1.17.1.jar build-apks --bundle=StefansDroid-0.0.1.aab --output=StefansDroid-Alpha.apks --mode=universal
dist $ unzip StefansDroid-Alpha.apks
```
