from datetime import datetime, timedelta
import streamlit as st

# === Helper Functions ===

def parse_date(date_str):
    """Convert string to date object"""
    return datetime.strptime(date_str, '%d-%m-%Y').date()

def working_days(start, end):
    """Return number of working days between start and end (inclusive), excluding Fridays"""
    delta = end - start
    days = [start + timedelta(days=i) for i in range(delta.days + 1)]
    return len([day for day in days if day.weekday() != 4])  # 4 = Friday

def add_working_days(start, num_days):
    """Add a number of working days (excluding Fridays) to a start date"""
    current = start
    added = 0
    while added < num_days:
        if current.weekday() != 4:
            added += 1
        if added < num_days:
            current += timedelta(days=1)
    return current

def calculate_crew_estimation(start_date, today_date, original_duration, total_crew, progress):
    elapsed_days = working_days(start_date, today_date)

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

    # Estimate how long full task will take
    progress_rate = (progress / 100) / elapsed_days
    estimated_total_duration = max(int(1 / progress_rate), 1)

    # Predict finish date from start
    predicted_finish = add_working_days(start_date, estimated_total_duration - 1)

    # Delay calculation
    predicted_duration = working_days(start_date, predicted_finish)
    delay = predicted_duration - original_duration

    # Remaining duration starts after today
    tomorrow = today_date + timedelta(days=1)
    remaining_duration = working_days(tomorrow, predicted_finish)

    remaining_crew = total_crew * (1 - progress / 100)
    crew_per_day = remaining_crew / remaining_duration if remaining_duration > 0 else 0

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

# === Streamlit UI ===

st.set_page_config(page_title="Crew Estimation Tool", layout="centered")
st.title("👷‍♂️ Crew Estimation Web Tool")

with st.form("crew_form"):
    st.markdown("### Enter Activity Data")
    start_date = st.text_input("Start Date (DD-MM-YYYY)", placeholder="e.g. 20-07-2025")
    today_date = st.text_input("Today's Date (DD-MM-YYYY)", placeholder="e.g. 24-07-2025")
    original_duration = st.number_input("Original Planned Duration (working days)", min_value=1)
    total_crew = st.number_input("Total Assigned Crew", min_value=1)
    progress = st.number_input("Progress Done (%)", min_value=0.0, max_value=100.0, step=0.1)
    submitted = st.form_submit_button("Calculate")

if submitted:
    try:
        start = parse_date(start_date)
        today = parse_date(today_date)
        if today < start:
            st.error("Today's date cannot be before the start date.")
        else:
            results = calculate_crew_estimation(start, today, original_duration, total_crew, progress)
            st.subheader("📊 Estimation Results")
            for key, value in results.items():
                st.markdown(f"**{key}:** {value}")
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")
