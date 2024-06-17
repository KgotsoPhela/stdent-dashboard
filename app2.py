import streamlit as st
import json
import datetime
import pandas as pd
import plotly.express as px

# Set wide layout
st.set_page_config(layout="wide")

# Load the JSON file
def load_data():
    with open('data.json', 'r') as f:
        return json.load(f)

# Initialize data
data = load_data()

# Function to update week status
def update_week_status(week):
    if week["total_paid_amount"] >= week["amount_per_week"] and (datetime.date.today() - datetime.datetime.strptime(week["week_start_date"], "%Y-%m-%d").date()).days > 6:
        week["status"] = "Closed"
    else:
        week["status"] = "Not Closed"

# Calculate statistics
total_sessions = sum(len(week["sessions"]) for week in data["weeks"])
total_payments = sum(week['total_paid_amount'] for week in data['weeks'])
total_outstanding = sum(week['total_outstanding_amount'] for week in data['weeks'])

# Display dashboard
st.title("Dashboard")

# Display statistics in card-like containers
st.header("Statistics")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div style="padding: 10px; border-radius: 5px; background-color: #f0f2f6; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
        <h3>Total Sessions Held</h3>
        <p style="font-size: 24px;">{}</p>
    </div>
    """.format(total_sessions), unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div style="padding: 10px; border-radius: 5px; background-color: #f0f2f6; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
        <h3>Total Payments Made</h3>
        <p style="font-size: 24px;">R{}</p>
    </div>
    """.format(total_payments), unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div style="padding: 10px; border-radius: 5px; background-color: #f0f2f6; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
        <h3>Total Outstanding Payments</h3>
        <p style="font-size: 24px;">R{}</p>
    </div>
    """.format(total_outstanding), unsafe_allow_html=True)

# Display the breakdown of outstanding payments by week only if there are outstanding payments
outstanding_weeks = [week for week in data["weeks"] if week['total_outstanding_amount'] > 0]
if outstanding_weeks:
    st.header("Outstanding Payments Breakdown")
    for week in outstanding_weeks:
        st.markdown(f"""
            <div style="padding: 10px; border-radius: 5px; background-color: #f0f2f6; border: 2px solid #ff6666; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); margin-bottom: 10px;">
                <p><b>{week['week_name']}:</b> R{week['total_outstanding_amount']}</p>
            </div>
        """, unsafe_allow_html=True)

# Display weekly summary in expander
st.header("Weekly Summary")
with st.expander("Expand to see weekly summary"):
    for week in data["weeks"]:
        st.markdown("""
        <div style="padding: 10px; border-radius: 5px; background-color: #e0f7fa; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); margin-bottom: 10px;">
            <h4>{}</h4>
            <p><b>Date:</b> {} || {}<br>
            <b>Sessions Completed:</b> {}<br>
            <b>Status:</b> {}<br>
            <b>Outstanding Amount:</b> R{}</p>
        </div>
        """.format(week['week_name'], week['week_start_date'], week['week_end_date'], len(week['sessions']), week['status'], week['total_outstanding_amount']), unsafe_allow_html=True)

# Display detailed table for the current week
st.header("Current Week Details")
current_week = max(data["weeks"], key=lambda w: datetime.datetime.strptime(w["week_start_date"], "%Y-%m-%d"))
st.markdown("""
<div style="padding: 10px; border-radius: 5px; background-color: #e8f5e9; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); margin-bottom: 10px;">
    <h4>Current Week: {}</h4>
    <p><b>Date:</b> {} || {}<br>
    <b>Sessions Completed:</b> {}<br>
    <b>Total Paid Amount:</b> R{}<br>
    <b>Total Outstanding Amount:</b> R{}<br>
    <b>Status:</b> {}</p>
</div>
""".format(current_week['week_name'], current_week['week_start_date'], current_week['week_end_date'], len(current_week['sessions']), current_week['total_paid_amount'], current_week['total_outstanding_amount'], current_week['status']), unsafe_allow_html=True)

# Display sessions for the current week
sessions_df = pd.DataFrame(current_week["sessions"])
st.divider()
st.subheader("Current Week Sessions")
st.table(sessions_df)
st.divider()

# Prepare data for graphs
weeks_df = pd.DataFrame(data["weeks"])

col1, col2 = st.columns(2)

# Total Sessions Per Week
with col1:
    st.header("Total Sessions Per Week")
    fig = px.bar(weeks_df, x="week_name", y=weeks_df["sessions"].apply(len), labels={"y": "Number of Sessions", "week_name": "Week"})
    st.plotly_chart(fig, use_container_width=True)

# Payments Made vs. Outstanding
with col2:
    st.header("Payments Made vs. Outstanding")
    fig = px.bar(weeks_df, x="week_name", y=["total_paid_amount", "total_outstanding_amount"], labels={"value": "Amount (R)", "week_name": "Week"})
    st.plotly_chart(fig, use_container_width=True)

# Cumulative Payments Over Time
st.header("Cumulative Payments Over Time")
weeks_df["cumulative_paid"] = weeks_df["total_paid_amount"].cumsum()
fig = px.line(weeks_df, x="week_name", y="cumulative_paid", labels={"cumulative_paid": "Cumulative Payments (R)", "week_name": "Week"}, markers=True)
st.plotly_chart(fig, use_container_width=True)

# Run the app
if __name__ == '__main__':
    st.write("Streamlit app is running...")
