import datetime
import random
import io
import sqlite3
import os

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st


# Show app title and description.
st.set_page_config(page_title="Project & Marketing Campaign Tracker", page_icon="📊")
st.title("📊 Project & Marketing Campaign Tracker")
st.write(
    """
    This app helps you manage marketing campaign projects. Track campaign details, 
    timelines, and team assignments. Create new campaigns, edit existing ones, 
    and view campaign statistics.
    """
)

# Helper function to calculate progress percentage
def calculate_progress(status, start_date, end_date):
    """Calculate progress percentage based on status and dates."""
    if status == "Completed":
        return 100
    if status == "Planning":
        return 0
    today = datetime.date.today()
    total_days = (end_date - start_date).days
    elapsed_days = (today - start_date).days
    if total_days <= 0:
        return 0
    progress = min(100, max(0, int(100 * elapsed_days / total_days)))
    return progress

# Database initialization
DB_PATH = "campaigns.db"

def init_db():
    """Initialize the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            campaign_id TEXT PRIMARY KEY,
            campaign_name TEXT,
            status TEXT,
            priority TEXT,
            start_date DATE,
            end_date DATE,
            assigned_to TEXT,
            progress_pct INTEGER,
            remarks TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_campaigns_to_db(df):
    """Save campaigns dataframe to SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Clear existing data
    c.execute("DELETE FROM campaigns")
    
    # Insert new data
    for _, row in df.iterrows():
        c.execute("""
            INSERT INTO campaigns VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["Campaign ID"],
            row["Campaign Name"],
            row["Status"],
            row["Priority"],
            str(row["Start Date"]),
            str(row["End Date"]),
            row["Assigned To"],
            int(row["Progress (%)"]),
            row["Remarks"]
        ))
    
    conn.commit()
    conn.close()

def load_campaigns_from_db():
    """Load campaigns from SQLite database."""
    if not os.path.exists(DB_PATH):
        return None
    
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM campaigns", conn)
    conn.close()
    
    if df.empty:
        return None
    
    # Rename columns to match dataframe structure
    df = df.rename(columns={
        "campaign_id": "Campaign ID",
        "campaign_name": "Campaign Name",
        "status": "Status",
        "priority": "Priority",
        "start_date": "Start Date",
        "end_date": "End Date",
        "assigned_to": "Assigned To",
        "progress_pct": "Progress (%)",
        "remarks": "Remarks"
    })
    
    # Convert date strings to date objects
    df["Start Date"] = pd.to_datetime(df["Start Date"]).dt.date
    df["End Date"] = pd.to_datetime(df["End Date"]).dt.date
    
    return df

# Create a random Pandas dataframe with existing campaigns.
if "df" not in st.session_state:
    
    # Initialize database
    init_db()
    
    # Try to load from database first
    loaded_df = load_campaigns_from_db()
    
    if loaded_df is not None:
        st.session_state.df = loaded_df
    else:
        # Set seed for reproducibility.
        np.random.seed(42)

        # Make up some fake campaign names.
        campaign_names = [
            "Summer Product Launch 2024",
            "Black Friday Sales Campaign",
            "Email Marketing Blitz",
            "Social Media Awareness Campaign",
            "Holiday Season Promotion",
            "Brand Relaunch Initiative",
            "New Product Feature Launch",
            "Customer Loyalty Program",
            "Seasonal Clearance Sale",
            "Influencer Collaboration Campaign",
            "Back to School Promotion",
            "Valentine's Day Campaign",
            "Earth Day Green Initiative",
            "Spring Collection Launch",
            "Summer Internship Recruitment",
            "Q4 Revenue Growth Campaign",
            "Mobile App Marketing Push",
            "Webinar Series Launch",
            "Content Marketing Sprint",
            "Customer Referral Program",
        ]

        team_members = [
            "Alice Johnson",
            "Bob Smith",
            "Carol Davis",
            "David Wilson",
            "Emma Brown",
            "Frank Miller",
            "Grace Lee",
            "Henry Taylor",
        ]

        # Generate the dataframe with 100 rows/campaigns.
        start_dates = [
            datetime.date(2024, 1, 1) + datetime.timedelta(days=random.randint(0, 200))
            for _ in range(100)
        ]
        
        statuses = np.random.choice(["Planning", "Active", "Completed"], size=100)
        
        data = {
            "Campaign ID": [f"CAMP-{i}" for i in range(1100, 1000, -1)],
            "Campaign Name": np.random.choice(campaign_names, size=100),
            "Status": statuses,
            "Priority": np.random.choice(["High", "Medium", "Low"], size=100),
            "Start Date": start_dates,
            "End Date": [
                start_dates[i] + datetime.timedelta(days=random.randint(7, 90))
                for i in range(100)
            ],
            "Assigned To": np.random.choice(team_members, size=100),
            "Progress (%)": [calculate_progress(statuses[i], start_dates[i], 
                             start_dates[i] + datetime.timedelta(days=random.randint(7, 90))) 
                             for i in range(100)],
            "Remarks": [""] * 100,
        }
        df = pd.DataFrame(data)
        st.session_state.df = df
        
        # Save initial data to database
        save_campaigns_to_db(st.session_state.df)
    
    st.session_state.activity_log = []  # Track changes


# Show a section to add a new campaign.
st.header("Add a Campaign")

# We're adding campaigns via an `st.form` and some input widgets. If widgets are used
# in a form, the app will only rerun once the submit button is pressed.
with st.form("add_campaign_form"):
    col1, col2 = st.columns(2)
    with col1:
        campaign_name = st.text_input("Campaign Name")
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        start_date = st.date_input("Start Date", value=datetime.date.today())
    with col2:
        status = st.selectbox("Status", ["Planning", "Active", "Completed"])
        # Allow selecting an existing assignee or entering a new name
        existing_assignees = sorted(
            set(st.session_state.df["Assigned To"].fillna("").astype(str).unique())
        )
        existing_assignees = [a for a in existing_assignees if a != ""]
        if existing_assignees:
            assignee_options = ["Enter a new name"] + existing_assignees
            assignee_choice = st.selectbox("Assigned To", assignee_options)
            if assignee_choice == "Enter a new name":
                assigned_to = st.text_input(
                    "New assignee name",
                    placeholder="Enter assignee name (e.g. Alice Johnson)",
                )
            else:
                assigned_to = assignee_choice
        else:
            assigned_to = st.text_input(
                "New assignee name",
                placeholder="Enter assignee name (e.g. Alice Johnson)",
            )
        end_date = st.date_input("End Date", value=datetime.date.today() + datetime.timedelta(days=30))
    
    remarks = st.text_area("Remarks (optional)", placeholder="Add any notes or progress updates", height=60)
    submitted = st.form_submit_button("Submit")

if submitted:
    # Make a dataframe for the new campaign and append it to the dataframe in session
    # state.
    recent_campaign_number = int(max(st.session_state.df["Campaign ID"]).split("-")[1])
    progress = calculate_progress(status, start_date, end_date)
    df_new = pd.DataFrame(
        [
            {
                "Campaign ID": f"CAMP-{recent_campaign_number+1}",
                "Campaign Name": campaign_name,
                "Status": status,
                "Priority": priority,
                "Start Date": start_date,
                "End Date": end_date,
                "Assigned To": assigned_to,
                "Progress (%)": progress,
                "Remarks": remarks,
            }
        ]
    )

    # Show a little success message.
    st.write("Campaign submitted! Here are the campaign details:")
    st.dataframe(df_new, use_container_width=True, hide_index=True)
    st.session_state.df = pd.concat([df_new, st.session_state.df], axis=0)
    
    # Save to database
    save_campaigns_to_db(st.session_state.df)
    
    # Log activity
    st.session_state.activity_log.append({
        "timestamp": datetime.datetime.now(),
        "action": "Created",
        "campaign_id": f"CAMP-{recent_campaign_number+1}",
        "campaign_name": campaign_name,
        "user": "User"
    })

# Show section to view and edit existing campaigns in a table.
st.header("Existing Campaigns")
st.write(f"Number of campaigns: `{len(st.session_state.df)}`")

st.info(
    "You can edit the campaigns by double clicking on a cell. Note how the plots below "
    "update automatically! You can also sort the table by clicking on the column headers.",
    icon="✍️",
)

# Show the campaigns dataframe with `st.data_editor`. This lets the user edit the table
# cells. The edited data is returned as a new dataframe.
edited_df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Status": st.column_config.SelectboxColumn(
            "Status",
            help="Campaign status",
            options=["Planning", "Active", "Completed"],
            required=True,
        ),
        "Priority": st.column_config.SelectboxColumn(
            "Priority",
            help="Campaign priority",
            options=["High", "Medium", "Low"],
            required=True,
        ),
        "Assigned To": st.column_config.TextColumn(
            "Assigned To",
            help="Team member assigned to campaign",
            required=True,
        ),
        "Progress (%)": st.column_config.SelectboxColumn(
            "Progress (%)",
            help="Campaign progress - select from list",
            options=[i for i in range(0, 101, 5)],  # 0, 5, 10, 15, ..., 100
            required=True,
        ),
        "Remarks": st.column_config.TextColumn(
            "Remarks",
            help="Notes and progress updates",
            width="medium",
        ),
        "Start Date": st.column_config.DateColumn(
            "Start Date",
            help="Campaign start date",
            format="YYYY-MM-DD",
        ),
        "End Date": st.column_config.DateColumn(
            "End Date",
            help="Campaign end date",
            format="YYYY-MM-DD",
        ),
    },
    # Disable editing the Campaign ID column.
    disabled=["Campaign ID"],
)

# Sync back to session state if changed
st.session_state.df = edited_df

# Ensure date columns are datetime objects
st.session_state.df["Start Date"] = pd.to_datetime(st.session_state.df["Start Date"]).dt.date
st.session_state.df["End Date"] = pd.to_datetime(st.session_state.df["End Date"]).dt.date

# Save to database after edits
save_campaigns_to_db(st.session_state.df)

# Auto-calculate progress button
st.write("")
col_auto, col_manual = st.columns([1, 2])
with col_auto:
    if st.button("🔄 Auto-calculate Progress"):
        for idx, row in st.session_state.df.iterrows():
            st.session_state.df.at[idx, "Progress (%)"] = calculate_progress(
                row["Status"],
                row["Start Date"],
                row["End Date"]
            )
        # Save to database
        save_campaigns_to_db(st.session_state.df)
        st.success("Progress updated based on status and dates!")
        st.rerun()

with col_manual:
    st.info("**Progress Update Tips:**\n- Click 'Auto-calculate' to set progress based on status (Completed=100%, Planning=0%, Active=based on elapsed time)\n- Manually edit the Progress column in the table above for custom values")

# Show some metrics and charts about the campaigns.
st.header("Statistics")

# Show metrics side by side using `st.columns` and `st.metric`.
col1, col2, col3 = st.columns(3)
num_active_campaigns = len(st.session_state.df[st.session_state.df.Status == "Active"])
num_completed_campaigns = len(st.session_state.df[st.session_state.df.Status == "Completed"])
num_planning_campaigns = len(st.session_state.df[st.session_state.df.Status == "Planning"])
col1.metric(label="Active Campaigns", value=num_active_campaigns, delta=2)
col2.metric(label="Completed Campaigns", value=num_completed_campaigns, delta=5)
col3.metric(label="In Planning", value=num_planning_campaigns, delta=-1)

# Show two Altair charts using `st.altair_chart`.
st.write("")
st.write("##### Campaign status per month")
status_plot = (
    alt.Chart(edited_df)
    .mark_bar()
    .encode(
        x="month(Start Date):O",
        y="count():Q",
        xOffset="Status:N",
        color="Status:N",
    )
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(status_plot, use_container_width=True, theme="streamlit")

st.write("##### Current campaign priorities")
priority_plot = (
    alt.Chart(edited_df)
    .mark_arc()
    .encode(theta="count():Q", color="Priority:N")
    .properties(height=300)
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(priority_plot, use_container_width=True, theme="streamlit")

# Assignee-specific chart: allow selecting a name and show assigned vs completed counts
st.write("")
st.write("##### Projects assigned and completed (by assignee)")
assignees = sorted(set(st.session_state.df["Assigned To"].fillna("").astype(str).unique()))
assignees = [a for a in assignees if a != ""]
assignee_options = ["All"] + assignees
selected_assignee = st.selectbox("Select assignee", assignee_options)

if selected_assignee == "All":
    df_assignee = st.session_state.df
else:
    df_assignee = st.session_state.df[st.session_state.df["Assigned To"] == selected_assignee]

assigned_count = len(df_assignee)
completed_count = len(df_assignee[df_assignee.Status == "Completed"])

chart_df = pd.DataFrame({
    "Category": ["Assigned", "Completed"],
    "Count": [assigned_count, completed_count],
})

assignee_chart = (
    alt.Chart(chart_df)
    .mark_bar()
    .encode(x="Category:N", y="Count:Q", color="Category:N")
    .properties(height=300)
)

st.altair_chart(assignee_chart, use_container_width=True, theme="streamlit")

# ACTIVITY LOG
st.write("")
st.header("Activity Log")
if st.session_state.activity_log:
    activity_df = pd.DataFrame(st.session_state.activity_log)
    st.dataframe(activity_df.sort_values("timestamp", ascending=False), use_container_width=True, hide_index=True)
else:
    st.info("No activity logged yet.")

# ASSIGNEE WORKLOAD
st.write("")
st.header("Assignee Workload")
workload_data = []
for assignee in sorted(set(st.session_state.df["Assigned To"].unique())):
    assignee_df = st.session_state.df[st.session_state.df["Assigned To"] == assignee]
    workload_data.append({
        "Assignee": assignee,
        "Total": len(assignee_df),
        "Active": len(assignee_df[assignee_df["Status"] == "Active"]),
        "Completed": len(assignee_df[assignee_df["Status"] == "Completed"]),
        "Planning": len(assignee_df[assignee_df["Status"] == "Planning"]),
        "Avg Progress": int(assignee_df["Progress (%)"].mean()),
    })
workload_df = pd.DataFrame(workload_data)
st.dataframe(workload_df, use_container_width=True, hide_index=True)

# TIMELINE CHART (Gantt-style)
st.write("")
st.header("Campaign Timeline")
gantt_df = st.session_state.df.copy()
# Ensure date columns are datetime for Altair
gantt_df["Start Date"] = pd.to_datetime(gantt_df["Start Date"])
gantt_df["End Date"] = pd.to_datetime(gantt_df["End Date"])

timeline_chart = (
    alt.Chart(gantt_df)
    .mark_bar(height=15)
    .encode(
        y=alt.Y("Campaign Name:N", title="Campaign", sort=alt.SortField("Start Date")),
        x=alt.X("Start Date:T", title="Timeline"),
        x2="End Date:T",
        color=alt.Color("Status:N", scale=alt.Scale(
            domain=["Planning", "Active", "Completed"],
            range=["#ffcc00", "#0099ff", "#00cc00"]
        )),
        tooltip=["Campaign Name:N", "Status:N", "Assigned To:N", "Progress (%):Q"]
    )
    .properties(height=500)
)
st.altair_chart(timeline_chart, use_container_width=True, theme="streamlit")
