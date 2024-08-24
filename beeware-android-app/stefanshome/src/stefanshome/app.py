import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, LEFT, RIGHT
from toga.colors import rgb
import httpx
import time
import textwrap
from pathlib import Path
import json

# Hardcoded path that I should probably change, but im okay with the idea of the collections being somewhere in Documents
save_path = "/storage/emulated/0/Documents/StefansHome/collections" # No trailing slash
collection_name = "my-grocery-list" # dont include the file extension
remote_server = "http://192.168.0.100:5000"
collection_skeleton = {"lastModified": 0, "tasks": [], "feeds": []}

class StefansHome(toga.App):
    # Simply clears the screen of all views when switching views
    def clear_all_views(self):
        self.main_box.clear()

    # Edit view for editing a specific task
    def draw_edit_task(self, task_id, mode):

        # Clear current view
        self.clear_all_views()

        task = self.get_collection(collection_name)["tasks"][self.get_index("task", task_id, self.get_collection(collection_name))]

        # Old Task attributes
        old_title = task["title"]

        # Used to recycle the view for creating new, and editing old tasks
        if (mode == "edit"):
            mode = "Editing Task"
        elif (mode == "new"):
            mode = "New Task"
        else:
            print("ERROR: draw_edit_task not given a proper mode")

        label_title = toga.Label(mode, style=Pack(font_size=28)) # Title
        spacer = toga.Box(style=Pack(background_color=rgb(237, 237, 237), height=75)) # Spacer
        input_new_title = toga.TextInput(value=old_title) # New Task Title input (starts with old task title as the filled input)
        new_title = toga.Box(children=[
            toga.Label("New Title", style=Pack(padding=(8, 0, 0, 0))),
            input_new_title
        ], style=Pack(
            direction=ROW
        ))

        # Button submit includes submitting the task ID of the task being modified, all the attributes of the new task in a dictionary, and the old collection
        button_submit = toga.Button("Submit", 
            on_press=lambda widget: 
                self.edit_submit_button("task", task["id"], {"id": task_id, "title": input_new_title.value, "description": task["description"], "location": task["location"], "category": task["category"], "dueDate": task["dueDate"], "recurrence": task["recurrence"], "completed": task["completed"]}, self.get_collection(collection_name)),
        ) # Submit changes. `lambda widget:` added to prevent the button being automatically pressed on startup, which happened if I didn't have that lambda code there.

        button_cancel = toga.Button("Cancel", 
            on_press=lambda widget: 
                self.edit_cancel_button(),
        ) # Cancel any pending changes

        button_box = toga.Box(children=[
            button_submit,
            button_cancel
        ], style=Pack(direction=ROW))

        edit_task = toga.Box(children=[
            label_title,
            spacer,
            new_title,
            button_box
        ],style=Pack(
            background_color=rgb(237, 237, 237),
            padding=(10, 10, 10, 10),
            direction=COLUMN,
            flex=1
        ))

        self.main_box.add(edit_task)

    # Handles the "cancel" button press in the edit task view
    def edit_cancel_button(self):
        self.clear_all_views()
        self.draw_main_view()

    # Handles the "submit" button press in the edit task view 
    def edit_submit_button(self, taskorfeed, id, new_taskorfeed, collection):
        self.change_item(taskorfeed, id, new_taskorfeed, collection)
        self.clear_all_views() 
        self.draw_main_view()

    # Returns the index of the task or feed in the collection based on the ID, since they are not ordered by ID (or at least, I don't imagine they will be at the time of writing this)
    def get_index(self, taskorfeed, id, collection):
        for item in collection["{taskorfeed}s".format(taskorfeed=taskorfeed)]:
            if item["id"] == id:
                return(collection["{taskorfeed}s".format(taskorfeed=taskorfeed)].index(item))

    # This function is responsible for changing task data. Depending on the ID of the changed task, it either changes an existing task, or creates a new one.
    def change_item(self, taskorfeed, id, new_taskorfeed, collection):
        collection["{taskorfeed}s".format(taskorfeed=taskorfeed)][self.get_index(taskorfeed, id, collection)] = new_taskorfeed 
        collection["lastModified"] = int(time.time())
        self.save_data(collection, collection_name)

    # Saves collection to file being currently used to store collection on the device's storage
    def save_data(self, collection, collection_name):
        try:
            with open("{save_path}/{collection_name}.json".format(save_path=save_path, collection_name=collection_name), 'w') as file:
                file.write(str(json.dumps(collection)))
            self.main_window.info_dialog("Success", "Collection Successfully saved to: '{path}/{collection_name}.json'".format(path=save_path, collection_name=collection_name))
        except Exception as e:
            self.main_window.info_dialog("Error", "Could not save collection to the local device with the following error:\n{error}".format(error=e))

    # Main view of the app
    def draw_main_view(self):
        main_view_box = toga.OptionContainer(content=[], style=Pack(flex=1))
        main_view_box.content.append(toga.OptionItem("Feeds", self.draw_feed_view(self.get_collection(collection_name))))
        main_view_box.content.append(toga.OptionItem("Tasks", self.draw_task_view(self.get_collection(collection_name))))

        self.main_box.add(main_view_box)

    # View used for seeing subscribed blogs
    def draw_feed_view(self, collection):
        feeds = collection["feeds"]

        # Option box containing read/unread filters
        not_up_to_date = toga.Box(style=Pack(padding=(5, 5, 5, 5), direction=COLUMN))
        up_to_date = toga.Box(style=Pack(padding=(5, 5, 5, 5), direction=COLUMN))

        num_no_up_to_date = 0

        for feed in feeds:
            if feed["isUserUpToDate"] == False:
                not_up_to_date.add(self.draw_feed(feed))
                not_up_to_date.add(self.draw_divider(rgb(255, 255, 255)))
                num_no_up_to_date += 1
            else:
                up_to_date.add(self.draw_feed(feed))
                up_to_date.add(self.draw_divider(rgb(255, 255, 255)))

        not_up_to_date_scroll_container = toga.ScrollContainer(content=not_up_to_date)
        up_to_date_scroll_container = toga.ScrollContainer(content=up_to_date)

        feed_option_box = toga.OptionContainer(content=[], style=Pack(flex=1))
        feed_option_box.content.append(toga.OptionItem("Not Up to Date ({num_no_up_to_date})".format(num_no_up_to_date=num_no_up_to_date), not_up_to_date_scroll_container))
        feed_option_box.content.append(toga.OptionItem("Up to Date", up_to_date_scroll_container))

        #self.main_box.add(feed_option_box)
        return(feed_option_box)
    
    def draw_divider(self, rgb):
        return toga.Divider(direction="HORIZONTAL", style=Pack(height=2, flex=1, background_color=rgb, padding=(10, 0, 0, 0)))

    # Draw a feed
    def draw_feed(self, feed):
        if (len(feed["title"]) > 20):
            feed_title = feed["title"][:20] + ".."
        else:
            feed_title = feed["title"]

        feed_date_last_updated = "{date} ({tz})".format(date=time.strftime('%Y-%m-%d %I:%M %p', time.localtime(feed["dateLastUpdated"])), tz=time.tzname[0])

        feed_update_mechanism = feed["updateMechanism"]

        title_date_option_box = toga.Box(children=[
            toga.Label("{feed_title}".format(feed_title=feed_title), style=Pack(font_size=20, color=rgb(0, 0, 0), padding=(2, 0, 2, 5))),
            toga.Label("{feed_date_last_updated}".format(feed_date_last_updated=feed_date_last_updated), style=Pack(font_size=10, color=rgb(61, 61, 61), padding=(2, 0, 2, 9))),
            ], style=Pack(direction=COLUMN))

        category_box = toga.Box(children=[
            toga.Label("{feed_category}".format(feed_category=feed["category"]), style=Pack(font_size=12, color=rgb(0, 0, 0), padding=(10, 0, 10, 150-len(feed["category"])), alignment='right', flex=1)),
            toga.Switch(text="Caught up?", value=feed["isUserUpToDate"], style=Pack(color=rgb(0, 0, 0), padding=(0, 20, 0, 40)))
        ], style=Pack(direction=COLUMN))

        top_half_box = toga.Box(children=[
            title_date_option_box,
            category_box,
        ], style=Pack(
            direction=ROW
        ))

        button_edit = toga.Button("Edit", 
            on_press=lambda widget: 
                self.draw_edit_feed(feed["id"], "edit")        
        ) 

        button_go_to_url = toga.Button("Go to URL",
            on_press=lambda widget:
                self.open_url_in_browser(feed["url"])
        )

        feed_box = toga.Box(children=[
            top_half_box,
            toga.Divider(direction="HORIZONTAL", style=Pack(height=2, flex=1, background_color=rgb(186, 186, 186), padding=(10, 0, 0, 10))),
            toga.Label("{feed_update_mechanism}".format(feed_update_mechanism=feed_update_mechanism), style=Pack(font_size=10, color=rgb(0, 0, 0), padding=(5, 0, 0, 10))),
            button_edit,
            button_go_to_url
            ], style=Pack(
                direction=COLUMN, 
                padding=0,
                background_color=rgb(212, 212, 212),
                height=200
                )) 

        return(feed_box)

    # Draw Edit Feed view
    def draw_edit_feed(self, feed_id, mode):

        # Clear current view
        self.clear_all_views()

        feed = self.get_collection(collection_name)["feeds"][self.get_index("feed", feed_id, self.get_collection(collection_name))]

        # Old Task attributes
        old_title = feed["title"]

        # Used to recycle the view for creating new, and editing old tasks
        if (mode == "edit"):
            mode = "Editing Feed"
        elif (mode == "new"):
            mode = "New Feed"
        else:
            print("ERROR: draw_edit_feed() not given a proper mode")

        label_title = toga.Label(mode, style=Pack(font_size=28)) # Title
        spacer = toga.Box(style=Pack(background_color=rgb(237, 237, 237), height=75)) # Spacer
        input_new_title = toga.TextInput(value=old_title) # New feed Title input (starts with old task title as the filled input)
        new_title = toga.Box(children=[
            toga.Label("New Title", style=Pack(padding=(8, 0, 0, 0))),
            input_new_title
        ], style=Pack(
            direction=ROW
        ))

        # Button submit includes submitting the task ID of the task being modified, all the attributes of the new task in a dictionary, and the old collection
        button_submit = toga.Button("Submit", 
            on_press=lambda widget: 
                self.edit_submit_button("feed", feed["id"], {"id": feed_id, "title": input_new_title.value, "category": feed["category"], "url": feed["url"], "dateLastUpdated": feed["dateLastUpdated"], "isUserUpToDate": feed["isUserUpToDate"], "updateMechanism": feed["updateMechanism"]}, self.get_collection(collection_name)),
        ) # Submit changes. `lambda widget:` added to prevent the button being automatically pressed on startup, which happened if I didn't have that lambda code there.

        button_cancel = toga.Button("Cancel", 
            on_press=lambda widget: 
                self.edit_cancel_button(),
        ) # Cancel any pending changes

        button_box = toga.Box(children=[
            button_submit,
            button_cancel
        ], style=Pack(direction=ROW))

        edit_feed = toga.Box(children=[
            label_title,
            spacer,
            new_title,
            button_box
        ],style=Pack(
            background_color=rgb(237, 237, 237),
            padding=(10, 10, 10, 10),
            direction=COLUMN,
            flex=1
        ))

        self.main_box.add(edit_feed)

    # Open URL in browser todo
    def open_url_in_browser(self, url):
        print("Going to URL: "+url)
        pass

    # View used for seeing tasks filtered by date, using an optionBox as a parent box
    def draw_task_view(self, collection):
        tasks = collection["tasks"]

        # Option Box containing date filters
        date_nodate = toga.Box(style=Pack(padding=(5, 5, 5, 5), direction=COLUMN))
        date_today = toga.Box(style=Pack(padding=(5, 5, 5, 5), direction=COLUMN))
        date_1weeks = toga.Box(style=Pack(padding=(5, 5, 5, 5), direction=COLUMN))
        date_overdue = toga.Box(style=Pack(padding=(5, 5, 5, 5), direction=COLUMN))
        date_alltasks = toga.Box(style=Pack(padding=(5, 5, 5, 5), direction=COLUMN))

        current_date_epoch = int(time.time())
        overdue_tasks = 0

        for task in tasks:
            date_alltasks.add(self.draw_task(task))
            date_alltasks.add(self.draw_divider(rgb(255, 255, 255)))
            if (task["dueDate"] == 0): # Check if any tasks have no due date
                date_nodate.add(self.draw_task(task))
                date_nodate.add(self.draw_divider(rgb(255, 255, 255)))
            elif (task["dueDate"] - current_date_epoch < 0): # Check if any tasks are overdue
                date_overdue.add(self.draw_task(task))
                date_overdue.add(self.draw_divider(rgb(255, 255, 255)))
                overdue_tasks += 1
            elif (task["dueDate"] - current_date_epoch <= 604800): # Check if any tasks are due in 7 days
                date_1weeks.add(self.draw_task(task))
                date_1weeks.add(self.draw_divider(rgb(255, 255, 255)))
                if (task["dueDate"] - current_date_epoch <= 86400): # Check if any tasks are due today
                    date_today.add(self.draw_task(task))
                    date_today.add(self.draw_divider(rgb(255, 255, 255)))

        date_nodate_scroll_container = toga.ScrollContainer(content=date_nodate)
        date_today_scroll_container = toga.ScrollContainer(content=date_today)
        date_1weeks_scroll_container = toga.ScrollContainer(content=date_1weeks)
        date_overdue_scroll_container = toga.ScrollContainer(content=date_overdue)
        date_alltasks_scroll_container = toga.ScrollContainer(content=date_alltasks)

        date_option_box = toga.OptionContainer(content=[], style=Pack(flex=1))
        date_option_box.content.append(toga.OptionItem("Today", date_today_scroll_container))
        date_option_box.content.append(toga.OptionItem("Next 7 Days", date_1weeks_scroll_container))
        date_option_box.content.append(toga.OptionItem("All Tasks", date_alltasks_scroll_container))
        date_option_box.content.append(toga.OptionItem("Overdue ({num_overdue})".format(num_overdue = overdue_tasks), date_overdue_scroll_container))
        date_option_box.content.append(toga.OptionItem("No Due Date", date_nodate_scroll_container))

        #self.main_box.add(date_option_box)
        return(date_option_box)
    
    # Takes task dictionary stored in JSON response
    def draw_task(self, taskAttributes):

        # Checks if a due date is set. If not, show no date
        if (taskAttributes["dueDate"] == 0):
            task_due_date = "No Due Date"
        else:
            task_due_date = "{date} ({tz})".format(date=time.strftime('%Y-%m-%d %I:%M %p', time.localtime(taskAttributes["dueDate"])), tz=time.tzname[0])

        # Checks if the title is too long. If so, truncate.
        if (len(taskAttributes["title"]) > 20):
            task_title = taskAttributes["title"][:20] + ".."
        else:
            task_title = taskAttributes["title"]

        title_date_option_box = toga.Box(children=[
            toga.Label("{task_title}".format(task_title=task_title), style=Pack(font_size=20, color=rgb(0, 0, 0), padding=(2, 0, 2, 5))),
            toga.Label("{task_due_date}".format(task_due_date=task_due_date), style=Pack(font_size=10, color=rgb(61, 61, 61), padding=(2, 0, 2, 9))),
            ], style=Pack(direction=COLUMN))

        category_box = toga.Box(children=[
            toga.Label("{task_category}".format(task_category=taskAttributes["category"]), style=Pack(font_size=12, color=rgb(0, 0, 0), padding=(10, 0, 10, 150-len(taskAttributes["category"])), alignment='right', flex=1)),
            toga.Switch(text="Complete?", value=taskAttributes["completed"], style=Pack(color=rgb(0, 0, 0), padding=(0, 20, 0, 80-len(task_due_date))))
        ], style=Pack(direction=COLUMN))

        top_half_box = toga.Box(children=[
            title_date_option_box,
            category_box,
        ], style=Pack(
            direction=ROW
        ))

        # Some quick logic that truncates any characters over the 200 character limit, so that it fits in the task view
        if (len(taskAttributes["description"]) > 200):
            task_description = taskAttributes["description"][:200] + "..."
        else:
            task_description = taskAttributes["description"]

        button_edit = toga.Button("Edit", 
            on_press=lambda widget: 
                self.draw_edit_task(taskAttributes["id"], "edit")        
        ) 

        task_box = toga.Box(children=[
            top_half_box,
            toga.Divider(direction="HORIZONTAL", style=Pack(height=2, flex=1, background_color=rgb(186, 186, 186), padding=(10, 0, 0, 10))),
            toga.Label("{task_description}".format(task_description=textwrap.fill(task_description, width=60)), style=Pack(font_size=10, color=rgb(0, 0, 0), padding=(5, 0, 0, 10))),
            button_edit
            ], style=Pack(
                direction=COLUMN, 
                padding=0,
                background_color=rgb(212, 212, 212),
                height=200
                )) 

        return(task_box)

    def settings_submit_button(self, new_collection_name, new_server_address):
        global collection_name 
        collection_name = new_collection_name
        global remote_server 
        remote_server = new_server_address
        self.edit_cancel_button()

    # Draw the settings menu
    def draw_settings(self, collection_name, remote_server):
        self.clear_all_views()

        input_collection_server_address = toga.TextInput()

        # Todo add these settings
        #        ("Auto Syncing", False, "Enable automatically syncing local collections with the remote server."),
        #        ("Auto Sync Interval", 5, "Time interval in minutes to automatically sync collections if Auto Syncing is enabled.")

        # Collection Management section
        collection_management_title = toga.Label("Collection Management", style=Pack(font_size=26, padding=(0, 0, 10, 0)))
        collection_management_server_address_input = toga.TextInput(value=remote_server)
        collection_management_server_address = toga.Box(children=[
            toga.Label("Collection Server Address", style=Pack(font_size=16)),
            collection_management_server_address_input
        ], style=Pack(
            direction=COLUMN
        ))
        collection_management_collection_name_input = toga.TextInput(value=collection_name)
        collection_management_collection_name = toga.Box(children=[
            toga.Label("Collection Name", style=Pack(font_size=16)),
            collection_management_collection_name_input
        ], style=Pack(
            direction=COLUMN
        ))
        settings_collection_management = toga.Box(children=[
            collection_management_title,
            collection_management_server_address,
            self.draw_divider(rgb(255, 255, 255)),
            collection_management_collection_name,
            self.draw_divider(rgb(255, 255, 255)),
        ], style=Pack(
            direction=COLUMN
        ))

        # All settings go in this box
        settings = toga.Box(children=[
            settings_collection_management
        ], style=Pack(
            direction=COLUMN,
            flex=1
        ))

        settings_and_values_box = toga.ScrollContainer(content=settings, style=Pack(flex=1))

        button_exit_without_saving = toga.Button("Exit without Saving", 
            on_press=lambda widget: 
                self.edit_cancel_button(),
            style=Pack(flex=1)
        ) # Cancel any pending changes

        button_exit_with_saving = toga.Button("Exit and Save", 
            on_press=lambda widget: 
                self.settings_submit_button(collection_management_collection_name_input.value, collection_management_server_address_input.value),
            style=Pack(flex=1)
        ) # Cancel any pending changes

        exit_buttons_box = toga.Box(children=[
            button_exit_with_saving,
            button_exit_without_saving
        ], style=Pack(
            direction=ROW,
            flex=1
        ))

        settings_box = toga.Box(children=[
            settings_and_values_box,
            self.draw_divider(rgb(150, 150, 150)),
            exit_buttons_box
        ], style=Pack(
            direction=COLUMN,
            flex=1
        ))

        self.main_box.add(settings_box)

    # Reads the collection from the local device and returns the contents as a dictionary
    def get_collection(self, collection_name):
        try:
            with open("{save_path}/{collection_name}.json".format(save_path=save_path, collection_name=collection_name), 'r+') as file:
                local_collection = file.read()
                return json.loads(local_collection)
        except FileNotFoundError as e:
            print("Error: {error}".format(error=e))
            self.create_new_collection(collection_name)
            self.main_window.info_dialog("Alert", "'{collection_name}' not found on local device, so it was created.".format(collection_name=collection_name))
            with open("{save_path}/{collection_name}.json".format(save_path=save_path, collection_name=collection_name), 'r+') as file:
                local_collection = file.read()
                return json.loads(local_collection)

    # Creates a new collection from a given collection name
    def create_new_collection(self, collection_name):
        with open("{save_path}/{collection_name}.json".format(save_path=save_path, collection_name=collection_name), 'w') as file:
            file.write(str(json.dumps(collection_skeleton)))

    # Compares the remote and local collections to see which one is more up-to-date. Should use the lastModified value
    def sync_collection(self, remote_server, collection_name):
        try:
            with httpx.Client() as client:
                response = client.get("{remote_server}/tasks/{collection_name}".format(remote_server=remote_server, collection_name=collection_name))
            remote_collection = response.json()
            local_collection = self.get_collection(collection_name)

        except Exception as e:
            self.main_window.info_dialog("Error", "Could not connect to the remote server. Please double-check your collection settings, as well as server connectivity.\n\n{error}".format(error=e))

        # If the local collection is newer than the remote collection, update the remote collection with a POST request
        if (local_collection["lastModified"] > remote_collection["lastModified"]):
            self.main_window.info_dialog("Alert", "Local collection is newer than the remote collection. Updating remote collection.")
            try:
                with httpx.Client() as client:
                    response = client.put(
                        "{remote_server}/tasks/{collection_name}".format(remote_server=remote_server, collection_name=collection_name), 
                        json=local_collection,
                        headers={
                            "Content-Type": "application/json",
                            #"Authorization": "Basic {basic_auth}".format(basic_auth=basic_auth)
                        }
                        )
                self.main_window.info_dialog("Success", "Remote collection has been successfully updated!\n\n{response}".format(response=response))
            except Exception as e:
                self.main_window.info_dialog("Error", "Could not update the remote collection.\n\n{error}".format(error=e))
                
        # If the remote collection is newer than the local collection, save it to local storage
        elif (local_collection["lastModified"] < remote_collection["lastModified"]):
            self.main_window.info_dialog("Alert", "Remote collection is newer than the local collection. Updating local collection.")
            self.save_data(remote_collection, collection_name)
            self.clear_all_views()
            self.draw_main_view()

        # If both collections are the same
        elif (local_collection["lastModified"] == remote_collection["lastModified"]):
            self.main_window.info_dialog("Alert", "Both local and remote collections are already synced.")

    def draw_item_selection(self):
        self.clear_all_views()

        title = toga.Label("Select New Item Type", style=Pack(font_size=26))

        button_box = toga.Box(children=[
        toga.Button("Feed", 
            on_press=lambda widget: self.draw_add_item("Feed")
            ),
        toga.Button("Task",
            on_press=lambda widget: self.draw_add_item("Task")
            )
        ], style=Pack(
            direction=COLUMN, flex=1
            ))

        item_selection_box = toga.Box(children=[
            title,
            button_box
        ], style=Pack(
            direction=COLUMN,
            flex=1
        ))

        self.main_box.add(item_selection_box)

    def draw_add_item(self, feed_or_task):
        self.clear_all_views()

        add_item_title = toga.Label("Create a new {item}".format(item=feed_or_task), style=Pack(font_size=26))

        # Parent box
        add_item_attributes_box = toga.Box(children=[], style=Pack(
            direction=COLUMN,
            flex=0
        ))

        # Title
        title_input = toga.TextInput(value="", style=Pack(flex=1))
        title_box = toga.Box(children=[
            toga.Label("Title", style=Pack(font_size=16, padding=(5, 0, 0, 0))),
            title_input
        ], style=Pack(
            direction=ROW,
            padding=(0, 0, 0, 5),
            flex=1
        ))
        add_item_attributes_box.add(title_box)

        # Category
        category_input = toga.TextInput(value="", style=Pack(flex=1))
        category_box = toga.Box(children=[
            toga.Label("Category", style=Pack(font_size=16, padding=(5, 0, 0, 0))),
            category_input
        ], style=Pack(
            direction=ROW,
            padding=(0, 0, 0, 5),
            flex=1
        ))
        add_item_attributes_box.add(category_box)

        # Draw feed or task attributes depending on button pressed in draw_item_selection view
        match feed_or_task:
            case "Feed":
                # URL
                url_input = toga.TextInput(value="", style=Pack(flex=1))
                url_box = toga.Box(children=[
                    toga.Label("URL", style=Pack(font_size=16, padding=(5, 0, 0, 0))),
                    url_input
                ], style=Pack(
                    direction=ROW,
                    padding=(0, 0, 0, 5),
                    flex=1
                ))
                add_item_attributes_box.add(url_box)

                # Update Mechanism
                update_mechanism_select = toga.Selection(items=[
                    "Web Page Checksum", 
                    "Last-Modified HTTP Header", 
                    "document.lastModified JS Function", 
                    "HTML Element Regex"
                    ], style=Pack(
                        flex=1
                    ))
                update_mechanism_box = toga.Box(children=[
                    toga.Label("Update Method", style=Pack(font_size=16, padding=(5, 0, 0, 0))),
                    update_mechanism_select
                ], style=Pack(
                    direction=ROW,
                    padding=(0, 0, 0, 5),
                    flex=1
                ))
                add_item_attributes_box.add(update_mechanism_box)

                match update_mechanism_select.value:
                    case "Web Page Checksum":
                        update_mechanism = "checksum"
                    case "Last-Modified HTTP Header":
                        update_mechanism = "lastModifiedHttpHeader"
                    case "document.lastModified JS Function":
                        update_mechanism = "documentLastModifiedJs"
                    case "HTML Element Regex":
                        update_mechanism = "htmlRegex"

                feed_or_task_dict = {
                    "id": 3,
                    "title": title_input.value,
                    "category": category_input.value,
                    "url": url_input.value,
                    "dateLastUpdated": int(time.time()),
                    "isUserUpToDate": true,
                    str(update_mechanism): ""
                }

            case "Task":
                # Description
                description_input = toga.TextInput(value="", style=Pack(flex=1))
                description_box = toga.Box(children=[
                    toga.Label("Description", style=Pack(font_size=16, padding=(5, 0, 0, 0))),
                    description_input
                ], style=Pack(
                    direction=ROW,
                    padding=(0, 0, 0, 5),
                    flex=1
                ))
                add_item_attributes_box.add(description_box)

                # Description
                location_input = toga.TextInput(value="", style=Pack(flex=1))
                location_box = toga.Box(children=[
                    toga.Label("Location", style=Pack(font_size=16, padding=(5, 0, 0, 0))),
                    location_input
                ], style=Pack(
                    direction=ROW,
                    padding=(0, 0, 0, 5),
                    flex=1
                ))
                add_item_attributes_box.add(location_box)
                
                # Due Date
                due_date_switch = toga.Switch(text="Has a due date?")
                due_date_switch_box = toga.Box(children=[
                    due_date_switch
                ], style=Pack(
                    direction=ROW,
                    padding=(0, 0, 0, 5),
                    flex=1
                ))
                due_date_value = toga.TextInput(value="", style=Pack(flex=1))
                due_date_value_box = toga.Box(children=[
                    toga.Label("Due Date", style=Pack(font_size=16, padding=(5, 0, 0, 0))),
                    due_date_value
                ], style=Pack(
                    direction=ROW,
                    padding=(0, 0, 0, 5),
                    flex=1
                ))
                due_date_box = toga.Box(children=[
                    due_date_switch_box,
                    due_date_value_box
                ], style=Pack(
                    direction=COLUMN,
                    padding=(0, 0, 0, 5),
                    flex=1
                ))
                add_item_attributes_box.add(due_date_box)

                # Recurrence
                recurrence_range_input = toga.TextInput(value="", style=Pack(flex=1))
                recurrence_range_box = toga.Box(children=[
                    toga.Label("Recurrence Range", style=Pack(font_size=16, padding=(5, 0, 0, 0))),
                    recurrence_range_input
                ], style=Pack(
                    direction=ROW,
                    padding=(0, 0, 0, 5),
                    flex=1
                ))
                add_item_attributes_box.add(recurrence_range_box)
                recurrence_interval_input = toga.TextInput(value="", style=Pack(flex=1))
                recurrence_interval_box = toga.Box(children=[
                    toga.Label("Recurrence Interval", style=Pack(font_size=16, padding=(5, 0, 0, 0))),
                    recurrence_interval_input
                ], style=Pack(
                    direction=ROW,
                    padding=(0, 0, 0, 5),
                    flex=1
                ))
                add_item_attributes_box.add(recurrence_interval_box)
                recurrence_end_date_input = toga.TextInput(value="", style=Pack(flex=1))
                recurrence_end_date_box = toga.Box(children=[
                    toga.Label("Recurrence End Date", style=Pack(font_size=16, padding=(5, 0, 0, 0))),
                    recurrence_end_date_input
                ], style=Pack(
                    direction=ROW,
                    padding=(0, 0, 0, 5),
                    flex=1
                ))
                add_item_attributes_box.add(recurrence_end_date_box)

        button_box = toga.Box(children=[
            toga.Button("Submit", 
                on_press=lambda widget: self.edit_submit_button(feed_or_task_select.value, feed["id"], {"id": feed_id, "title": input_new_title.value, "category": feed["category"], "url": feed["url"], "dateLastUpdated": feed["dateLastUpdated"], "isUserUpToDate": feed["isUserUpToDate"], "updateMechanism": feed["updateMechanism"]}, self.get_collection(collection_name)),
                style=Pack(flex=1)
                ),
            toga.Button("Cancel",
                on_press=lambda widget: self.edit_cancel_button(),
                style=Pack(flex=1)
                )
        ], style=Pack(
            direction=ROW, 
            flex=0
            ))

        add_item_parent_box = toga.Box(children=[
            add_item_title,
            add_item_attributes_box,
            button_box
        ], style=Pack(
            direction=COLUMN, 
            flex=1
            ))

        self.main_box.add(add_item_parent_box)

    def startup(self) :
        # Create path to save collection on local device if it doesn't already exist
        Path(save_path).mkdir(parents=True, exist_ok=True)

        # Check if collection exists. If not, the whole thing breaks. Make example collection if one does not exist.
        if (Path("{save_path}/{collection_name}.json".format(save_path=save_path, collection_name=collection_name)).is_file() == False):
            self.create_new_collection("my-first-collection")
            self.main_window.info_dialog("Welcome", "Welcome to StefansHome! No collection was detected, so one was created at: '{path}/{collection_name}.json'".format(path=save_path, collection_name=collection_name))

        settings_button = toga.Command(
            lambda widget: self.draw_settings(collection_name, remote_server),
            text="⚙", 
            tooltip="Open Settings Menu",
            section=0
        )

        refresh_button = toga.Command(
            lambda widget: self.sync_collection(remote_server, collection_name),
            text="Sync", 
            tooltip="Syncs the Collections",
            section=0
        )

        add_item_button = toga.Command(
            lambda widget: self.draw_item_selection(),
            text="Add",
            tooltip="Add a feed or task to the collection",
            section=0
        )

        # Add main view to main window
        self.main_box = toga.Box()
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content =  self.main_box
        self.main_window.toolbar.add(settings_button)
        self.main_window.toolbar.add(refresh_button)
        self.main_window.toolbar.add(add_item_button)
        self.main_window.show()
        self.draw_main_view()

def main():
    return StefansHome()
