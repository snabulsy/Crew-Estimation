from datetime import datetime, timedelta
import streamlit as st

# === Helper Functions ===

def parse_date(date_str):
    """Parse date from string in format DD-MM-YYYY"""
    return datetime.strptime(date_str, '%d-%m-%Y').date()

def working_days(start, end):
    """Count working days excluding Fridays (weekday 4), inclusive"""
    delta = end - start
    days = [start + timedelta(days=i) for i in range(delta.days + 1)]
    return len([day for day in days if day.weekday() != 4])  # 4 = Friday

def add_working_days(start, num_days):
    """Add working days (excluding Fridays) to a start date"""
    current = start
    added = 0
    while added < num_days:
        current += timedelta(days=1)
        if current.weekday() != 4:
            added += 1
    return current

def calculate_crew_estimation(start_date, today_date, original_duration, total_crew, progress):
    elapsed_days = working_days(start_date, today_date)

    # If progress or elapsed days are 0 → handle edge case
    if progress <= 0 or elapsed_days <= 0:
        return {
            "Predicted Finish Date": "N/A",
            "Predicted Duration": 0,
            "Delay": 0,
            "Elapsed Days": elapsed_days,
            "Progress Rate": 0,
            "Estimated Total Duration": 0,
            "Remaining Duration": 0,
            "Remaining Crew": total_crew,
            "Crew Needed Per Day": 0
        }

    # Estimate based on progress so far
    progress_rate = progress / 100 / elapsed_days
    estimated_total_duration = max(int(1 / progress_rate), 1)
    remaining_duration = max(estimated_total_duration - elapsed_days, 1)

    predicted_finish = add_working_days(today_date, remaining_duration)
    predicted_duration = working_days(start_date, predicted_finish)
    delay = predicted_duration - original_duration

    remaining_crew = total_crew * (1 - progress / 100)
    crew_per_day = remaining_crew / remaining_duration

    return {
        "Predicted Finish Date": predicted_finish.strftime('%d-%m-%Y'),
        "Predicted Duration": predicted_duration,
        "Delay": delay,
        "Elapsed Days": elapsed_days,
        "Progress Rate": round(progress_rate, 4),
        "Estimated Total Duration": estimated_total_duration,
        "Remaining Duration": remaining_duration,
        "Remaining Crew": round(remaining_crew, 2),
        "Crew Needed Per Day": round(crew_per_day, 2)
    }

# === Streamlit Interface ===

st.title("Crew Estimation Web Calculator 👷‍♂️")

with st.form("input_form"):
    st.markdown("### Input Project Data")
    start_date = st.text_input("Start Date (DD-MM-YYYY)", placeholder="e.g. 20-07-2025")
    today_date = st.text_input("Today's Date (DD-MM-YYYY)", placeholder="e.g. 24-07-2025")
    original_duration = st.number_input("Original Duration (in days)", min_value=1)
    total_crew = st.number_input("Total Crew for Activity", min_value=1)
    progress = st.number_input("Progress (%)", min_value=0.0, max_value=100.0, step=0.1)
    submitted = st.form_submit_button("Calculate")

if submitted:
    try:
        start = parse_date(start_date)
        today = parse_date(today_date)
        results = calculate_crew_estimation(start, today, original_duration, total_crew, progress)

        st.subheader("📊 Results")
        for k, v in results.items():
            st.write(f"**{k}:** {v}")
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")
