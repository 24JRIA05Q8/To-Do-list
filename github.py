import streamlit as st
from datetime import datetime, date, time, timedelta
import pandas as pd
import uuid

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Smart To-Do Manager",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #f5f7fb;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.app-title {
    font-size: 42px;
    font-weight: 800;
    color: #2563eb;
    margin-bottom: 0px;
}

.subtitle {
    color: #64748b;
    font-size: 18px;
    margin-bottom: 25px;
}

.task-card {
    padding: 20px;
    border-radius: 15px;
    background-color: white;
    border: 1px solid #e2e8f0;
    margin-bottom: 15px;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.05);
}

.stat-card {
    padding: 20px;
    border-radius: 15px;
    background-color: white;
    border: 1px solid #e2e8f0;
    text-align: center;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.05);
}

.stat-number {
    font-size: 32px;
    font-weight: bold;
    color: #2563eb;
}

.stat-label {
    color: #64748b;
    font-size: 14px;
}

.priority-high {
    color: #dc2626;
    font-weight: bold;
}

.priority-medium {
    color: #d97706;
    font-weight: bold;
}

.priority-low {
    color: #16a34a;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "role" not in st.session_state:
    st.session_state.role = ""

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_status(task):
    """Automatically calculate task status."""

    if task["progress"] >= 100:
        return "Completed"

    now = datetime.now()
    due_datetime = datetime.strptime(
        task["due_datetime"],
        "%Y-%m-%d %H:%M"
    )

    if due_datetime < now:
        return "Overdue"

    remaining = due_datetime - now

    if remaining <= timedelta(hours=24):
        return "Due Soon"

    if task["progress"] > 0:
        return "In Progress"

    return "Pending"


def get_status_emoji(status):

    status_icons = {
        "Completed": "🟢",
        "In Progress": "🔵",
        "Pending": "🟡",
        "Due Soon": "🟠",
        "Overdue": "🔴"
    }

    return status_icons.get(status, "⚪")


def get_time_remaining(due_datetime):

    due = datetime.strptime(
        due_datetime,
        "%Y-%m-%d %H:%M"
    )

    now = datetime.now()

    if due < now:
        difference = now - due

        days = difference.days
        hours = difference.seconds // 3600

        if days > 0:
            return f"Overdue by {days} day(s) {hours} hour(s)"

        return f"Overdue by {hours} hour(s)"

    difference = due - now

    days = difference.days
    hours = difference.seconds // 3600
    minutes = (difference.seconds % 3600) // 60

    if days > 0:
        return f"{days} day(s) {hours} hour(s) remaining"

    if hours > 0:
        return f"{hours} hour(s) {minutes} minute(s) remaining"

    return f"{minutes} minute(s) remaining"


def delete_task(task_id):

    st.session_state.tasks = [
        task for task in st.session_state.tasks
        if task["id"] != task_id
    ]


def update_progress(task_id, progress):

    for task in st.session_state.tasks:

        if task["id"] == task_id:

            task["progress"] = progress

            if progress >= 100:
                task["status"] = "Completed"
            else:
                task["status"] = get_status(task)


def export_tasks():

    if not st.session_state.tasks:
        return None

    data = []

    for task in st.session_state.tasks:

        row = task.copy()

        row["status"] = get_status(task)

        data.append(row)

    df = pd.DataFrame(data)

    return df.to_csv(index=False).encode("utf-8")


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## ⚡ Smart To-Do")

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Add Task",
            "My Tasks",
            "Statistics"
        ],
        index=[
            "Dashboard",
            "Add Task",
            "My Tasks",
            "Statistics"
        ].index(st.session_state.page)
    )

    st.session_state.page = page

    st.divider()

    st.markdown("### 👤 Your Role")

    role = st.selectbox(
        "Select your role",
        [
            "Student",
            "Teacher",
            "Engineer",
            "Employee",
            "Freelancer",
            "Business Owner",
            "Other"
        ],
        index=0
    )

    st.session_state.role = role

    st.divider()

    st.info(
        "💡 Tasks are stored in Streamlit session memory. "
        "No database is used."
    )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="app-title">✅ Smart To-Do Manager</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="subtitle">Welcome, {st.session_state.role}! '
    'Manage your tasks efficiently.</div>',
    unsafe_allow_html=True
)


