import os
import json
from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime
import tkinter as tk
from functools import partial
import tkinter.messagebox as messagebox

@dataclass
class Task:
    """Represents a task with various attributes."""
    task_id: str
    description: str
    due_date: datetime
    priority: int
    status: str = "Pending"

TASKS_FILE = "tasks.json"

def get_tasks_from_json():
    """Retrieve tasks from the JSON file."""
    if not os.path.exists(TASKS_FILE):
        return []
    
    with open(TASKS_FILE, 'r') as f:
        try:
            task_dicts = json.load(f)
            return [
                Task(
                    task_id=task_dict["task_id"],
                    description=task_dict["description"],
                    due_date=datetime.strptime(task_dict["due_date"], "%Y-%m-%d %H:%M:%S"),
                    priority=task_dict["priority"],
                    status=task_dict["status"]
                )
                for task_dict in task_dicts
            ]
        except (json.JSONDecodeError, KeyError):
            return []

def save_tasks_to_json(tasks: List[Task]):

    """Save tasks to the JSON file."""
    task_dicts = [
        {
            "task_id": task.task_id,
            "description": task.description,
            "due_date": task.due_date.strftime("%Y-%m-%d %H:%M:%S"),
            "priority": task.priority,
            "status": task.status
        }
        for task in tasks
    ]
    
    with open(TASKS_FILE, 'w') as f:
        json.dump(task_dicts, f, indent=2)

def renumber_tasks(tasks: List[Task]):
    """Renumber tasks sequentially starting from T1."""
    for index, task in enumerate(tasks):
        task.task_id = f"T{index + 1}"

def add_task(description: str, due_date: datetime, priority: int) -> Task:
    """Add a new task to the JSON file."""
    
    # Validate the priority
    if priority < 1 or priority > 10:
        raise ValueError("Priority must be between 1 and 10!")

    # Validate the due date is in the future
    if due_date <= datetime.now():
        raise ValueError("Due date must be in the future!")

    # Get existing tasks
    tasks = get_tasks_from_json()
    
    # Generate new task ID
    new_task = Task(f"T{len(tasks) + 1}", description, due_date, priority)

    # Add to existing tasks
    tasks.append(new_task)

    renumber_tasks(tasks)
    
    # Save updated tasks
    save_tasks_to_json(tasks)
    
    return new_task


def update_task(task_id: str, updates: Dict[str, any]) -> Task:
    """Update specific attributes of a task in the JSON file."""
    tasks = get_tasks_from_json()
    updated_task = None

    for task in tasks:
        if task.task_id == task_id:
            # Update only specified attributes
            updated_task = Task(
                task_id=task.task_id,
                description=updates.get("description", task.description),
                due_date=updates.get("due_date", task.due_date),
                priority=updates.get("priority", task.priority),
                status=updates.get("status", task.status)
            )
            tasks[tasks.index(task)] = updated_task
            break

    save_tasks_to_json(tasks)
    return updated_task


def delete_task(task_id: str):
    """Delete a task from the JSON file."""
    # Get existing tasks
    tasks = get_tasks_from_json()
    
    # Remove the task
    updated_tasks = [task for task in tasks if task.task_id != task_id]

    renumber_tasks(updated_tasks)

    # Save updated tasks
    save_tasks_to_json(updated_tasks)

