"""
main.py — CLI demo for PawPal+ scheduling system
Run: python main.py
"""

from pawpal_system import parse_task, build_schedule, print_schedule


def run_demo():
    print("=== PawPal+ Demo ===\n")

    # Demo 1: Basic conflict
    print("Demo 1 — Conflict between Walk and Grooming")
    tasks = [
        parse_task("Walk",     "08:00 AM", 30, "HIGH",   pet_name="Buddy"),
        parse_task("Grooming", "08:10 AM", 45, "MEDIUM", pet_name="Buddy"),
        parse_task("Feeding",  "07:00 AM", 15, "HIGH",   pet_name="Buddy"),
    ]
    schedule, removed = build_schedule(tasks)
    print_schedule(schedule, removed)

    # Demo 2: No conflicts
    print("Demo 2 — Three tasks, no conflicts")
    tasks2 = [
        parse_task("Feeding",  "07:00 AM", 15, "HIGH", pet_name="Luna"),
        parse_task("Walk",     "09:00 AM", 30, "HIGH", pet_name="Luna"),
        parse_task("Nap time", "02:00 PM", 60, "LOW",  pet_name="Luna"),
    ]
    schedule2, removed2 = build_schedule(tasks2)
    print_schedule(schedule2, removed2)

    # Demo 3: Three-way conflict
    print("Demo 3 — Three-way conflict at 10:00 AM")
    tasks3 = [
        parse_task("Vet visit", "10:00 AM", 60, "HIGH",   pet_name="Max"),
        parse_task("Bath",      "10:15 AM", 45, "MEDIUM", pet_name="Max"),
        parse_task("Playtime",  "10:30 AM", 30, "LOW",    pet_name="Max"),
    ]
    schedule3, removed3 = build_schedule(tasks3)
    print_schedule(schedule3, removed3)


if __name__ == "__main__":
    run_demo()