# =========================================================
# DASHBOARD
# =========================================================

if st.session_state.page == "Dashboard":

    tasks = st.session_state.tasks

    total = len(tasks)

    completed = sum(
        1 for task in tasks
        if get_status(task) == "Completed"
    )

    overdue = sum(
        1 for task in tasks
        if get_status(task) == "Overdue"
    )

    due_soon = sum(
        1 for task in tasks
        if get_status(task) == "Due Soon"
    )

    pending = sum(
        1 for task in tasks
        if get_status(task) in ["Pending", "In Progress"]
    )

    if total > 0:
        overall_progress = sum(
            task["progress"] for task in tasks
        ) / total
    else:
        overall_progress = 0

    # -------------------------
    # STATISTICS CARDS
    # -------------------------

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number">{total}</div>
                <div class="stat-label">Total Tasks</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number">{completed}</div>
                <div class="stat-label">Completed</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number">{pending}</div>
                <div class="stat-label">Pending</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number">{due_soon}</div>
                <div class="stat-label">Due Soon</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col5:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number">{overdue}</div>
                <div class="stat-label">Overdue</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")

    # -------------------------
    # ALERTS
    # -------------------------

    overdue_tasks = [
        task for task in tasks
        if get_status(task) == "Overdue"
    ]

    due_soon_tasks = [
        task for task in tasks
        if get_status(task) == "Due Soon"
    ]

    if overdue_tasks:

        st.error(
            f"🚨 You have {len(overdue_tasks)} overdue task(s)! "
            "Please complete them as soon as possible."
        )

    if due_soon_tasks:

        st.warning(
            f"⏰ {len(due_soon_tasks)} task(s) are due within "
            "the next 24 hours."
        )

    # -------------------------
    # OVERALL PROGRESS
    # -------------------------

    st.subheader("📊 Overall Progress")

    st.progress(
        int(overall_progress) / 100
    )

    st.write(
        f"**{overall_progress:.1f}%** of your tasks are completed."
    )

    # -------------------------
    # RECENT TASKS
    # -------------------------

    st.subheader("📋 Recent Tasks")

    if not tasks:

        st.info(
            "No tasks yet. Go to **Add Task** to create your first task."
        )

    else:

        recent_tasks = tasks[-5:]
        recent_tasks.reverse()

        for task in recent_tasks:

            status = get_status(task)
            emoji = get_status_emoji(status)

            with st.container():

                st.markdown(
                    f"""
                    <div class="task-card">
                        <h3>{emoji} {task['title']}</h3>
                        <p>{task['description']}</p>
                        <b>Priority:</b> {task['priority']} &nbsp;&nbsp;
                        <b>Category:</b> {task['category']}<br><br>
                        <b>Progress:</b> {task['progress']}%<br>
                        <b>Status:</b> {status}<br>
                        <b>Deadline:</b> {task['due_datetime']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.progress(task["progress"] / 100)


# =========================================================
# ADD TASK
# =========================================================

elif st.session_state.page == "Add Task":

    st.subheader("➕ Add New Task")

    with st.form("add_task_form"):

        title = st.text_input(
            "Task Name *",
            placeholder="Example: Complete Python Assignment"
        )

        description = st.text_area(
            "Task Description",
            placeholder="Describe what needs to be completed..."
        )

        col1, col2 = st.columns(2)

        with col1:

            category = st.selectbox(
                "Category",
                [
                    "College",
                    "Work",
                    "Personal",
                    "Project",
                    "Study",
                    "Meeting",
                    "Other"
                ]
            )

        with col2:

            priority = st.selectbox(
                "Priority",
                [
                    "Low",
                    "Medium",
                    "High",
                    "Urgent"
                ]
            )

        st.markdown("### 📅 Schedule")

        col1, col2 = st.columns(2)

        with col1:

            added_date = st.date_input(
                "Added Date",
                value=date.today()
            )

        with col2:

            added_time = st.time_input(
                "Added Time",
                value=datetime.now().time().replace(second=0, microsecond=0)
            )

        col1, col2 = st.columns(2)

        with col1:

            due_date = st.date_input(
                "Completion / Due Date",
                value=date.today() + timedelta(days=1)
            )

        with col2:

            due_time = st.time_input(
                "Completion / Due Time",
                value=time(18, 0)
            )

        st.markdown("### 📈 Initial Progress")

        progress = st.slider(
            "How much of this task is already completed?",
            min_value=0,
            max_value=100,
            value=0,
            step=10
        )

        submitted = st.form_submit_button(
            "🚀 Add Task",
            use_container_width=True
        )

        if submitted:

            if not title.strip():

                st.error("Please enter a task name.")

            else:

                added_datetime = datetime.combine(
                    added_date,
                    added_time
                )

                due_datetime = datetime.combine(
                    due_date,
                    due_time
                )

                if due_datetime <= added_datetime:

                    st.error(
                        "Completion date/time must be after "
                        "the added date/time."
                    )

                else:

                    new_task = {
                        "id": str(uuid.uuid4()),
                        "title": title.strip(),
                        "description": description.strip(),
                        "category": category,
                        "priority": priority,
                        "added_datetime": added_datetime.strftime(
                            "%Y-%m-%d %H:%M"
                        ),
                        "due_datetime": due_datetime.strftime(
                            "%Y-%m-%d %H:%M"
                        ),
                        "progress": progress,
                        "status": "Pending"
                    }

                    st.session_state.tasks.append(
                        new_task
                    )

                    st.success(
                        f"✅ Task '{title}' added successfully!"
                    )

                    st.balloons()


# =========================================================
# MY TASKS
# =========================================================

elif st.session_state.page == "My Tasks":

    st.subheader("📋 My Tasks")

    tasks = st.session_state.tasks

    if not tasks:

        st.info(
            "No tasks available. Add your first task!"
        )

    else:

        # -------------------------
        # SEARCH & FILTER
        # -------------------------

        col1, col2, col3 = st.columns(3)

        with col1:

            search = st.text_input(
                "🔍 Search",
                placeholder="Search task..."
            )

        with col2:

            status_filter = st.selectbox(
                "Filter Status",
                [
                    "All",
                    "Completed",
                    "In Progress",
                    "Pending",
                    "Due Soon",
                    "Overdue"
                ]
            )

        with col3:

            priority_filter = st.selectbox(
                "Filter Priority",
                [
                    "All",
                    "Low",
                    "Medium",
                    "High",
                    "Urgent"
                ]
            )

        # -------------------------
        # FILTER TASKS
        # -------------------------

        filtered_tasks = []

        for task in tasks:

            status = get_status(task)

            matches_search = (
                search.lower() in task["title"].lower()
                or search.lower() in task["description"].lower()
            )

            matches_status = (
                status_filter == "All"
                or status == status_filter
            )

            matches_priority = (
                priority_filter == "All"
                or task["priority"] == priority_filter
            )

            if (
                matches_search
                and matches_status
                and matches_priority
            ):
                filtered_tasks.append(task)

        st.write(
            f"Showing **{len(filtered_tasks)}** task(s)"
        )

        # -------------------------
        # DISPLAY TASKS
        # -------------------------

        for task in filtered_tasks:

            status = get_status(task)
            emoji = get_status_emoji(status)

            with st.container():

                st.markdown(
                    f"""
                    <div class="task-card">
                        <h3>{emoji} {task['title']}</h3>
                        <p>{task['description']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.write(
                        f"**Category:** {task['category']}"
                    )

                with col2:
                    st.write(
                        f"**Priority:** {task['priority']}"
                    )

                with col3:
                    st.write(
                        f"**Status:** {status}"
                    )

                with col4:
                    st.write(
                        f"**Deadline:** {task['due_datetime']}"
                    )

                st.progress(
                    task["progress"] / 100
                )

                st.write(
                    f"📈 **Progress: {task['progress']}%**"
                )

                st.write(
                    f"⏳ **{get_time_remaining(task['due_datetime'])}**"
                )

                # -------------------------
                # UPDATE PROGRESS
                # -------------------------

                new_progress = st.slider(
                    f"Update Progress — {task['title']}",
                    0,
                    100,
                    task["progress"],
                    5,
                    key=f"progress_{task['id']}"
                )

                if new_progress != task["progress"]:

                    update_progress(
                        task["id"],
                        new_progress
                    )

                    st.rerun()

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        "✅ Mark Completed",
                        key=f"complete_{task['id']}",
                        use_container_width=True
                    ):

                        update_progress(
                            task["id"],
                            100
                        )

                        st.success(
                            "Task completed!"
                        )

                        st.rerun()

                with col2:

                    if st.button(
                        "🗑️ Delete",
                        key=f"delete_{task['id']}",
                        use_container_width=True
                    ):

                        delete_task(
                            task["id"]
                        )

                        st.success(
                            "Task deleted."
                        )

                        st.rerun()

                st.divider()


# =========================================================
# STATISTICS
# =========================================================

elif st.session_state.page == "Statistics":

    st.subheader("📊 Productivity Statistics")

    tasks = st.session_state.tasks

    if not tasks:

        st.info(
            "Add some tasks to see your statistics."
        )

    else:

        total = len(tasks)

        completed = sum(
            1 for task in tasks
            if get_status(task) == "Completed"
        )

        overdue = sum(
            1 for task in tasks
            if get_status(task) == "Overdue"
        )

        in_progress = sum(
            1 for task in tasks
            if get_status(task) == "In Progress"
        )

        pending = sum(
            1 for task in tasks
            if get_status(task) == "Pending"
        )

        average_progress = sum(
            task["progress"]
            for task in tasks
        ) / total

        # -------------------------
        # METRICS
        # -------------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Tasks",
                total
            )

        with col2:
            st.metric(
                "Completed",
                completed
            )

        with col3:
            st.metric(
                "Overdue",
                overdue
            )

        with col4:
            st.metric(
                "Average Progress",
                f"{average_progress:.1f}%"
            )

        st.divider()

        # -------------------------
        # STATUS CHART
        # -------------------------

        st.subheader("📌 Task Status")

        status_data = pd.DataFrame({
            "Status": [
                "Completed",
                "In Progress",
                "Pending",
                "Overdue"
            ],
            "Tasks": [
                completed,
                in_progress,
                pending,
                overdue
            ]
        })

        st.bar_chart(
            status_data.set_index("Status")
        )

        # -------------------------
        # CATEGORY ANALYSIS
        # -------------------------

        st.subheader("📚 Tasks by Category")

        category_data = {}

        for task in tasks:

            category = task["category"]

            category_data[category] = (
                category_data.get(category, 0) + 1
            )

        category_df = pd.DataFrame(
            list(category_data.items()),
            columns=["Category", "Tasks"]
        )

        st.bar_chart(
            category_df.set_index("Category")
        )

        # -------------------------
        # PRIORITY ANALYSIS
        # -------------------------

        st.subheader("🔥 Tasks by Priority")

        priority_data = {}

        for task in tasks:

            priority = task["priority"]

            priority_data[priority] = (
                priority_data.get(priority, 0) + 1
            )

        priority_df = pd.DataFrame(
            list(priority_data.items()),
            columns=["Priority", "Tasks"]
        )

        st.bar_chart(
            priority_df.set_index("Priority")
        )

        # -------------------------
        # EXPORT
        # -------------------------

        st.subheader("📥 Export Tasks")

        csv_data = export_tasks()

        if csv_data:

            st.download_button(
                label="⬇️ Download Tasks as CSV",
                data=csv_data,
                file_name="my_tasks.csv",
                mime="text/csv",
                use_container_width=True
            )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Smart To-Do Manager • Built with Python + Streamlit • "
    "No database used"
)