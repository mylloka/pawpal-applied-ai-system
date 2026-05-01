"""
app.py — Streamlit UI for PawPal+
Run: streamlit run app.py
"""

import streamlit as st
from pawpal_system import parse_task, build_schedule

st.set_page_config(page_title="PawPal+", page_icon="🐾")
st.title("🐾 PawPal+ Scheduler")
st.caption("Build a conflict-free daily schedule for your pets.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

# ── Add a task ──────────────────────────────────────────────────────────────
with st.expander("➕ Add a task", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        task_name  = st.text_input("Task name", placeholder="e.g. Morning walk")
        pet_name   = st.text_input("Pet name",  placeholder="e.g. Buddy")
        start_time = st.text_input("Start time", placeholder="e.g. 8:00 AM")
    with col2:
        duration   = st.number_input("Duration (minutes)", min_value=1, max_value=480, value=30)
        priority   = st.selectbox("Priority", ["HIGH", "MEDIUM", "LOW"])
        recurring  = st.selectbox("Recurring", [None, "daily", "weekly"])

    if st.button("Add task"):
        if not task_name or not start_time:
            st.warning("Please fill in task name and start time.")
        else:
            try:
                task = parse_task(task_name, start_time, duration, priority,
                                  pet_name=pet_name, recurring=recurring)
                st.session_state.tasks.append(task)
                st.success(f"Added: {task_name} at {start_time}")
            except ValueError as e:
                st.error(f"Input error: {e}")

# ── Task list ───────────────────────────────────────────────────────────────
if st.session_state.tasks:
    st.subheader(f"Tasks added ({len(st.session_state.tasks)})")
    for i, t in enumerate(st.session_state.tasks):
        st.write(f"{i+1}. {t.name} | {t.start_time.strftime('%I:%M %p')} | "
                 f"{t.duration_minutes} min | {t.priority} | {t.pet_name}")

    col_build, col_clear = st.columns([1, 1])
    with col_build:
        if st.button("🗓️ Build schedule", type="primary"):
            schedule, removed = build_schedule(st.session_state.tasks)
            st.subheader("✅ Final Schedule")
            if not schedule:
                st.info("No tasks could be scheduled.")
            for task in schedule:
                st.success(str(task))

            if removed:
                st.subheader("⚠️ Removed (conflicts)")
                for entry in removed:
                    st.warning(f"{entry['task'].name} — {entry['reason']}")
    with col_clear:
        if st.button("Clear all tasks"):
            st.session_state.tasks = []
            st.rerun()
else:
    st.info("No tasks yet. Add one above to get started.")
