import json
from datetime import datetime

FILE = "tasks.json"


def load():
    try:
        with open(FILE, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save(tasks):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def show(tasks):
    if not tasks:
        print("List is empty.")
        return
    print()
    for i, t in enumerate(tasks, 1):
        status = "[+]" if t["done"] else "[ ]"
        print(f"  {i}. {status} [{t['priority']}] {t['title']}  (deadline: {t['deadline'] or '-'})")
    print()

def add(tasks):
    title    = input("Title: ").strip()
    priority = input("Priority (high/medium/low) [medium]: ").strip() or "medium"
    deadline = input("Deadline (DD.MM.YYYY, Enter - none): ").strip() or None
    tasks.append({"title": title, "priority": priority, "deadline": deadline, "done": False,
                  "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")})
    save(tasks)
    print("Added.")

def delete(tasks):
    show(tasks)
    n = input("Number to delete: ").strip()
    if n.isdigit() and 1 <= int(n) <= len(tasks):
        removed = tasks.pop(int(n) - 1)
        save(tasks)
        print(f"'{removed['title']}' deleted.")
    else:
        print("Invalid number.")

def toggle(tasks):
    show(tasks)
    n = input("Number to toggle: ").strip()
    if n.isdigit() and 1 <= int(n) <= len(tasks):
        t = tasks[int(n) - 1]
        t["done"] = not t["done"]
        save(tasks)
        print("Status:", "Done" if t["done"] else "In progress")
    else:
        print("Invalid number.")

def search(tasks):
    q = input("Search: ").strip().lower()
    results = [t for t in tasks if q in t["title"].lower()]
    show(results) if results else print("Nothing found.")

def sort_and_show(tasks):
    print("Sort by: [1] Priority  [2] Deadline  [3] Created date")
    c = input("Choice: ").strip()
    order = {"high": 1, "medium": 2, "low": 3}
    if c == "1":
        show(sorted(tasks, key=lambda t: order.get(t["priority"], 9)))
    elif c == "2":
        show(sorted(tasks, key=lambda t: t["deadline"] or "9999"))
    elif c == "3":
        show(sorted(tasks, key=lambda t: t.get("created_at", "")))
    else:
        print("Invalid choice.")


def main():
    tasks = load()
    while True:
        print("--- TODO+ ----------------------------")
        print("1. Show all        4. Toggle done")
        print("2. Add             5. Search")
        print("3. Delete          6. Sort")
        print("0. Exit")
        print("--------------------------------------")
        c = input("Choice: ").strip()

        if   c == "1": show(tasks)
        elif c == "2": add(tasks)
        elif c == "3": delete(tasks)
        elif c == "4": toggle(tasks)
        elif c == "5": search(tasks)
        elif c == "6": sort_and_show(tasks)
        elif c == "0": print("Bye!"); break
        else:          print("Invalid choice.")

if __name__ == "__main__":
    main()
