from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import os
from datetime import datetime

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"

# Path for the CSV file
CSV_FILE = "data.csv"

# Ensure the CSV file exists
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w") as f:
        f.write("date,water_intake,sleep_hours,activity_hours\n")

# Home/Dashboard Route
@app.route("/")
def home():
    return render_template("dashboard.html")

# Helper function to get monthly data
def get_monthly_data(df, column_name, selected_month=None, selected_year=None):
    # Convert 'date' to datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df['week'] = df['date'].dt.isocalendar().week
    df['day_of_week'] = df['date'].dt.dayofweek

    # Default to current month and year if no selection is made
    today = datetime.now()
    if not selected_month:
        selected_month = today.month
    if not selected_year:
        selected_year = today.year

    # Filter data for the selected month and year
    filtered_df = df[(df['month'] == selected_month) & (df['year'] == selected_year)]

    # Initialize values for Sunday-Saturday
    days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    weekly_values = [0] * 7

    for _, row in filtered_df.iterrows():
        day = (row['day_of_week'] + 1) % 7  # Adjust to start from Sunday
        if not pd.isnull(row[column_name]):
            weekly_values[day] += row[column_name]

    return days, weekly_values

# Dropdown options for months and years
def generate_month_options():
    return [{"month": i, "label": datetime(2024, i, 1).strftime('%B')} for i in range(1, 13)]

def generate_year_options(df):
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    years = df['date'].dt.year.dropna().unique()
    return sorted(years)

# Routes for Water Intake
@app.route("/water", methods=["GET"])
def water():
    df = pd.read_csv(CSV_FILE)

    # Get selected month and year from dropdown or default to current
    selected_month = request.args.get("month", type=int)
    selected_year = request.args.get("year", type=int)

    days, water_values = get_monthly_data(df, 'water_intake', selected_month, selected_year)
    month_options = generate_month_options()
    year_options = generate_year_options(df)

    return render_template("water.html", days=days, values=water_values, month_options=month_options,
                           year_options=year_options, selected_month=selected_month, selected_year=selected_year)

@app.route("/add_water", methods=["POST"])
def add_water():
    date = request.form["date"]
    amount = request.form["amount"]

    df = pd.read_csv(CSV_FILE)
    new_record = pd.DataFrame([{
        "date": date,
        "water_intake": float(amount),
        "sleep_hours": None,
        "activity_hours": None
    }])

    df = pd.concat([df, new_record], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

    flash("Water intake added successfully!", "success")
    return redirect(url_for("water"))

# Sleep Hours Routes
@app.route("/sleep", methods=["GET"])
def sleep():
    df = pd.read_csv(CSV_FILE)

    selected_month = request.args.get("month", type=int)
    selected_year = request.args.get("year", type=int)

    days, sleep_values = get_monthly_data(df, 'sleep_hours', selected_month, selected_year)
    month_options = generate_month_options()
    year_options = generate_year_options(df)

    return render_template("sleep.html", days=days, values=sleep_values, month_options=month_options,
                           year_options=year_options, selected_month=selected_month, selected_year=selected_year)

@app.route("/add_sleep", methods=["POST"])
def add_sleep():
    date = request.form["date"]
    hours = request.form["hours"]

    df = pd.read_csv(CSV_FILE)
    new_record = pd.DataFrame([{
        "date": date,
        "water_intake": None,
        "sleep_hours": float(hours),
        "activity_hours": None
    }])

    df = pd.concat([df, new_record], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

    flash("Sleep hours added successfully!", "success")
    return redirect(url_for("sleep"))

# Activity Hours Routes
@app.route("/activity", methods=["GET"])
def activity():
    df = pd.read_csv(CSV_FILE)

    selected_month = request.args.get("month", type=int)
    selected_year = request.args.get("year", type=int)

    days, activity_values = get_monthly_data(df, 'activity_hours', selected_month, selected_year)
    month_options = generate_month_options()
    year_options = generate_year_options(df)

    return render_template("activity.html", days=days, values=activity_values, month_options=month_options,
                           year_options=year_options, selected_month=selected_month, selected_year=selected_year)

@app.route("/add_activity", methods=["POST"])
def add_activity():
    date = request.form["date"]
    hours = request.form["hours"]

    df = pd.read_csv(CSV_FILE)
    new_record = pd.DataFrame([{
        "date": date,
        "water_intake": None,
        "sleep_hours": None,
        "activity_hours": float(hours)
    }])

    df = pd.concat([df, new_record], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

    flash("Activity hours added successfully!", "success")
    return redirect(url_for("activity"))

if __name__ == "__main__":
    app.run(debug=True)

