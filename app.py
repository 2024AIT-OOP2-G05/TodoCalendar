from flask import Flask, render_template, request, redirect, url_for
import calendar
from datetime import datetime
import json
import os
import uuid

app = Flask(__name__)

DB_FILE = 'database.json'

if not os.path.exists(DB_FILE):
    with open(DB_FILE, 'w') as db:
        json.dump([], db)

@app.route('/')
def index():
    now = datetime.now()
    year = now.year
    month = now.month

    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)

    with open(DB_FILE, 'r') as db:
        schedules = json.load(db)
    return render_template('calendar.html', year=year, month=month, month_days=month_days, schedules=schedules)

@app.route('/detail/<int:year>/<int:month>/<int:day>')
def detail(year, month, day):
    with open(DB_FILE, 'r') as db:
        schedules = json.load(db)
    target_date = datetime(year, month, day)

    filtered_schedules = []
    for schedule in schedules:
        start = datetime.strptime(schedule['start_date'], "%Y-%m-%d")
        end = datetime.strptime(schedule['end_date'], "%Y-%m-%d")
        if start <= target_date <= end:
            filtered_schedules.append(schedule)

    # completedがFalseのものとTrueのものを分ける
    incomplete_schedules = [s for s in filtered_schedules if not s.get('completed', False)]
    completed_schedules = [s for s in filtered_schedules if s.get('completed', False)]

    return render_template('detail.html', year=year, month=month, day=day,
                           incomplete_schedules=incomplete_schedules,
                           completed_schedules=completed_schedules)

@app.route('/add_schedule', methods=['GET', 'POST'])
def add_schedule():
    if request.method == 'POST':
        title = request.form['title']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        details = request.form['details']

        with open(DB_FILE, 'r') as db:
            schedules = json.load(db)

        schedules.append({
            'id': uuid.uuid4().hex,  # 一意のIDを付与
            'title': title,
            'start_date': start_date,
            'end_date': end_date,
            'details': details,
            'completed': False
        })

        with open(DB_FILE, 'w') as db:
            json.dump(schedules, db, indent=4, ensure_ascii=False)

        return redirect(url_for('index'))

    return render_template('add_schedule.html')

@app.route('/view_schedules')
def view_schedules():
    with open(DB_FILE, 'r') as db:
        schedules = json.load(db)
    return render_template('view_schedules.html', schedules=schedules)

@app.route('/complete_schedule', methods=['POST'])
def complete_schedule():
    sched_id = request.form.get('id')
    year = request.form.get('year')
    month = request.form.get('month')
    day = request.form.get('day')

    with open(DB_FILE, 'r') as db:
        schedules = json.load(db)

    for s in schedules:
        if s['id'] == sched_id:
            s['completed'] = True
            break

    with open(DB_FILE, 'w') as db:
        json.dump(schedules, db, indent=4, ensure_ascii=False)

    return redirect(url_for('detail', year=year, month=month, day=day))

@app.route('/delete_schedule', methods=['POST'])
def delete_schedule():
    sched_id = request.form.get('id')
    year = request.form.get('year')
    month = request.form.get('month')
    day = request.form.get('day')

    with open(DB_FILE, 'r') as db:
        schedules = json.load(db)

    schedules = [s for s in schedules if s['id'] != sched_id]

    with open(DB_FILE, 'w') as db:
        json.dump(schedules, db, indent=4, ensure_ascii=False)

    return redirect(url_for('detail', year=year, month=month, day=day))

if __name__ == '__main__':

    app.run(debug=True, port=11111)
