import os
import json
from dataclasses import dataclass, replace
from typing import List, Dict, Optional
from datetime import datetime
import tkinter as tk
import tkinter.messagebox as messagebox
from typing import Tuple

def my_sorted(iterable, key=None):
    def bubble_sort(arr, n, i=0):
        if n == 1:
            return arr
        if i == n - 1:
            return bubble_sort(arr, n - 1)  # Reduce the problem size
        # Swap if needed
        if (key(arr[i]) if key else arr[i]) > (key(arr[i + 1]) if key else arr[i + 1]):
            arr[i], arr[i + 1] = arr[i + 1], arr[i]

        # Recurse to the next element
        return bubble_sort(arr, n, i + 1)
    return bubble_sort(iterable[:], len(iterable))  # Start sorting with a copy of the original list


@dataclass(frozen=True)
class Task:
    task_id: str
    description: str
    due_date: datetime
    priority: int
    status: str = "Pending"


class TaskManager:
    TASKS_FILE = "tasks.json"

    def add_task(tasks: List[Task], description: str, due_date: datetime, priority: int) -> Tuple[List[Task], Optional[Task]]:
        new_task = Task(f"T{len(tasks) + 1}", description, due_date, priority)
        
        # Validate the task
        validation_error = TaskManager.validate_task(new_task)
        if validation_error:
            return tasks, None

        # Add task to the list
        tasks.append(new_task)
        TaskManager.renumber_tasks(tasks)
        TaskManager.save_tasks(tasks)
        
        return tasks, new_task

    def update_task(tasks: List[Task], task_id: str, updates: Dict[str, any]) -> Tuple[List[Task], Optional[Task]]:
        
        def update_recursively(tasks, task_id, updates, index=0, updated_task=None):
            # Base case
            if not tasks:
                return tasks, updated_task

            # Check if the current task matches the task_id
            current_task = tasks[0]
            if current_task.task_id == task_id:
                # Apply the updates if task_id matches
                updated_task = replace(
                    current_task,
                    description=updates.get("description", current_task.description),
                    due_date=updates.get("due_date", current_task.due_date),
                    priority=updates.get("priority", current_task.priority),
                    status=updates.get("status", current_task.status)
                )
                # Update the task in the list
                tasks[0] = updated_task
                return tasks, updated_task  # Return the updated tasks and task
            
            # Recurse on the rest of the list
            updated_tasks, updated_task = update_recursively(tasks[1:], task_id, updates, index + 1, updated_task)
            # Rebuild the list by adding the updated first task back in
            return [tasks[0]] + updated_tasks, updated_task

        # Start the recursion
        updated_tasks, updated_task = update_recursively(tasks, task_id, updates)
        
        TaskManager.save_tasks(updated_tasks)
        return updated_tasks, updated_task

    def delete_task(tasks: List[Task], task_id: str) -> List[Task]:
        
        def delete_recursively(tasks, task_id, result=[]):
            # Base case
            if not tasks:
                TaskManager.renumber_tasks(result)
                TaskManager.save_tasks(result)
                return result

            # Get the first task
            task = tasks[0]

            # If task_id doesn't match, keep the task in the result
            if task.task_id != task_id:
                result.append(task)

            # Recurse with the remaining tasks
            return delete_recursively(tasks[1:], task_id, result)

        # Start the recursion with the full list of tasks
        return delete_recursively(tasks, task_id)

    def filter_tasks(tasks: List[Task], filter_by: str) -> List[Task]:
        
        def filter_recursively(tasks, filter_by, filtered_tasks=[]):
            # Base case
            if not tasks:
                return filtered_tasks

            # Get the first task
            task = tasks[0]

            # Apply the filter criteria
            match filter_by:
                case "Pending":
                    if task.status == "Pending":
                        filtered_tasks.append(task)
                case "Completed":
                    if task.status == "Completed":
                        filtered_tasks.append(task)
                case "Overdue":
                    if task.status == "Overdue":
                        filtered_tasks.append(task)
                case _:
                    filtered_tasks.append(task)  # Return all tasks if no match

            # Recursively process the rest of the tasks
            return filter_recursively(tasks[1:], filter_by, filtered_tasks)

        # Start the recursion with the full list of tasks
        return filter_recursively(tasks, filter_by)

    def sort_tasks(tasks: List[Task], sort_by: str) -> List[Task]:
        match sort_by:
            case "Priority":
                return my_sorted(tasks, key=lambda task: task.priority)
            case "Due Date":
                return my_sorted(tasks, key=lambda task: task.due_date)
            case _:
                return tasks

    def load_tasks() -> List[Task]:
        """Purely functional task loading with error handling using recursion."""
        try:
            if not os.path.exists(TaskManager.TASKS_FILE):
                return []

            with open(TaskManager.TASKS_FILE, 'r') as f:
                task_dicts = json.load(f)
                
                def create_task_from_dict(task_dicts, tasks=[]):
                    # Base case
                    if not task_dicts:
                        return tasks
                    
                    # Process the first task_dict and create a Task
                    task_dict = task_dicts[0]
                    task = Task(
                        task_id=task_dict["task_id"],
                        description=task_dict["description"],
                        due_date=datetime.strptime(task_dict["due_date"], "%Y-%m-%d %H:%M:%S"),
                        priority=task_dict["priority"],
                        status=task_dict["status"]
                    )
                    
                    # Recurse on the remaining task_dicts
                    return create_task_from_dict(task_dicts[1:], tasks + [task])

                # Start recursion with the list of task_dicts
                return create_task_from_dict(task_dicts)

        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            return []

    def save_tasks(tasks: List[Task]) -> None:
        
        def build_task_dicts(tasks, task_dicts=[]):
            # Base case
            if not tasks:
                return task_dicts

            # Extract the first task and create the corresponding dictionary
            task = tasks[0]
            task_dict = {
                "task_id": task.task_id,
                "description": task.description,
                "due_date": task.due_date.strftime("%Y-%m-%d %H:%M:%S"),
                "priority": task.priority,
                "status": task.status
            }

            # Recurse on the remaining tasks, appending the current task's dictionary
            return build_task_dicts(tasks[1:], task_dicts + [task_dict])

        # Start the recursion
        task_dicts = build_task_dicts(tasks)
        
        # Write to the file
        with open(TaskManager.TASKS_FILE, 'w') as f:
            json.dump(task_dicts, f, indent=2)

    def validate_task(task: Task) -> Optional[str]:
        if task.priority < 1 or task.priority > 10:
            return "Priority must be between 1 and 10!"
        
        if task.due_date <= datetime.now():
            return "Due date must be in the future!"
        
        return None

    def renumber_tasks(tasks: List[Task], index: int = 0) -> None:
        if index == len(tasks):  # Base case
            return
        task = replace(tasks[index], task_id=f"T{index + 1}")
        tasks[index] = task  # Update the task in the list
        TaskManager.renumber_tasks(tasks, index + 1)  # Recursively renumber the next task


