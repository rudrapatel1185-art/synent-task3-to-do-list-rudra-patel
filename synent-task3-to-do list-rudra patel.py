
"""
To-Do List Manager
A menu-driven CLI task manager with priorities, status tracking, and persistence.
"""

import json
import os
from datetime import datetime

DATA_FILE = "todos.json"


# ─── Data layer ───────────────────────────────────────────────────────────────

def load_tasks():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            print("  ⚠  Could not read saved tasks — starting fresh.")
    return []


def save_tasks(tasks):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(tasks, f, indent=2)
    except IOError as e:
        print(f"  ⚠  Could not save tasks: {e}")


def next_id(tasks):
    return max((t["id"] for t in tasks), default=0) + 1


# ─── Display helpers ──────────────────────────────────────────────────────────

PRIORITY_LABEL = {"1": "🔴 High", "2": "🟡 Medium", "3": "🟢 Low"}
STATUS_LABEL   = {"pending": "⏳ Pending", "done": "✅ Done"}


def print_divider():
    print("  " + "─" * 52)


def print_task_row(t):
    pid    = f"[{t['id']:>3}]"
    status = "✅" if t["status"] == "done" else "⏳"
    pri    = {"1": "🔴", "2": "🟡", "3": "🟢"}.get(t["priority"], "  ")
    title  = t["title"]
    added  = t.get("added", "")
    print(f"  {pid} {status} {pri}  {title:<30}  {added}")


def view_tasks(tasks, filter_status=None):
    filtered = [t for t in tasks if filter_status is None or t["status"] == filter_status]
    if not filtered:
        label = f"{filter_status} " if filter_status else ""
        print(f"\n  No {label}tasks found.")
        return

    print()
    print_divider()
    print(f"  {'ID':>5}  St  Pri  {'Title':<30}  Added")
    print_divider()
    for t in sorted(filtered, key=lambda x: (x["priority"], x["id"])):
        print_task_row(t)
    print_divider()
    total   = len(filtered)
    done    = sum(1 for t in filtered if t["status"] == "done")
    pending = total - done
    print(f"  Total: {total}  |  ✅ Done: {done}  |  ⏳ Pending: {pending}")


# ─── Actions ──────────────────────────────────────────────────────────────────

def add_task(tasks):
    print("\n  ── Add Task ──")
    title = input("  Task title: ").strip()
    if not title:
        print("  ✗ Title cannot be empty.")
        return

    print("  Priority:  1 🔴 High   2 🟡 Medium   3 🟢 Low")
    while True:
        p = input("  Choose (1 / 2 / 3) [default 2]: ").strip() or "2"
        if p in ("1", "2", "3"):
            break
        print("  ✗ Enter 1, 2, or 3.")

    task = {
        "id":       next_id(tasks),
        "title":    title,
        "priority": p,
        "status":   "pending",
        "added":    datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"  ✓ Task #{task['id']} added — \"{title}\"")


def delete_task(tasks):
    if not tasks:
        print("\n  No tasks to delete.")
        return
    view_tasks(tasks)
    raw = input("\n  Enter task ID to delete (or 'q' to cancel): ").strip()
    if raw.lower() == "q":
        return
    try:
        tid = int(raw)
    except ValueError:
        print("  ✗ Invalid ID.")
        return
    match = next((t for t in tasks if t["id"] == tid), None)
    if not match:
        print(f"  ✗ No task with ID {tid}.")
        return
    confirm = input(f"  Delete \"{match['title']}\"? (y / n): ").strip().lower()
    if confirm == "y":
        tasks.remove(match)
        save_tasks(tasks)
        print(f"  ✓ Task #{tid} deleted.")
    else:
        print("  Cancelled.")


def mark_done(tasks):
    pending = [t for t in tasks if t["status"] == "pending"]
    if not pending:
        print("\n  No pending tasks.")
        return
    view_tasks(tasks, filter_status="pending")
    raw = input("\n  Enter task ID to mark as done (or 'q' to cancel): ").strip()
    if raw.lower() == "q":
        return
    try:
        tid = int(raw)
    except ValueError:
        print("  ✗ Invalid ID.")
        return
    match = next((t for t in tasks if t["id"] == tid), None)
    if not match:
        print(f"  ✗ No task with ID {tid}.")
    elif match["status"] == "done":
        print(f"  ⚠  Task #{tid} is already marked done.")
    else:
        match["status"] = "done"
        save_tasks(tasks)
        print(f"  ✓ Task #{tid} marked as done.")


def clear_done(tasks):
    done = [t for t in tasks if t["status"] == "done"]
    if not done:
        print("\n  No completed tasks to clear.")
        return
    confirm = input(f"\n  Remove all {len(done)} completed task(s)? (y / n): ").strip().lower()
    if confirm == "y":
        tasks[:] = [t for t in tasks if t["status"] != "done"]
        save_tasks(tasks)
        print(f"  ✓ {len(done)} completed task(s) removed.")
    else:
        print("  Cancelled.")


# ─── Menu ─────────────────────────────────────────────────────────────────────

MENU = [
    ("1", "View all tasks"),
    ("2", "View pending tasks"),
    ("3", "Add task"),
    ("4", "Mark task as done"),
    ("5", "Delete task"),
    ("6", "Clear completed tasks"),
    ("q", "Quit"),
]


def print_menu():
    print("\n  ╔══════════════════════════════╗")
    print("  ║       To-Do List Manager     ║")
    print("  ╠══════════════════════════════╣")
    for key, label in MENU:
        print(f"  ║  [{key}] {label:<26}║")
    print("  ╚══════════════════════════════╝")


def main():
    tasks = load_tasks()

    while True:
        print_menu()
        choice = input("  Choose an option: ").strip().lower()

        if   choice == "1": view_tasks(tasks)
        elif choice == "2": view_tasks(tasks, filter_status="pending")
        elif choice == "3": add_task(tasks)
        elif choice == "4": mark_done(tasks)
        elif choice == "5": delete_task(tasks)
        elif choice == "6": clear_done(tasks)
        elif choice == "q":
            print("\n  Goodbye!\n")
            break
        else:
            print("  ✗ Invalid option — choose from the menu.")


if __name__ == "__main__":
    main()