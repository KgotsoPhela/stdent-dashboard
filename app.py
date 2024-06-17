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

# Save the JSON file
def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

# Initialize data
data = load_data()

# Function to update week status
def update_week_status(week):
    if week["total_paid_amount"] >= week["amount_per_week"] and (datetime.date.today() - datetime.datetime.strptime(week["week_start_date"], "%Y-%m-%d").date()).days > 6:
        week["status"] = "Closed"
    else:
        week["status"] = "Not Closed"

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Manage Sessions", "Dashboard"])

if page == "Manage Sessions":
    st.title("Manage Sessions and Payments")
    
    # Define column widths
    col1, col2 = st.columns([3, 1])

    with col2:
        # Add a new week
        st.header("Add a New Week")
        week_start_date = st.date_input("Week Start Date", datetime.date.today())
        week_end_date = week_start_date + datetime.timedelta(days=5)

        # Determine the week number
        if data["weeks"]:
            week_number = len(data["weeks"]) + 1
        else:
            week_number = 1

        if st.button("Add Week"):
            new_week = {
                "week_name": f"week{week_number}",
                "week_start_date": week_start_date.strftime("%Y-%m-%d"),
                "week_end_date": week_end_date.strftime("%Y-%m-%d"),
                "amount_per_week": 600,
                "amount_per_session": 120,
                "normal_number_of_sessions_per_week": 5,
                "sessions": [],
                "total_paid_amount": 0,
                "total_outstanding_amount": 600,
                "status": "Not Closed"
            }
            data["weeks"].append(new_week)
            save_data(data)
            st.success("Week added successfully!")

        # Add a new session
        st.header("Add a New Session")
        selected_week = st.selectbox("Select Week", [week["week_name"] for week in data["weeks"]])
        session_date = st.date_input("Date", datetime.date.today())
        session_number = st.number_input("Session Number", min_value=1, step=1)
        payment_status = st.selectbox("Payment Status", ["Paid", "Not Paid"])
        notes = st.text_area("Notes")

        if st.button("Add Session"):
            for week in data["weeks"]:
                if week["week_name"] == selected_week:
                    session_paid_amount = 120 if payment_status == "Paid" else 0
                    session_outstanding_amount = 120 if payment_status == "Not Paid" else 0
                    new_session = {
                        "session_date": session_date.strftime("%Y-%m-%d"),
                        "session_number": session_number,
                        "payment_status": payment_status,
                        "session_paid_amount": session_paid_amount,
                        "session_outstanding_amount": session_outstanding_amount,
                        "notes": notes
                    }
                    week["sessions"].append(new_session)
                    week["total_paid_amount"] += session_paid_amount
                    week["total_outstanding_amount"] = week["amount_per_week"] - week["total_paid_amount"]
                    update_week_status(week)
                    save_data(data)
                    st.success("Session added successfully!")
                    break

        # Edit session payment status
        st.header("Edit Session Payment Status")
        selected_week_edit = st.selectbox("Select Week to Edit", [week["week_name"] for week in data["weeks"]])
        for week in data["weeks"]:
            if week["week_name"] == selected_week_edit:
                sessions_df_edit = pd.DataFrame(week["sessions"])
                if not sessions_df_edit.empty:
                    session_to_edit = st.selectbox("Select Session to Edit", sessions_df_edit["session_number"])
                    new_payment_status = st.selectbox("New Payment Status", ["Paid", "Not Paid"])
                    if st.button("Update Payment Status"):
                        for session in week["sessions"]:
                            if session["session_number"] == session_to_edit:
                                if session["payment_status"] != new_payment_status:
                                    if new_payment_status == "Paid":
                                        week["total_paid_amount"] += 120
                                        session["session_paid_amount"] = 120
                                        session["session_outstanding_amount"] = 0
                                    else:
                                        week["total_paid_amount"] -= 120
                                        session["session_paid_amount"] = 0
                                        session["session_outstanding_amount"] = 120
                                    session["payment_status"] = new_payment_status
                                    week["total_outstanding_amount"] = week["amount_per_week"] - week["total_paid_amount"]
                                    update_week_status(week)
                                    save_data(data)
                                    st.success("Payment status updated successfully!")
                                    break

    with col1:
        # Display sessions for each week
        st.header("All Weeks and Sessions")
        for week in data["weeks"]:
            st.markdown(f"""
                <div style="padding: 10px; border-radius: 5px; background-color: #e0f7fa; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); margin-bottom: 10px;">
                    <h4>{week['week_name']} (Start Date: {week['week_start_date']})</h4>
                    <p><b>Status:</b> {week['status']}<br>
                    <b>Total Paid Amount:</b> R{week['total_paid_amount']}<br>
                    <b>Total Outstanding Amount:</b> R{week['total_outstanding_amount']}</p>
                </div>
            """, unsafe_allow_html=True)
            sessions_df = pd.DataFrame(week["sessions"])
            st.table(sessions_df)

elif page == "Dashboard":
    st.title("Dashboard")

    # Calculate statistics
    total_sessions = sum(len(week["sessions"]) for week in data["weeks"])
    total_payments = sum(week['total_paid_amount'] for week in data['weeks'])
    total_outstanding = sum(week['total_outstanding_amount'] for week in data['weeks'])

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
