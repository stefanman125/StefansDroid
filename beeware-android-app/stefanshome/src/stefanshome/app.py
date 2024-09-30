import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, LEFT, RIGHT
from toga.colors import rgb
import httpx
import time
import textwrap
from pathlib import Path
import json
from datetime import datetime
import xml.etree.ElementTree as ET
import base64

# Hardcoded path that I should probably change, but im okay with the idea of the collections being somewhere in Documents
collection_save_path = "/storage/emulated/0/Documents/StefansHome/collections" # No trailing slash
collection_name = "my-grocery-list" # dont include the file extension
server_address = "http://192.168.0.100:5000"
collection_skeleton = {"lastModified": 0, "tasks": [], "feeds": []}
password = ""
debug_mode = False

# Settings File
settings_save_filepath = "/storage/emulated/0/Documents/StefansHome/preferences.xml"
settings_skeleton_root = ET.Element("settings")

settings_skeleton_collection_management = ET.SubElement(settings_skeleton_root, "collectionManagement")
settings_skeleton_collection_management_collection_name = ET.SubElement(settings_skeleton_collection_management, "collectionName")
settings_skeleton_collection_management_collection_name.text = "my-first-collection"

settings_skeleton_server_management = ET.SubElement(settings_skeleton_root, "serverManagement")
settings_skeleton_server_management_server_address = ET.SubElement(settings_skeleton_server_management, "serverAddress")
settings_skeleton_server_management_server_address.text = "http://your-website.ca"
settings_skeleton_server_management_password = ET.SubElement(settings_skeleton_server_management, "serverPassword")
settings_skeleton_server_management_password.text = ""

settings_skeleton_app_preferences = ET.SubElement(settings_skeleton_root, "appPreferences")
settings_skeleton_app_preferences_startup_sync = ET.SubElement(settings_skeleton_app_preferences, "syncOnStartup")
settings_skeleton_app_preferences_startup_sync.text = "False"
settings_skeleton_app_preferences_debug_mode = ET.SubElement(settings_skeleton_app_preferences, "debugMode")
settings_skeleton_app_preferences_debug_mode.text = "False" 

settings_skeleton = ET.ElementTree(settings_skeleton_root)

