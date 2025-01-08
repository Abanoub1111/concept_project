testawes
import os
import json
from datetime import datetime
import tkinter as tk
import tkinter.messagebox as messagebox

TASKS_FILE = "D:/year 4 term 1/concept/project/functional_programming/tasks.json"

def load_tasks():
    try:
        if not os.path.exists(TASKS_FILE):
            return []
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

def add_task(description, due_date, priority):
    # Load existing tasks
    tasks = load_tasks()
    
    # Create new task
    new_task = {
        "task_id": f"T{len(tasks) + 1}",
        "description": description,
        "due_date": due_date.strftime("%Y-%m-%d %H:%M:%S"),
        "priority": priority,
        "status": "Pending"
    }
    # Validate task
    if validate_task(new_task):
        # Directly modify the JSON file
        tasks.append(new_task)
        save_tasks(tasks)
        return new_task
    return None

def update_task(task_id, updates):
    # Load existing tasks
    tasks = load_tasks()
    
    # Find and update the task
    for task in tasks:
        if task['task_id'] == task_id:
            # Update task fields
            for key, value in updates.items():
                if key == 'due_date':
                    # Convert datetime to string if needed
                    task[key] = value.strftime("%Y-%m-%d %H:%M:%S") if isinstance(value, datetime) else value
                else:
                    task[key] = value
            
            # Directly save changes to JSON
            save_tasks(tasks)
            return task
    
    return None

def delete_task(task_id):
    # Load existing tasks
    tasks = load_tasks()
    
    # Remove the task
    tasks = [task for task in tasks if task['task_id'] != task_id]
    
    # Renumber tasks
    for i, task in enumerate(tasks, 1):
        task['task_id'] = f"T{i}"
    
    # Directly save changes to JSON
    save_tasks(tasks)
    
    return tasks

def filter_tasks(filter_by):
    tasks = load_tasks()
    
    if filter_by == "Pending":
        return [task for task in tasks if task["status"] == "Pending"]
    elif filter_by == "Completed":
        return [task for task in tasks if task["status"] == "Completed"]
    elif filter_by == "Overdue":
        return [task for task in tasks if task["status"] == "Overdue"]
    return tasks

def sort_tasks(sort_by):
    tasks = load_tasks()
    
    if sort_by == "Priority":
        return sorted(tasks, key=lambda task: task["priority"])
    elif sort_by == "Due Date":
        return sorted(tasks, key=lambda task: datetime.strptime(task["due_date"], "%Y-%m-%d %H:%M:%S"))
    return tasks

def validate_task(task):
    # Convert due_date to datetime if it's a string
    if isinstance(task["due_date"], str):
        task["due_date"] = datetime.strptime(task["due_date"], "%Y-%m-%d %H:%M:%S")
    
    # Validate priority
    if task["priority"] < 1 or task["priority"] > 10:
        return False
    
    # Validate due date
    if task["due_date"] <= datetime.now():
        return False
    
    return True


class TaskPlannerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Task Planner")
        
        # Setup UI components
        self.setup_ui()

    def setup_ui(self):
        # Create UI components
        self.create_input_fields()
        self.create_task_list()
        self.create_control_buttons()
        self.refresh_task_list()

    def create_input_fields(self):
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
        self.task_listbox = tk.Listbox(self.root, width=50)
        self.task_listbox.grid(row=0, column=0, padx=10, pady=10, rowspan=6)

    def create_control_buttons(self):
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
        """Dropdown creation for sorting and filtering."""
        # Sort options
        sort_options = ["All", "Priority", "Due Date"]

        # Filter options
        filter_options = ["All", "Pending", "Completed", "Overdue"]

        # Sort Dropdown
        sort_var = tk.StringVar(self.root)
        sort_var.set(sort_options[0])  # Default value
        sort_dropdown = tk.OptionMenu(
            self.root,
            sort_var,
            *sort_options,
            command=lambda selection: self.apply_sort(selection)
        )
        sort_dropdown.grid(row=6, column=1, padx=10, pady=10)

        # Filter Dropdown
        filter_var = tk.StringVar(self.root)
        filter_var.set(filter_options[0])  # Default value
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
            self.refresh_task_list()
        else:
            tasks = sort_tasks(sort_by)
            self.update_task_listbox(tasks)

    def apply_filter(self, filter_by: str):
        """Apply filtering to tasks based on user selection."""
        if filter_by == "All":  # Default or no filtering
            self.refresh_task_list()
        else:
            tasks = filter_tasks(filter_by)
            self.update_task_listbox(tasks)

    def update_task_listbox(self, tasks):
        """Update task listbox with given tasks."""
        self.task_listbox.delete(0, tk.END)
        for task in tasks:
            self.task_listbox.insert(
                tk.END, 
                f"{task['task_id']} - {task['description']} (Due: {task['due_date']}, Priority: {task['priority']}, Status: {task['status']})"
            )

    def refresh_task_list(self):
        """Refresh task list from JSON file."""
        tasks = load_tasks()
        self.update_task_listbox(tasks)

    def add_task_handler(self):
        try:
            description = self.entries['description'].get()
            due_date = datetime.strptime(self.entries['due_date'].get(), "%Y-%m-%d")
            priority = int(self.entries['priority'].get())
            
            new_task = add_task(description, due_date, priority)
            if new_task:
                # Clear input fields
                for entry in self.entries.values():
                    entry.delete(0, tk.END)
                
                # Refresh task list
                self.refresh_task_list()
            else:
                messagebox.showerror("Error", "Invalid task parameters!")
        
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def delete_task_handler(self):
        selected = self.task_listbox.curselection()
        if selected:
            tasks = load_tasks()
            task_id = tasks[selected[0]]['task_id']
            delete_task(task_id)
            self.refresh_task_list()

    def update_task_handler(self):
        selected = self.task_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "No task selected!")
            return

        tasks = load_tasks()
        task_id = tasks[selected[0]]['task_id']
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

            update_task(task_id, updates)
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