def run_task_planner_gui():
    root = tk.Tk()
    root.title("Task Planner")

    # Tasks list and listbox setup
    task_description_label = tk.Label(root, text="Task Description:")
    task_description_label.grid(row=0, column=1, padx=10, pady=5, sticky="W")
    task_description_entry = tk.Entry(root)
    task_description_entry.grid(row=1, column=1, padx=10, pady=5)

    task_due_date_label = tk.Label(root, text="Due Date (YYYY-MM-DD):")
    task_due_date_label.grid(row=2, column=1, padx=10, pady=5, sticky="W")
    task_due_date_entry = tk.Entry(root)
    task_due_date_entry.grid(row=3, column=1, padx=10, pady=5)

    task_priority_label = tk.Label(root, text="Priority:")
    task_priority_label.grid(row=4, column=1, padx=10, pady=5, sticky="W")
    task_priority_entry = tk.Entry(root)
    task_priority_entry.grid(row=5, column=1, padx=10, pady=5)

    task_listbox = tk.Listbox(root, width=50)
    task_listbox.grid(row=0, column=0, padx=10, pady=10, rowspan=6)

    def refresh_task_list():
        """Refresh the task listbox from the JSON file."""
        tasks = get_tasks_from_json()
        task_listbox.delete(0, tk.END)
        for task in tasks:
            task_listbox.insert(tk.END, f"{task.task_id} - {task.description} (Due: {task.due_date.strftime('%Y-%m-%d')}, Priority: {task.priority}, Status: {task.status})")
    def add_task_handler():
        try:
            description = task_description_entry.get()

            # Parse the due date
            due_date_str = task_due_date_entry.get()
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d")

            # Parse the priority
            priority_str = task_priority_entry.get()
            priority = int(priority_str)
            
            # Call add_task which now has validation
            add_task(description, due_date, priority)
            
            # Clear input fields after adding the task
            task_description_entry.delete(0, tk.END)
            task_due_date_entry.delete(0, tk.END)
            task_priority_entry.delete(0, tk.END)
            
            # Refresh the task list
            refresh_task_list()
        except ValueError as e:
            # Show an error message if validation fails
            messagebox.showerror("Error", str(e))


    def delete_task_handler():
        selected = task_listbox.curselection()
        if selected:
            tasks = get_tasks_from_json()
            task_id = tasks[selected[0]].task_id
            delete_task(task_id)
            refresh_task_list()

    def update_task_handler():
        """Open a window to update a selected task."""
        selected = task_listbox.curselection()
        if not selected:
            tk.messagebox.showerror("Error", "No task selected!")
            return

        tasks = get_tasks_from_json()
        task_id = tasks[selected[0]].task_id

        # Create a new modal window for updating the task
        update_window = tk.Toplevel(root)
        update_window.title("Update Task")

        # Update fields
        update_description_label = tk.Label(update_window, text="Update Description:")
        update_description_label.grid(row=0, column=0, padx=10, pady=5, sticky="W")
        update_description_entry = tk.Entry(update_window, width=30)
        update_description_entry.grid(row=0, column=1, padx=10, pady=5)

        update_due_date_label = tk.Label(update_window, text="Update Due Date (YYYY-MM-DD):")
        update_due_date_label.grid(row=1, column=0, padx=10, pady=5, sticky="W")
        update_due_date_entry = tk.Entry(update_window, width=30)
        update_due_date_entry.grid(row=1, column=1, padx=10, pady=5)

        update_priority_label = tk.Label(update_window, text="Update Priority:")
        update_priority_label.grid(row=2, column=0, padx=10, pady=5, sticky="W")
        update_priority_entry = tk.Entry(update_window, width=30)
        update_priority_entry.grid(row=2, column=1, padx=10, pady=5)

        update_status_label = tk.Label(update_window, text="Update Status:")
        update_status_label.grid(row=3, column=0, padx=10, pady=5, sticky="W")
        update_status_var = tk.StringVar(update_window)
        update_status_var.set("Select Status")
        update_status_dropdown = tk.OptionMenu(update_window, update_status_var, "Pending", "Completed", "Overdue")
        update_status_dropdown.grid(row=3, column=1, padx=10, pady=5)

        def submit_update():
            updates = {}
            if update_description_entry.get():
                updates["description"] = update_description_entry.get()
            if update_due_date_entry.get():
                try:
                    updates["due_date"] = datetime.strptime(update_due_date_entry.get(), "%Y-%m-%d")
                except ValueError:
                    tk.messagebox.showerror("Error", "Invalid date format!")
                    return
            if update_priority_entry.get():
                try:
                    updates["priority"] = int(update_priority_entry.get())
                except ValueError:
                    tk.messagebox.showerror("Error", "Priority must be an integer!")
                    return
            if update_status_var.get() != "Select Status":
                updates["status"] = update_status_var.get()

            if not updates:
                tk.messagebox.showerror("Error", "No updates provided!")
                return

            update_task(task_id, updates)
            refresh_task_list()
            update_window.destroy()

        submit_button = tk.Button(update_window, text="Submit Update", command=submit_update)
        submit_button.grid(row=4, column=0, columnspan=2, pady=10)

    def filter_tasks_by_status(selected_status: str):
        """Filter tasks based on the selected status using pattern matching."""
        tasks = get_tasks_from_json()

        match selected_status:
            case "All":
                filtered_tasks = tasks
            case "Filter by Pending":
                filtered_tasks = [task for task in tasks if task.status == "Pending"]
            case "Filter by Completed":
                filtered_tasks = [task for task in tasks if task.status == "Completed"]
            case "Filter by Overdue":
                filtered_tasks = [task for task in tasks if task.status == "Overdue"]
            case _:
                filtered_tasks = tasks

        task_listbox.delete(0, tk.END)
        for task in filtered_tasks:
            task_listbox.insert(
                tk.END,
                f"{task.task_id} - {task.description} (Due: {task.due_date.strftime('%Y-%m-%d')}, Priority: {task.priority}, Status: {task.status})"
            )

    def sort_tasks_by_criteria(selected_criteria: str):
        """Sort tasks based on the selected criteria using pattern matching."""
        tasks = get_tasks_from_json()

        match selected_criteria:
            case "All":
                sorted_tasks = tasks
            case "Sort by Priority":
                sorted_tasks = sorted(tasks, key=lambda task: task.priority)
            case "Sort by Due Date":
                sorted_tasks = sorted(tasks, key=lambda task: task.due_date)
            case _:
                sorted_tasks = tasks

        task_listbox.delete(0, tk.END)
        for task in sorted_tasks:
            task_listbox.insert(
                tk.END,
                f"{task.task_id} - {task.description} (Due: {task.due_date.strftime('%Y-%m-%d')}, Priority: {task.priority}, Status: {task.status})"
            )

    def create_task_controls(root, add_task_handler, delete_task_handler, update_task_handler, sort_tasks_by_criteria, filter_tasks_by_status):
        # Add Task Button
        add_button = tk.Button(root, text="Add Task", command=add_task_handler)
        add_button.grid(row=6, column=0, padx=10, pady=10)

        # Delete Task Button
        delete_button = tk.Button(root, text="Delete Task", command=delete_task_handler)
        delete_button.grid(row=7, column=0, padx=10, pady=10)

        # Update Task Button
        update_button = tk.Button(root, text="Update Task", command=update_task_handler)
        update_button.grid(row=8, column=0, padx=10, pady=10)

        # Sort dropdown menu
        sort_var = tk.StringVar(root)
        sort_var.set("Sort by")  # Set initial label (won't change after selection)
        sort_dropdown = tk.OptionMenu(
            root,
            sort_var,
            "ALL", "Sort by Priority", "Sort by Due Date",  # Sorting options
            command=sort_tasks_by_criteria  # Pass the selected criteria to the handler
        )
        sort_var.set("Sort by")
        sort_dropdown.grid(row=6, column=1, padx=10, pady=10)


        # Filter dropdown menu
        filter_var = tk.StringVar(root)
        filter_var.set("Filter by Status")  # Set initial label (won't change after selection)
        filter_dropdown = tk.OptionMenu(
            root,
            filter_var,
            "All", "Filter by Pending", "Filter by Completed", "Filter by Overdue",  # Filtering options
            command=filter_tasks_by_status  # Pass the selected status to the handler
        )
        filter_dropdown.grid(row=7, column=1, padx=10, pady=10)

    # Create task controls on the UI
    create_task_controls(root, add_task_handler, delete_task_handler, update_task_handler, sort_tasks_by_criteria, filter_tasks_by_status)

    # Initial task list
    refresh_task_list()

    root.mainloop()


if __name__ == "__main__":
    run_task_planner_gui()