class StefansHome(toga.App):
    # Simply clears the screen of all views when switching views
    def clear_all_views(self):
        self.main_box.clear()

    # Handles the "delete" button press in the edit task view
    def remove_item_button(self, taskorfeed, id):
        collection = self.get_collection(collection_name)
        collection[taskorfeed] = [item for item in collection[taskorfeed] if item['id'] != id]
        collection["lastModified"] = int(time.time())
        self.debug_message("Info", "Removed {taskorfeed} with ID {id}".format(taskorfeed=taskorfeed, id=id))
        self.save_data(collection, collection_name)
        self.clear_all_views() 
        self.draw_main_view()

    # Handles the "cancel" button press in the edit task view
    def edit_cancel_button(self):
        self.clear_all_views()
        self.draw_main_view()

    # Handles the "submit" button press in the edit task view 
    def handle_feed_submit(self, taskorfeed, new_id, new_item_dict, collection):
        self.change_item(taskorfeed, new_id, new_item_dict, collection)
        self.clear_all_views() 
        self.draw_main_view()
    
    def handle_task_submit(self, due_date_switch, taskorfeed, new_id, new_item_dict, collection):
        if due_date_switch.value == False:
            new_item_dict["dueDate"] = 0
        self.change_item(taskorfeed, new_id, new_item_dict, collection)
        self.clear_all_views() 
        self.draw_main_view()

    # Returns the index of the task or feed in the collection based on the ID, since they are not ordered by ID (or at least, I don't imagine they will be at the time of writing this)
    def get_index(self, taskorfeed, id, collection):
        for item in collection["{taskorfeed}".format(taskorfeed=taskorfeed)]:
            if item["id"] == id:
                return(collection["{taskorfeed}".format(taskorfeed=taskorfeed)].index(item))

    # This function is responsible for changing task data. Depending on the ID of the changed task, it either changes an existing task, or creates a new one.
    def change_item(self, taskorfeed, id, new_item_dict, collection):
        # If the task/feed does not exist in the collection
        if not any(d["id"] == id for d in collection[taskorfeed]):
            self.debug_message("Info", "Creating new {item}".format(item=taskorfeed))
            collection[taskorfeed].append(new_item_dict)
            self.save_data(collection, collection_name)
        # Otherwise, change the existing one
        else:
            self.debug_message("Info", "Changing old {item}".format(item=taskorfeed))
            collection[taskorfeed][self.get_index(taskorfeed, id, collection)] = new_item_dict 
            self.save_data(collection, collection_name)

    # Saves collection to file being currently used to store collection on the device's storage
    def save_data(self, collection, collection_name):
        collection["lastModified"] = int(time.time())
        print(collection["lastModified"])
        try:
            with open("{collection_save_path}/{collection_name}.json".format(collection_save_path=collection_save_path, collection_name=collection_name), 'w') as file:
                file.write(str(json.dumps(collection)))
            self.debug_message("Success", "Collection Successfully saved to: '{path}/{collection_name}.json'".format(path=collection_save_path, collection_name=collection_name))
        except Exception as e:
            self.debug_message("Error", "Could not save collection to the local device with the following error:\n{error}".format(error=e))
        self.clear_all_views()
        self.draw_main_view()

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
    def draw_feed(self, feed_attributes):
        if (len(feed_attributes["title"]) > 20):
            feed_title = feed_attributes["title"][:20] + ".."
        else:
            feed_title = feed_attributes["title"]

        feed_date_last_updated = "{date} ({tz})".format(date=time.strftime('%Y-%m-%d %I:%M %p', time.localtime(feed_attributes["dateLastUpdated"])), tz=time.tzname[0])

        feed_update_mechanism = list(feed_attributes.items())[-1][0] # Update mechanism doesn't have its own key

        title_date_option_box = toga.Box(children=[
            toga.Label("{feed_title}".format(feed_title=feed_title), style=Pack(font_size=20, color=rgb(0, 0, 0), padding=(2, 0, 2, 5))),
            toga.Label("{feed_date_last_updated}".format(feed_date_last_updated=feed_date_last_updated), style=Pack(font_size=10, color=rgb(61, 61, 61), padding=(2, 0, 2, 9))),
            ], style=Pack(direction=COLUMN))

        category_box = toga.Box(children=[
            toga.Label("{feed_category}".format(feed_category=feed_attributes["category"]), style=Pack(font_size=12, color=rgb(0, 0, 0), padding=(10, 0, 10, self.get_category_padding(feed_title, len(feed_attributes["category"]))), alignment='right', flex=1)),
            toga.Switch(text="Caught up?", value=feed_attributes["isUserUpToDate"], on_change=lambda widget: self.change_switch_state(widget, "feeds", feed_attributes["id"], feed_attributes, self.get_collection(collection_name)), style=Pack(color=rgb(0, 0, 0), padding=(0, 20, 0, 40)))
        ], style=Pack(direction=COLUMN))

        top_half_box = toga.Box(children=[
            title_date_option_box,
            category_box,
        ], style=Pack(
            direction=ROW
        ))

        button_edit = toga.Button("Edit", 
            on_press=lambda widget: 
                self.draw_add_item("feeds", "existing", feed_attributes["id"], feed_attributes)        
        ) 

        button_go_to_url = toga.Button("Go to URL",
            on_press=lambda widget:
                self.open_url_in_browser(feed_attributes["url"])
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

    # Open URL in browser todo
    def open_url_in_browser(self, url):
        print("Copying URL: "+url)
        # Todo using Kivy

    def change_switch_state(self, widget, taskorfeed, id, new_item_dict, collection):
        match taskorfeed:
            case "tasks":
                new_item_dict["completed"] = widget.value
            case "feeds":
                new_item_dict["isUserUpToDate"] = widget.value
        self.change_item(taskorfeed, id, new_item_dict, collection)

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
            elif (task["dueDate"] - current_date_epoch < 0 and task["completed"] == False): # Check if any tasks are overdue
                date_overdue.add(self.draw_task(task))
                date_overdue.add(self.draw_divider(rgb(255, 255, 255)))
                overdue_tasks += 1
            elif (task["dueDate"] - current_date_epoch <= 604800 and task["completed"] == False): # Check if any tasks are due in 7 days
                date_1weeks.add(self.draw_task(task))
                date_1weeks.add(self.draw_divider(rgb(255, 255, 255)))
                if (task["dueDate"] - current_date_epoch <= 86400 and task["completed"] == False): # Check if any tasks are due today
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
    
    # Returns padding values based on the title and category sizes
    def get_category_padding(self, title, category):
        padding_static = 300
        padding_category = category
        padding_title = len(title)*11
        category_dynamic_padding = int(padding_static-padding_category-padding_title)
        return category_dynamic_padding

    # Returns padding values based on the due date and switch text found in the Complete? and Caught Up? Switch texts for task and feed feeds respectively
    def get_switch_padding(self, due_date, switch_text):
        pass

    # Takes task dictionary stored in JSON response
    def draw_task(self, task_attributes):

        # Checks if a due date is set. If not, show no date
        if (task_attributes["dueDate"] == 0):
            task_due_date = "No Due Date"
        else:
            task_due_date = "{date} ({tz})".format(date=time.strftime('%Y-%m-%d %I:%M %p', time.localtime(task_attributes["dueDate"])), tz=time.tzname[0])

        # Checks if the title is too long. If so, truncate it
        if (len(task_attributes["title"]) > 20):
            task_title = task_attributes["title"][:20] + ".."
        else:
            task_title = task_attributes["title"]

        title_date_option_box = toga.Box(children=[
            toga.Label("{task_title}".format(task_title=task_title), style=Pack(font_size=20, color=rgb(0, 0, 0), padding=(2, 0, 2, 5))),
            toga.Label("{task_due_date}".format(task_due_date=task_due_date), style=Pack(font_size=10, color=rgb(61, 61, 61), padding=(2, 0, 2, 9))),
            ], style=Pack(direction=COLUMN))
        
        category_box = toga.Box(children=[
            toga.Label("{task_category}".format(task_category=task_attributes["category"]), style=Pack(font_size=12, color=rgb(0, 0, 0), padding=(10, 0, 10, self.get_category_padding(task_title, len(task_attributes["category"]))), alignment='right', flex=1)),
            toga.Switch(text="Complete?", value=task_attributes["completed"], style=Pack(color=rgb(0, 0, 0), padding=(0, 20, 0, self.get_category_padding(task_title, 30))), on_change=lambda widget: self.change_switch_state(widget, "tasks", task_attributes["id"], task_attributes, self.get_collection(collection_name)))
        ], style=Pack(direction=COLUMN))


        top_half_box = toga.Box(children=[
            title_date_option_box,
            category_box,
        ], style=Pack(
            direction=ROW
        ))

        # Some quick logic that truncates any characters over the 200 character limit, so that it fits in the task view
        if (len(task_attributes["description"]) > 200):
            task_description = task_attributes["description"][:200] + "..."
        else:
            task_description = task_attributes["description"]

        button_edit = toga.Button("Edit", 
            on_press=lambda widget: 
                self.draw_add_item("tasks", "existing", task_attributes["id"], task_attributes)        
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

    def settings_submit_button(self, new_collection_name, new_server_address, new_password, new_sync_on_startup, new_debug_mode):
        global collection_name 
        collection_name = new_collection_name
        global server_address 
        server_address = new_server_address
        global password
        password = new_password
        global sync_on_startup
        sync_on_startup = new_sync_on_startup
        global debug_mode
        debug_mode = new_debug_mode

        self.write_to_settings_file(collection_name, server_address, sync_on_startup, password, debug_mode)

        # Calls the edit cancel button just to reuse the function used to exit the view
        self.edit_cancel_button()

    # Draw the settings menu
    def draw_settings(self, collection_name, server_address, password, sync_on_startup, debug_mode):
        self.clear_all_views()

        # Collection Management section
        collection_management_title = toga.Label("Collection Management", style=Pack(font_size=26, padding=(0, 0, 10, 0)))
        collection_management_collection_name_input = toga.TextInput(value=collection_name)
        collection_management_collection_name = toga.Box(children=[
            toga.Label("Collection Name", style=Pack(font_size=16)),
            collection_management_collection_name_input
        ], style=Pack(
            direction=COLUMN
        ))
        settings_collection_management = toga.Box(children=[
            collection_management_title,
            collection_management_collection_name,
            self.draw_divider(rgb(255, 255, 255))
        ], style=Pack(
            direction=COLUMN
        ))

        # Server Management Section
        server_management_title = toga.Label("Server Management", style=Pack(font_size=26, padding=(0, 0, 10, 0)))

        server_management_server_address_input = toga.TextInput(value=server_address)
        server_management_server_address = toga.Box(children=[
            toga.Label("Collection Server Address", style=Pack(font_size=16)),
            server_management_server_address_input
        ], style=Pack(
            direction=COLUMN
        ))

        server_management_password_input = toga.TextInput(value=password)
        server_management_password = toga.Box(children=[
            toga.Label("Password (blank if none)", style=Pack(font_size=16)),
            server_management_password_input
        ], style=Pack(
            direction=COLUMN
        ))

        settings_server_management = toga.Box(children=[
            server_management_title,
            server_management_server_address,
            self.draw_divider(rgb(255, 255, 255)),
            server_management_password,
            self.draw_divider(rgb(255, 255, 255)),
        ], style=Pack(
            direction=COLUMN
        ))

        # App Preferences
        app_preferences_title = toga.Label("App Preferences", style=Pack(font_size=26, padding=(0, 0, 10, 0)))

        app_preferences_sync_startup_switch = toga.Switch("Sync Collections every time the app is opened", value=sync_on_startup, style=Pack(font_size=12))

        app_preferences_debug_mode_switch = toga.Switch("Debug Mode", value=debug_mode, style=Pack(font_size=12))

        settings_app_preferences = toga.Box(children=[
            app_preferences_title,
            app_preferences_sync_startup_switch,
            self.draw_divider(rgb(255, 255, 255)),
            app_preferences_debug_mode_switch,
            self.draw_divider(rgb(255, 255, 255)),
        ], style=Pack(
            direction=COLUMN
        ))

        # All settings go in this box
        settings = toga.Box(children=[
            settings_collection_management,
            settings_server_management,
            settings_app_preferences
        ], style=Pack(
            direction=COLUMN,
            flex=1
        ))

        settings_and_values_box = toga.ScrollContainer(content=settings, style=Pack(flex=1, padding=(0, 0, 0, 0)))

        button_exit_without_saving = toga.Button("Exit without Saving", 
            on_press=lambda widget: 
                self.edit_cancel_button(),
            style=Pack(flex=1)
        ) # Cancel any pending changes

        button_exit_with_saving = toga.Button("Exit and Save", 
            on_press=lambda widget: 
                self.settings_submit_button(collection_management_collection_name_input.value, server_management_server_address_input.value, server_management_password_input.value, app_preferences_sync_startup_switch.value, app_preferences_debug_mode_switch.value), 
            style=Pack(flex=1)
        ) # Save new settings

        exit_buttons_box = toga.Box(children=[
            button_exit_with_saving,
            button_exit_without_saving
        ], style=Pack(
            direction=ROW
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
            with open("{collection_save_path}/{collection_name}.json".format(collection_save_path=collection_save_path, collection_name=collection_name), 'r+') as file:
                local_collection = file.read()
                return json.loads(local_collection)
        except FileNotFoundError as e:
            self.main_window.info_dialog("Error: {error}".format(error=e))
            self.create_new_collection(collection_name)
            self.main_window.info_dialog("Info", "'{collection_name}' not found on local device, so it was created.".format(collection_name=collection_name))
            with open("{collection_save_path}/{collection_name}.json".format(collection_save_path=collection_save_path, collection_name=collection_name), 'r+') as file:
                local_collection = file.read()
                return json.loads(local_collection)

    # Creates a new collection from a given collection name
    def create_new_collection(self, collection_name):
        with open("{collection_save_path}/{collection_name}.json".format(collection_save_path=collection_save_path, collection_name=collection_name), 'w') as file:
            file.write(str(json.dumps(collection_skeleton)))

    # Compares the remote and local collections to see which one is more up-to-date. Should use the lastModified value
    def sync_collection(self, server_address, collection_name):

        # If password is set, encode it
        global password
        if (password != ""):
            basic_auth = ":"+password
            basic_auth = base64.b64encode(basic_auth.encode('utf-8')).decode('utf-8')

        try:
            with httpx.Client() as client:
                response = client.get("{server_address}/tasks/{collection_name}".format(server_address=server_address, collection_name=collection_name),
                headers={
                    "Authorization":"Basic {basic_auth}".format(basic_auth=basic_auth)
                })
                response.raise_for_status()
            remote_collection = response.json()
            local_collection = self.get_collection(collection_name)

        except httpx.HTTPStatusError as e:
            self.main_window.info_dialog("Error", "Could not connect to the remote server. Please double-check your collection settings, as well as server connectivity.\n\n{error_response}\n\n{error_code}".format(error_response=e.response.text, error_code=e.response))
            return
        except Exception as e:
            self.main_window.info_dialog("Error", "Unknown error.\n\n{error}".format(error=e))
            return

        # If the local collection is newer than the remote collection, update the remote collection with a POST request
        if (local_collection["lastModified"] > remote_collection["lastModified"]):
            self.debug_message("Info", "Local collection is newer than the remote collection. Updating remote collection.")

            try:
                with httpx.Client() as client:
                    response = client.put(
                        "{server_address}/tasks/{collection_name}".format(server_address=server_address, collection_name=collection_name), 
                        json=local_collection,
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": "Basic {basic_auth}".format(basic_auth=basic_auth)
                        }
                        )
                    response.raise_for_status()
                self.main_window.info_dialog("Alert", "Remote collection has been successfully updated!\n\n{response}".format(response=response))
            except httpx.HTTPStatusError as e:
                self.main_window.info_dialog("Error", "Network error when trying to update the remote collection.\n\n{error}".format(error=e))
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
            on_press=lambda widget: self.draw_add_item("feeds", "new", 0, { "id": 0, "title": "", "category": "", "url": "", "dateLastUpdated": 0, "isUserUpToDate": True, "checksum": "" })
            ),
        toga.Button("Task",
            on_press=lambda widget: self.draw_add_item("tasks", "new", 0, { "id": 0, "title": "", "description": "", "location": "", "category": "", "dueDate": 0, "recurrence": { "recurrenceRange": "None", "interval": 0, "endDate": 0}, "completed": False })
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

    # Gets a new id by iterating through all the existing tasks/feeds, and then returning one higher
    def get_new_id(self, feed_or_task):
        largest_id = 0
        for item in (self.get_collection(collection_name)[feed_or_task]):
            if (item["id"] > largest_id):
                largest_id = item["id"]
        largest_id += 1
        return largest_id

    # Assumes new item is being added
    def draw_add_item(self, feed_or_task, mode, item_id, item_dict):
        self.clear_all_views()

        if feed_or_task == "tasks":
            if item_dict["dueDate"] == 0:
                item_dict["dueDate"] = int(time.time())
                due_date_used = False
            else:
                due_date_used = True
            item_dict["dueDate"] = datetime.fromtimestamp(item_dict["dueDate"])

        if mode == "new":
            item_id = self.get_new_id(feed_or_task)
            add_item_title_text = "Create a new {feed_or_task}".format(feed_or_task=feed_or_task[:-1].capitalize())
        elif mode == "existing":
            item_id = item_dict["id"]
            add_item_title_text = "Edit an existing {feed_or_task}".format(feed_or_task=feed_or_task[:-1].capitalize())

        add_item_title = toga.Label("{add_item_title_text}".format(add_item_title_text=add_item_title_text), style=Pack(font_size=26))

        # Parent box
        add_item_attributes_box = toga.Box(children=[], style=Pack(
            direction=COLUMN,
            flex=0
        ))

        # Title
        title_input = toga.TextInput(value=item_dict["title"], style=Pack(flex=1))
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
        category_input = toga.TextInput(value=item_dict["category"], style=Pack(flex=1))
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
            case "feeds":
                # URL
                url_input = toga.TextInput(value=item_dict["url"], style=Pack(flex=1))
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
                    { "type": "Web Page Checksum", "value": "checksum" }, 
                    { "type": "Last-Modified HTTP Header", "value": "lastModifiedHttpHeader" }, 
                    { "type": "document.lastModified JS Function", "value": "documentLastModifiedJs" }, 
                    { "type": "HTML Element Regex", "value": "htmlRegex" }
                    ], accessor="type", style=Pack(
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

                # Submit button with function for adding a new feed
                submit_button = toga.Button("Submit", 
                on_press=lambda widget: self.handle_feed_submit(feed_or_task, item_id, {"id": item_id, "title": title_input.value, "category": category_input.value, "url": url_input.value, "dateLastUpdated": int(time.time()), "isUserUpToDate": True, str(update_mechanism_select.value.value): ""}, self.get_collection(collection_name)),
                style=Pack(flex=1)
                )

            case "tasks":
                # Description
                description_input = toga.MultilineTextInput(value=item_dict["description"], style=Pack(flex=1, height=250))
                description_box = toga.Box(children=[
                    toga.Label("Description", style=Pack(font_size=16, padding=(5, 0, 0, 0))),
                    description_input
                ], style=Pack(
                    direction=COLUMN,
                    padding=(0, 0, 0, 5),
                    flex=1
                ))
                add_item_attributes_box.add(description_box)

                # Location
                location_input = toga.TextInput(value=item_dict["location"], style=Pack(flex=1))
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
                due_date_switch = toga.Switch("Has a due date?", value=due_date_used)

                due_date_input = toga.DateInput(value=item_dict["dueDate"], style=Pack(flex=1))
                due_date_input_box = toga.Box(children=[
                    toga.Label("Due Date", style=Pack(font_size=16, padding=(5, 0, 0, 0))),
                    due_date_input
                ], style=Pack(
                    direction=ROW,
                    padding=(0, 0, 0, 5),
                    flex=1
                ))
                due_date_box = toga.Box(children=[
                    due_date_switch,
                    due_date_input_box
                ], style=Pack(
                    direction=COLUMN,
                    padding=(0, 0, 0, 5),
                    flex=1
                ))
                add_item_attributes_box.add(due_date_box)

                # Recurrence
                recurrence_range_input = toga.TextInput(value=item_dict["recurrence"]["recurrenceRange"], style=Pack(flex=1))
                recurrence_range_box = toga.Box(children=[
                    toga.Label("Recurrence Range", style=Pack(font_size=16, padding=(5, 0, 0, 0))),
                    recurrence_range_input
                ], style=Pack(
                    direction=ROW,
                    padding=(0, 0, 0, 5),
                    flex=1
                ))
                add_item_attributes_box.add(recurrence_range_box)
                recurrence_interval_input = toga.TextInput(value=item_dict["recurrence"]["interval"], style=Pack(flex=1))
                recurrence_interval_box = toga.Box(children=[
                    toga.Label("Recurrence Interval", style=Pack(font_size=16, padding=(5, 0, 0, 0))),
                    recurrence_interval_input
                ], style=Pack(
                    direction=ROW,
                    padding=(0, 0, 0, 5),
                    flex=1
                ))
                add_item_attributes_box.add(recurrence_interval_box)
                recurrence_end_date_input = toga.TextInput(value=item_dict["recurrence"]["endDate"], style=Pack(flex=1))
                recurrence_end_date_box = toga.Box(children=[
                    toga.Label("Recurrence End Date", style=Pack(font_size=16, padding=(5, 0, 0, 0))),
                    recurrence_end_date_input
                ], style=Pack(
                    direction=ROW,
                    padding=(0, 0, 0, 5),
                    flex=1
                ))
                add_item_attributes_box.add(recurrence_end_date_box)

                # Submit button with function for adding a new task
                submit_button = toga.Button("Submit", 
                on_press=lambda widget: self.handle_task_submit(due_date_switch, feed_or_task, item_id, {"id": item_id, "title": title_input.value, "description": description_input.value, "location": location_input.value, "category": category_input.value, "dueDate": int(datetime.strptime(str(due_date_input.value), "%Y-%m-%d").timestamp()), "recurrence": {"recurrenceRange": "None", "interval": 0, "endDate": 0}, "completed": False }, self.get_collection(collection_name)),
                style=Pack(flex=1)
                )

        button_box = toga.Box(children=[
            submit_button,
            toga.Button("Cancel",
                on_press=lambda widget: self.edit_cancel_button(),
                style=Pack(flex=1)
                )
        ], style=Pack(
            direction=ROW, 
            flex=0
            ))

        if mode == "existing":
            # Button remove removes the item
            button_remove = toga.Button("Delete",
                on_press=lambda widget:
                    self.remove_item_button(feed_or_task, item_id),
                style=Pack(
                    background_color=rgb(255, 0, 0)
                )
            )
            button_box.add(button_remove)

        add_item_parent_box = toga.Box(children=[
            add_item_title,
            add_item_attributes_box,
            button_box
        ], style=Pack(
            direction=COLUMN, 
            flex=1
            ))

        self.main_box.add(add_item_parent_box)

    def xml_to_dict(self, element):
        # Create a dictionary to hold the values
        result = {}
        for child in element:
            # If the child has sub-elements, recurse into the child
            if len(child) > 0:
                result[child.tag] = self.xml_to_dict(child)
            else:
                # If it's a leaf node, store its text value
                result[child.tag] = child.text
        return result

    def write_to_settings_file(self, collection_name, server_address, sync_on_startup, password, debug_mode):
        settings_root = ET.Element("settings")
        settings_collection_management = ET.SubElement(settings_root, "collectionManagement")
        settings_collection_management_collection_name = ET.SubElement(settings_collection_management, "collectionName")
        settings_collection_management_collection_name.text = collection_name
        settings_server_management = ET.SubElement(settings_root, "serverManagement")
        settings_server_management_server_address = ET.SubElement(settings_server_management, "serverAddress")
        settings_server_management_server_address.text = server_address
        settings_server_management_password = ET.SubElement(settings_server_management, "serverPassword")
        settings_server_management_password.text = password
        settings_app_preferences = ET.SubElement(settings_root, "appPreferences")
        settings_app_preferences_startup_sync = ET.SubElement(settings_app_preferences, "syncOnStartup")
        settings_app_preferences_startup_sync.text = str(sync_on_startup)
        settings_app_preferences_debug_mode = ET.SubElement(settings_app_preferences, "debugMode")
        settings_app_preferences_debug_mode.text = str(debug_mode)
        settings = ET.ElementTree(settings_root)
        with open(settings_save_filepath, 'wb') as f:
            settings.write(f, encoding="utf-8", xml_declaration=True)
        self.debug_message("Info", "New settings written to file")

    # Mainly used for converting the start_auto_sync setting variable
    def convert_to_bool(self, var):
        return var.upper() == "TRUE"

    def debug_message(self, title, message):
        if debug_mode: self.main_window.info_dialog(title, message)

    def startup(self):

        # Initialize main window
        self.main_box = toga.Box()
        self.main_window = toga.MainWindow(title=self.formal_name)

        # Create path to save collection on local device if it doesn't already exist
        Path(collection_save_path).mkdir(parents=True, exist_ok=True)

        # Check if the settings file exists
        if not Path(settings_save_filepath).is_file(): 
            self.main_window.info_dialog("Info", "No settings file found. Creating one at: {path}".format(path=settings_save_filepath))
            settings_skeleton.write(settings_save_filepath, encoding="utf-8", xml_declaration=True)

        settings = ET.parse(settings_save_filepath)
        settings_dict = self.xml_to_dict(settings.getroot())
        global collection_name
        collection_name = settings_dict["collectionManagement"]["collectionName"]
        global server_address 
        server_address = settings_dict["serverManagement"]["serverAddress"]
        global password
        password = settings_dict["serverManagement"]["serverPassword"]
        global sync_on_startup
        sync_on_startup = self.convert_to_bool(settings_dict["appPreferences"]["syncOnStartup"])
        global debug_mode
        debug_mode = self.convert_to_bool(settings_dict["appPreferences"]["debugMode"])

        # Check if collection exists. If not, the whole app breaks. Make example collection if one does not exist.
        if (Path("{collection_save_path}/{collection_name}.json".format(collection_save_path=collection_save_path, collection_name=collection_name)).is_file() == False):
            self.create_new_collection("my-first-collection")
            self.main_window.info_dialog("Welcome", "Welcome to StefansHome! No collection was detected, so one was created at: '{path}/{collection_name}.json'".format(path=collection_save_path, collection_name=collection_name))

        settings_button = toga.Command(
            lambda widget: self.draw_settings(collection_name, server_address, password, sync_on_startup, debug_mode),
            text="⚙", 
            tooltip="Open Settings Menu",
            section=0
        )

        refresh_button = toga.Command(
            lambda widget: self.sync_collection(server_address, collection_name),
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
        self.main_window.content =  self.main_box
        self.main_window.toolbar.add(settings_button)
        self.main_window.toolbar.add(refresh_button)
        self.main_window.toolbar.add(add_item_button)
        self.main_window.show()

        # Syncs the collections on startup if the setting is enabled
        if sync_on_startup: self.sync_collection(server_address, collection_name)
        
        # Home Screen of the app
        self.draw_main_view()

def main():
    return StefansHome()
