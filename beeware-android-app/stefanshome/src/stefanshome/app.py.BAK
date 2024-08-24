"""
An all-in-one application that has all the features that Stefan wants to use daily.
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, LEFT, RIGHT
from toga.colors import rgb
import httpx
import time
import textwrap
import os

class StefansHome(toga.App):
    # Edit view for editing a specific task
    def drawEditTask(self, task_id, task, mode):

        # Old Task attributes
        old_title = task["title"]

        # Used to recycle the view for creating new, and editing old tasks
        if (mode == "edit"):
            mode = "Editing Task"
        elif (mode == "new"):
            mode = "New Task"
        else:
            print("ERROR: drawEditTask not given a proper mode")

        label_title = toga.Label(mode, style=Pack(font_size=28)) # Title
        spacer = toga.Box(style=Pack(background_color=rgb(255, 0, 0), height=75)) # Spacer
        input_new_title = toga.TextInput(value=old_title) # New Task Title input (starts with old task title as the filled input)
        new_title = toga.Box(children=[
            toga.Label("New Title", style=Pack(padding=(8, 0, 0, 0))),
            input_new_title
        ], style=Pack(
            direction=ROW
        ))
        
        button_submit = toga.Button("Submit", on_press=lambda widget: self.changeTask(task["id"], input_new_title.value)) # Submit changes. `lambda widget:` added to prevent the button being automatically pressed on startup, which happened if I didn't have that lambda code there.

        edit_task = toga.Box(children=[
            label_title,
            spacer,
            new_title,
            button_submit
        ],style=Pack(
            background_color=rgb(237, 237, 237),
            padding=(10, 10, 10, 10),
            direction=COLUMN
        ))

        self.main_box.add(edit_task)

    # This function is responsible for changing task data. Depending on the ID of the changed task, it either changes an existing task, or creates a new one.
    def changeTask(self, task_id, task):
        print("Now printing task: "+str(task))
        self.saveData(self.getCollection())

    def saveData(self, collection):
        pass

    def dialogBox(self):
        pass

    # The main view for seeing tasks filtered by date
    def drawOptionBox(self, tasks):
        # Option Box containing date filters
        date_nodate = toga.Box(style=Pack(padding=(5, 5, 5, 5), direction=COLUMN))
        date_today = toga.Box(style=Pack(padding=(5, 5, 5, 5), direction=COLUMN))
        date_1weeks = toga.Box(style=Pack(padding=(5, 5, 5, 5), direction=COLUMN))
        date_4weeks = toga.Box(style=Pack(padding=(5, 5, 5, 5), direction=COLUMN))
        date_overdue = toga.Box(style=Pack(padding=(5, 5, 5, 5), direction=COLUMN))

        divider = toga.Divider(direction="HORIZONTAL", style=Pack(height=2, flex=1, background_color=rgb(255, 255, 255), padding=(10, 0, 0, 10)))

        current_date_epoch = int(time.time())
        overdue_tasks = 0

        for task in tasks:
            if (task["dueDate"] == 0): # Check if any tasks have no due date
                date_nodate.add(self.drawTask(task))
            elif (task["dueDate"] - current_date_epoch < 0): # Check if any tasks are overdue
                date_overdue.add(self.drawTask(task))
                overdue_tasks += 1
            elif (task["dueDate"] - current_date_epoch <= 2592000): # Check if any tasks are due in 30 days
                date_4weeks.add(self.drawTask(task))
                date_4weeks.add(divider)
                if (task["dueDate"] - current_date_epoch <= 604800): # Check if any tasks are due in 7 days
                    date_1weeks.add(self.drawTask(task))
                    if (task["dueDate"] - current_date_epoch <= 86400): # Check if any tasks are due today
                        date_today.add(self.drawTask(task))

        date_box = toga.OptionContainer(content=[], style=Pack(flex=1))
        date_box.content.append(toga.OptionItem("No Due Date", date_nodate))
        date_box.content.append(toga.OptionItem("Today", date_today))
        date_box.content.append(toga.OptionItem("Next 7 Days", date_1weeks))
        date_box.content.append(toga.OptionItem("Next 30 Days", date_4weeks))
        date_box.content.append(toga.OptionItem("Overdue ({num_overdue})".format(num_overdue = overdue_tasks), date_overdue))

        self.main_box.add(date_box)
    
    # Takes task dictionary stored in JSON response
    def drawTask(self, taskAttributes):

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

        title_date_box = toga.Box(children=[
            toga.Label("{task_title}".format(task_title=task_title), style=Pack(font_size=20, color=rgb(0, 0, 0), padding=(2, 0, 2, 5))),
            toga.Label("{task_due_date}".format(task_due_date=task_due_date), style=Pack(font_size=10, color=rgb(61, 61, 61), padding=(2, 0, 2, 9))),
            ], style=Pack(direction=COLUMN))

        category_box = toga.Box(children=[
            toga.Label("{task_category}".format(task_category=taskAttributes["category"]), style=Pack(font_size=12, color=rgb(0, 0, 0), padding=(10, 0, 10, 150-len(taskAttributes["category"])), alignment='right', flex=1)),
            toga.Switch(text="Complete?", value=taskAttributes["completed"], style=Pack(color=rgb(0, 0, 0), padding=(0, 20, 0, 80-len(task_due_date))))
        ], style=Pack(direction=COLUMN))

        top_half_box = toga.Box(children=[
            title_date_box,
            #toga.Box(style=Pack(width=30, background_color=rgb(255, 0, 0))), # Spacer
            category_box,
        ], style=Pack(
            direction=ROW
        ))

        # Some quick logic that truncates any characters over the 200 character limit, so that it fits in the task view
        if (len(taskAttributes["description"]) > 200):
            task_description = taskAttributes["description"][:200] + "..."
        else:
            task_description = taskAttributes["description"]

        task_box = toga.Box(children=[
            top_half_box,
            toga.Divider(direction="HORIZONTAL", style=Pack(height=2, flex=1, background_color=rgb(186, 186, 186), padding=(10, 0, 0, 10))),
            toga.Label("{task_description}".format(task_description=textwrap.fill(task_description, width=60)), style=Pack(font_size=10, color=rgb(0, 0, 0), padding=(5, 0, 0, 10)))
            ], style=Pack(
                direction=COLUMN, 
                padding=0,
                background_color=rgb(212, 212, 212),
                height=200
                )) 

        return(task_box)

    def getCollection(self):
        with httpx.Client() as client:
            response = client.get("http://192.168.0.100:5000/tasks/my-grocery-list")
        collection = response.json()
        return collection

    def startup(self):
        # Call getCollection at the start to get the latest copy of the users current collection
        collection = self.getCollection()

        # Add main box to main window
        self.main_box = toga.Box(style=Pack())
        #self.drawOptionBox(collection["tasks"])
        self.drawEditTask(0, collection["tasks"][0], "edit")
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.main_box
        self.main_window.show()

def main():
    return StefansHome()
