from datetime import datetime, timedelta
import streamlit as st

# === Helper Functions ===
def parse_date(date_str):
    return datetime.strptime(date_str, '%d-%m-%Y').date()

def working_days(start, end):
    delta = end - start
    days = [start + timedelta(days=i) for i in range(delta.days + 1)]
    return len([day for day in days if day.weekday() != 4])  # 4 = Friday

def add_working_days(start, num_days):
    current = start
    added = 0
    while added < num_days:
        if current.weekday() != 4:
            added += 1
        if added < num_days:
            current += timedelta(days=1)
    return current

def calculate_labor_estimation(start_date, today_date, original_duration, total_labor, progress, required_end_date):
    elapsed_days = working_days(start_date, today_date)
    progress_rate = (progress / 100) / elapsed_days if elapsed_days > 0 else 0
    estimated_total_duration = max(int(round(1 / progress_rate)), 1) if progress_rate > 0 else 0

    predicted_finish = add_working_days(start_date, estimated_total_duration)
    predicted_duration = working_days(start_date, predicted_finish)

    delay = predicted_duration - original_duration

    remaining_work = 1 - (progress / 100)
    tomorrow = today_date + timedelta(days=1)
    remaining_duration = working_days(tomorrow, predicted_finish)

    remaining_labor = total_labor * remaining_work
    labor_per_day = remaining_labor / remaining_duration if remaining_duration > 0 else 0

    # Labor needed to meet required end date (if provided)
    labor_needed_for_target = None
    remaining_days_user_target = None
    if required_end_date:
        remaining_days_user_target = working_days(tomorrow, required_end_date)
        labor_needed_for_target = remaining_labor / remaining_days_user_target if remaining_days_user_target > 0 else 0

    # Labor needed to finish by original duration
    original_finish_date = add_working_days(start_date, original_duration)
    remaining_days_for_original_plan = working_days(tomorrow, original_finish_date)
    labor_needed_for_original = remaining_labor / remaining_days_for_original_plan if remaining_days_for_original_plan > 0 else 0

    return {
        "Predicted Finish Date": predicted_finish.strftime('%d-%m-%Y'),
        "Predicted Duration (Working Days)": predicted_duration,
        "Delay (Working Days)": delay,
        "Elapsed Working Days": elapsed_days,
        "Progress Rate Per Day": round(progress_rate, 4),
        "Estimated Total Duration": estimated_total_duration,
        "Remaining Duration": remaining_duration,
        "Remaining Labor": round(remaining_labor, 2),
        "Labor Needed Per Day": round(labor_per_day, 2),
        "Required Finish Date": required_end_date.strftime('%d-%m-%Y') if required_end_date else "N/A",
        "Working Days to Required Finish": remaining_days_user_target,
        "Labor Needed to Meet Target Date": round(labor_needed_for_target, 2) if labor_needed_for_target is not None else "N/A",
        "Labor Needed to Finish by Original Duration": round(labor_needed_for_original, 2)
    }

# === Streamlit Interface ===
st.title("Labor Estimation Tool")

with st.form("input_form"):
    start_date = st.text_input("Start Date (DD-MM-YYYY)")
    today_date = st.text_input("Today's Date (DD-MM-YYYY)")
    original_duration = st.number_input("Original Duration (in working days)", min_value=1)
    total_labor = st.number_input("Total Labor Assigned to Activity", min_value=1)
    progress = st.number_input("📈 Progress (%)", min_value=0.0, max_value=100.0, step=0.1)
    required_end_date_str = st.text_input("Required Finish Date (DD-MM-YYYY) (Optional)", value="")
    submitted = st.form_submit_button("Calculate")

if submitted:
    try:
        start = parse_date(start_date)
        today = parse_date(today_date)
        required_end_date = parse_date(required_end_date_str) if required_end_date_str else None

        results = calculate_labor_estimation(
            start, today, original_duration, total_labor, progress, required_end_date
        )

        st.subheader("Results")
        for k, v in results.items():
            st.write(f"**{k}:** {v}")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
