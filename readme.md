# PawPal+ Applied AI System

## Project Summary

This project helps pet owners create a daily schedule for their pets. It builds a plan automatically and avoids time conflicts.

## Original Project

The original PawPal project allowed users to add pets and tasks. In this version, I added automatic scheduling, conflict detection, and testing.

## AI Feature

This project uses a testing system as its AI feature. I created 13 tests to check scheduling, conflicts, sorting, and recurrence to make sure the system works correctly.

## How It Works

Tasks are sorted by priority. The system builds a schedule and removes tasks that overlap. The final schedule is shown in order.

## Example

If there is a walk at 8:00 with high priority and grooming at 8:10 with medium priority, the system detects a conflict and keeps the walk.

## Testing

There are 13 tests and all of them pass. They check conflicts, recurrence, sorting, and edge cases.

## Limitations

The system does not learn from users and only uses fixed time slots. The user interface is not tested.

## How to Run

Run python main.py to see the demo.
Run streamlit run app.py to open the app.
Run python -m pytest test_pawpal.py -v to run tests.

## Demo

Add your Loom video link here.

## Files

pawpal_system.py
app.py
main.py
test_pawpal.py
requirements.txt
assets
