"""
Task Tracker version 1.0
8/10/2020
Kivy app that displays a list of tasks in GUI form.
User can add new tasks, change task sorting, and mark tasks as completed/uncompleted.
"""

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.properties import ListProperty
from kivy.properties import NumericProperty
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.uix.button import Button
from version1.patch0.task import Task
from version1.patch0.taskcollection import TaskCollection

SPINNER_SELECTIONS_TO_ATTRIBUTES = {"Completed": "is_completed",
                                    "Priority": "priority",
                                    "Subject": "subject",
                                    "Name": "name"}
STARTING_SPINNER_SELECTION_INDEX = 0
TASKS_FILE_NAME = "tasks.csv"
COMPLETED_COLOR = (.4, .4, .4, 1)
UNCOMPLETED_COLOR = (.2, .4, .6, 1)


class SpinnerOption(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = .6, .2, .4, 1


class TaskTrackerApp(App):
    """App that interacts with GUI and utilises Task and TaskCollection classes."""

    tasks_to_complete_text = StringProperty()
    info_panel_text = StringProperty()
    spinner_selections = ListProperty()
    current_spinner_selection = StringProperty()
    number_of_buttons = NumericProperty()
    tasks_box_height = NumericProperty()
    spinner_options = ObjectProperty(SpinnerOption)

    def __init__(self, **kwargs):
        """Initialize TravelTrackerApp class, load tasks into task_collection from tasks.csv."""
        super().__init__(**kwargs)
        self.task_collection = TaskCollection()
        self.task_collection.load_tasks(TASKS_FILE_NAME)
        self.buttons = []

    def build(self):
        """Construct the GUI, setting string and list properties to starting values."""
        self.title = "TaskTracker 1.0"
        self.icon = "icon.png"
        self.root = Builder.load_file("app.kv")
        Window.size = (800, 600)
        self.info_panel_text = "Welcome to Task Tracker 1.0"
        self.tasks_to_complete_text = "Tasks to complete: {}".format(self.task_collection.get_num_of_uncompleted_tasks())
        # Default starting spinner selection must always be the same, so keys are sorted
        self.spinner_selections = sorted(SPINNER_SELECTIONS_TO_ATTRIBUTES.keys())
        self.current_spinner_selection = self.spinner_selections[STARTING_SPINNER_SELECTION_INDEX]
        self.refresh_buttons()
        return self.root

    def on_stop(self):
        """Save tasks to tasks.csv when program ends."""
        self.task_collection.save_tasks(TASKS_FILE_NAME)

    def mark_completed_or_uncompleted(self, instance):
        """If task is completed, mark it as uncompleted. If task is uncompleted, mark it as completed.
        Refresh buttons, update tasks_to_complete and display info message according to task state
        and importance."""
        # Access button's task object
        task = instance.task
        if task.is_completed:
            task.mark_as_uncompleted()
            message = "You need to complete {}.".format(task.name)
            message += " Get to work!" if task.is_important() else ""
        else:
            task.mark_as_completed()
            message = "You completed {}.".format(task.name)
            message += " Great work!" if task.is_important() else ""

        self.info_panel_text = message
        self.tasks_to_complete_text = "Tasks to complete: {}".format(self.task_collection.get_num_of_uncompleted_tasks())
        self.refresh_buttons()

    def refresh_buttons(self):
        """Remove all buttons, sort tasks, then create task buttons with task text,
        function binding, and background colours depending on whether task has been
        completed or not."""
        self.root.ids.tasks_box.clear_widgets()
        self.number_of_buttons = 0
        # Get sorting attribute from current spinner selection
        sorting_attribute = SPINNER_SELECTIONS_TO_ATTRIBUTES[self.current_spinner_selection]
        self.task_collection.sort_tasks(sorting_attribute)

        for button_number, task in enumerate(self.task_collection.tasks, 1):
            button = Button(
                id="button_{}".format(button_number),
                text=str(task),
                background_color=COMPLETED_COLOR if task.is_completed else UNCOMPLETED_COLOR,
            )
            button.bind(on_release=self.mark_completed_or_uncompleted)
            button.task = task  # store reference to button's task object
            self.root.ids.tasks_box.add_widget(button)
            self.buttons.append(button)
        self.number_of_buttons = len(self.task_collection.tasks)
        self.tasks_box_height = self.number_of_buttons * 50

    def add_task(self):
        """Get task name, subject, and priority, and if they are valid,
        add Task to task_collection and refresh buttons."""
        name = self.root.ids.name_input.text.title()
        subject = self.root.ids.subject_input.text.title()
        priority = self.root.ids.priority_input.text

        if name and subject and priority:
            try:
                priority = int(priority)
                if priority <= 0:
                    self.info_panel_text = "Priority must be > 0"
                else:
                    # task_collection.add_task() returns a confirmation message:
                    confirmation = self.task_collection.add_task(Task(name, subject, priority))
                    self.info_panel_text = confirmation

                    # Utilize variable arguments to clear text of any amount of widgets
                    self.clear_widget_text(
                        self.root.ids.name_input,
                        self.root.ids.subject_input,
                        self.root.ids.priority_input
                    )
                    self.refresh_buttons()
            except ValueError:
                self.info_panel_text = "Please enter a valid number"
        else:
            self.info_panel_text = "All fields must be completed"

    @staticmethod
    def clear_widget_text(*widgets):
        """Clear the text of any number of any number of widgets passed in."""
        for widget in widgets:
            widget.text = ""

    def remove_completed_tasks(self):
        """Remove completed task buttons."""
        if self.task_collection.get_num_of_uncompleted_tasks() < len(self.task_collection.tasks):
            self.info_panel_text = "All completed tasks removed."
        for button in self.buttons:
            if button.task.is_completed:
                self.task_collection.remove_task(button.task)
                self.root.ids.tasks_box.remove_widget(button)


if __name__ == '__main__':
    TaskTrackerApp().run()
