import datetime
import random

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

# Show app title and description.
st.set_page_config(page_title="Projects & Marketing Campaign Tracker", page_icon="📊")
st.title("📊 Projects & Marketing Campaign Tracker")
st.write(
    """
    This app helps you manage marketing campaign projects. Track campaign details, 
    timelines, and team assignments. Create new campaigns, edit existing ones, 
    and view campaign statistics.
    """
)

# Create a random Pandas dataframe with existing campaigns.
if "df" not in st.session_state:

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
    
    data = {
        "Campaign ID": [f"CAMP-{i}" for i in range(1100, 1000, -1)],
        "Campaign Name": np.random.choice(campaign_names, size=100),
        "Status": np.random.choice(["Planning", "Active", "Completed"], size=100),
        "Priority": np.random.choice(["High", "Medium", "Low"], size=100),
        "Start Date": start_dates,
        "End Date": [
            start_dates[i] + datetime.timedelta(days=random.randint(7, 90))
            for i in range(100)
        ],
        "Assigned To": np.random.choice(team_members, size=100),
    }
    df = pd.DataFrame(data)

    # Save the dataframe in session state (a dictionary-like object that persists across
    # page runs). This ensures our data is persisted when the app updates.
    st.session_state.df = df


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
        assigned_to = st.selectbox("Assigned To", [
            "Alice Johnson", "Bob Smith", "Carol Davis", "David Wilson",
            "Emma Brown", "Frank Miller", "Grace Lee", "Henry Taylor"
        ])
        end_date = st.date_input("End Date", value=datetime.date.today() + datetime.timedelta(days=30))
    
    submitted = st.form_submit_button("Submit")

if submitted:
    # Make a dataframe for the new campaign and append it to the dataframe in session
    # state.
    recent_campaign_number = int(max(st.session_state.df["Campaign ID"]).split("-")[1])
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
            }
        ]
    )

    # Show a little success message.
    st.write("Campaign submitted! Here are the campaign details:")
    st.dataframe(df_new, use_container_width=True, hide_index=True)
    st.session_state.df = pd.concat([df_new, st.session_state.df], axis=0)

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
        "Assigned To": st.column_config.SelectboxColumn(
            "Assigned To",
            help="Team member assigned to campaign",
            options=[
                "Alice Johnson", "Bob Smith", "Carol Davis", "David Wilson",
                "Emma Brown", "Frank Miller", "Grace Lee", "Henry Taylor"
            ],
            required=True,
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