class TaskPlannerGUI:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Functional Task Planner")
        
        # Tasks storage
        self.tasks = TaskManager.load_tasks()
        
        # Setup UI components
        self.setup_ui()

    def setup_ui(self):
        """Modular UI setup with functional principles."""
        # Create UI components
        self.create_input_fields()
        self.create_task_list()
        self.create_control_buttons()
        self.refresh_task_list()

    def create_input_fields(self):
        """Functional approach to creating input fields."""
        fields = [
            ("Task Description:", "description"),
            ("Due Date (YYYY-MM-DD):", "due_date"),
            ("Priority:", "priority")
        ]
        
        self.entries = {}
        for row, (label_text, key) in enumerate(fields):
            tk.Label(self.root, text=label_text).grid(row=row*2, column=1, sticky="W", padx=10, pady=5)
            entry = tk.Entry(self.root)
            entry.grid(row=row*2+1, column=1, padx=10, pady=5)
            self.entries[key] = entry

    def create_task_list(self):
        """Create task listbox with functional principles."""
        self.task_listbox = tk.Listbox(self.root, width=50)
        self.task_listbox.grid(row=0, column=0, padx=10, pady=10, rowspan=6)

    def create_control_buttons(self):
        """Create control buttons with functional approach."""
        buttons = [
            ("Add Task", self.add_task_handler),
            ("Delete Task", self.delete_task_handler),
            ("Update Task", self.update_task_handler)
        ]
        
        for index, (text, command) in enumerate(buttons):
            btn = tk.Button(self.root, text=text, command=command)
            btn.grid(row=6+index, column=0, padx=10, pady=10)

        # Sort and Filter Dropdowns
        self.create_sort_filter_dropdowns()

    def create_sort_filter_dropdowns(self):
        """Dropdown creation using updated filter_tasks and sort_tasks methods."""
        # Sort options
        sort_options = ["All", "Priority", "Due Date"]

        # Filter options
        filter_options = ["All", "Pending", "Completed", "Overdue"]

        # Sort Dropdown
        sort_var = tk.StringVar(self.root)
        sort_var.set(sort_options[0])  # Default value: "Sort by"
        sort_dropdown = tk.OptionMenu(
            self.root,
            sort_var,
            *sort_options,
            command=lambda selection: self.apply_sort(selection)
        )
        sort_dropdown.grid(row=6, column=1, padx=10, pady=10)

        # Filter Dropdown
        filter_var = tk.StringVar(self.root)
        filter_var.set(filter_options[0])  # Default value: "All"
        filter_dropdown = tk.OptionMenu(
            self.root,
            filter_var,
            *filter_options,
            command=lambda selection: self.apply_filter(selection)
        )
        filter_dropdown.grid(row=7, column=1, padx=10, pady=10)

    def apply_sort(self, sort_by: str):
        """Apply sorting to tasks based on user selection."""
        if sort_by == "All":  # Default or no sorting
            self.tasks = TaskManager.load_tasks()
        else:
            self.tasks = TaskManager.sort_tasks(self.tasks, sort_by)
        self.refresh_task_list()

    def apply_filter(self, filter_by: str):
        """Apply filtering to tasks based on user selection."""
        if filter_by == "All":  # Default or no filtering
            self.tasks = TaskManager.load_tasks()
        else:
            self.tasks = TaskManager.filter_tasks(TaskManager.load_tasks(), filter_by)
        self.refresh_task_list()

    def refresh_task_list(self):
        """Functional task list refresh."""
        self.task_listbox.delete(0, tk.END)
        for task in self.tasks:
            self.task_listbox.insert(
                tk.END, 
                f"{task.task_id} - {task.description} (Due: {task.due_date.strftime('%Y-%m-%d')}, Priority: {task.priority}, Status: {task.status})"
            )

    def add_task_handler(self):
        """Functional task addition handler."""
        try:
            description = self.entries['description'].get()
            due_date = datetime.strptime(self.entries['due_date'].get(), "%Y-%m-%d")
            priority = int(self.entries['priority'].get())
            
            # Functional task addition
            self.tasks, new_task = TaskManager.add_task(self.tasks, description, due_date, priority)
            
            if new_task:
                # Clear input fields
                for entry in self.entries.values():
                    entry.delete(0, tk.END)
                
                self.refresh_task_list()
            else:
                messagebox.showerror("Error", "Invalid task parameters!")
        
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def delete_task_handler(self):
        """Functional task deletion handler."""
        selected = self.task_listbox.curselection()
        if selected:
            task_id = self.tasks[selected[0]].task_id
            self.tasks = TaskManager.delete_task(self.tasks, task_id)
            self.refresh_task_list()

    def update_task_handler(self):
        """Functional task update handler."""
        selected = self.task_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "No task selected!")
            return

        task_id = self.tasks[selected[0]].task_id
        update_window = tk.Toplevel(self.root)
        update_window.title("Update Task")

        # Create update fields dynamically
        update_entries = {}
        update_fields = [
            ("Update Description", "description", str),
            ("Update Due Date (YYYY-MM-DD)", "due_date", lambda x: datetime.strptime(x, "%Y-%m-%d")),
            ("Update Priority", "priority", int)
        ]

        for row, (label_text, key, converter) in enumerate(update_fields):
            tk.Label(update_window, text=label_text).grid(row=row, column=0, sticky="W", padx=10, pady=5)
            entry = tk.Entry(update_window, width=30)
            entry.grid(row=row, column=1, padx=10, pady=5)
            update_entries[key] = (entry, converter)

        # Status dropdown
        status_var = tk.StringVar(update_window)
        status_var.set("Select Status")
        status_dropdown = tk.OptionMenu(update_window, status_var, "Pending", "Completed", "Overdue")
        status_dropdown.grid(row=len(update_fields), column=1, padx=10, pady=5)

        def submit_update():
            updates = {}
            for key, (entry, converter) in update_entries.items():
                value = entry.get().strip()
                if value:
                    try:
                        updates[key] = converter(value)
                    except ValueError:
                        messagebox.showerror("Error", f"Invalid {key} format!")
                        return

            if status_var.get() != "Select Status":
                updates["status"] = status_var.get()

            if not updates:
                messagebox.showerror("Error", "No updates provided!")
                return

            self.tasks, _ = TaskManager.update_task(self.tasks, task_id, updates)
            self.refresh_task_list()
            update_window.destroy()

        tk.Button(update_window, text="Submit Update", command=submit_update).grid(
            row=len(update_fields)+1, column=0, columnspan=2, pady=10
        )

    def run(self):
        """Start the GUI event loop."""
        self.root.mainloop()


def main():
    TaskPlannerGUI().run()

if __name__ == "__main__":
    main()
