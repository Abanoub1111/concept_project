import os
import json
from datetime import datetime

TASKS_FILE = "D:/year 4 term 1/concept/project/functional_programming/tasks.json"

def my_sorted(iterable, key=None):
    for i in range(len(iterable)):
        for j in range(len(iterable) - i - 1):
            if (key(iterable[j]) if key else iterable[j]) > (key(iterable[j + 1]) if key else iterable[j + 1]):
                iterable[j], iterable[j + 1] = iterable[j + 1], iterable[j]
    return iterable

def load_tasks():
    try:
        if not os.path.exists(TASKS_FILE):
            return []
        with open(TASKS_FILE, 'r') as f:
            task_dicts = json.load(f)
            tasks = []
            for task_dict in task_dicts:
                task = {
                    "task_id": task_dict["task_id"],
                    "description": task_dict["description"],
                    "due_date": datetime.strptime(task_dict["due_date"], "%Y-%m-%d %H:%M:%S"),
                    "priority": task_dict["priority"],
                    "status": task_dict["status"]
                }
                tasks.append(task)
            return tasks
    except (json.JSONDecodeError, KeyError, FileNotFoundError):
        return []

def save_tasks(tasks):
    task_dicts = []
    for task in tasks:
        task_dict = {
            "task_id": task["task_id"],
            "description": task["description"],
            "due_date": task["due_date"].strftime("%Y-%m-%d %H:%M:%S"),
            "priority": task["priority"],
            "status": task["status"]
        }
        task_dicts.append(task_dict)
    with open(TASKS_FILE, 'w') as f:
        json.dump(task_dicts, f, indent=2)

def add_task(tasks, description, due_date, priority):
    new_task = {
        "task_id": f"T{len(tasks) + 1}",
        "description": description,
        "due_date": due_date,
        "priority": priority,
        "status": "Pending"
    }
    validation_error = validate_task(new_task)
    if validation_error:
        return tasks, None
    tasks.append(new_task)
    renumber_tasks(tasks)
    save_tasks(tasks)
    return tasks, new_task

def update_task(tasks, task_id, updates):
    for i, task in enumerate(tasks):
        if task["task_id"] == task_id:
            updated_task = {**task, **updates}
            tasks[i] = updated_task
            save_tasks(tasks)
            return tasks, updated_task
    return tasks, None

def delete_task(tasks, task_id):
    tasks = [task for task in tasks if task["task_id"] != task_id]
    renumber_tasks(tasks)
    save_tasks(tasks)
    return tasks

def filter_tasks(tasks, filter_by):
    if filter_by == "Pending":
        return [task for task in tasks if task["status"] == "Pending"]
    elif filter_by == "Completed":
        return [task for task in tasks if task["status"] == "Completed"]
    elif filter_by == "Overdue":
        return [task for task in tasks if task["status"] == "Overdue"]
    return tasks

def sort_tasks(tasks, sort_by):
    if sort_by == "Priority":
        return my_sorted(tasks, key=lambda task: task["priority"])
    elif sort_by == "Due Date":
        return my_sorted(tasks, key=lambda task: task["due_date"])
    return tasks

def validate_task(task):
    if task["priority"] < 1 or task["priority"] > 10:
        return "Priority must be between 1 and 10!"
    if task["due_date"] <= datetime.now():
        return "Due date must be in the future!"
    return None

def renumber_tasks(tasks):
    for i, task in enumerate(tasks):
        task["task_id"] = f"T{i + 1}"

def display_tasks(tasks):
    if not tasks:
        print("No tasks found.")
        return
    for task in tasks:
        print(f"{task['task_id']} - {task['description']} (Due: {task['due_date'].strftime('%Y-%m-%d')}, Priority: {task['priority']}, Status: {task['status']})")

def prompt_user_for_task():
    description = input("Enter task description: ")
    due_date_str = input("Enter due date (YYYY-MM-DD): ")
    priority = int(input("Enter priority (1-10): "))
    due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
    return description, due_date, priority

def main():
    tasks = load_tasks()

    while True:
        print("\nTask Planner")
        print("1. Add Task")
        print("2. Update Task")
        print("3. Delete Task")
        print("4. Display All Tasks")
        print("5. Filter Tasks")
        print("6. Sort Tasks")
        print("7. Exit")
        
        choice = input("Choose an option: ")
        
        if choice == '1':  # Add Task
            description, due_date, priority = prompt_user_for_task()
            tasks, new_task = add_task(tasks, description, due_date, priority)
            if new_task:
                print("Task added successfully!")
            else:
                print("Error: Invalid task parameters!")
        
        elif choice == '2':  # Update Task
            display_tasks(tasks)
            task_id = input("Enter task ID to update: ")
            description, due_date, priority = prompt_user_for_task()
            updates = {"description": description, "due_date": due_date, "priority": priority}
            tasks, updated_task = update_task(tasks, task_id, updates)
            if updated_task:
                print("Task updated successfully!")
            else:
                print("Error: Task not found!")
        
        elif choice == '3':  # Delete Task
            display_tasks(tasks)
            task_id = input("Enter task ID to delete: ")
            tasks = delete_task(tasks, task_id)
            print("Task deleted successfully!")
        
        elif choice == '4':  # Display All Tasks
            display_tasks(tasks)
        
        elif choice == '5':  # Filter Tasks
            filter_by = input("Enter filter (All, Pending, Completed, Overdue): ")
            tasks = filter_tasks(tasks, filter_by)
            display_tasks(tasks)
        
        elif choice == '6':  # Sort Tasks
            sort_by = input("Enter sort criteria (All, Priority, Due Date): ")
            tasks = sort_tasks(tasks, sort_by)
            display_tasks(tasks)
        
        elif choice == '7':  # Exit
            save_tasks(tasks)
            print("Goodbye!")
            break    # Save tasks back to file

if __name__ == "__main__":
    main()
