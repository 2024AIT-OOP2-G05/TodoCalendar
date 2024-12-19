from flask import Flask, render_template, request, redirect, url_for
import calendar
from datetime import datetime
import json
import os

app = Flask(__name__)

# データベースファイルのパス
DB_FILE = 'database.json'

# データベースを初期化
if not os.path.exists(DB_FILE):
    with open(DB_FILE, 'w') as db:
        json.dump([], db)

@app.route('/')
def index():
    # 現在の年と月を取得
    now = datetime.now()
    year = now.year
    month = now.month

    # カレンダーを作成
    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)

    # スケジュールを読み込み
    with open(DB_FILE, 'r') as db:
        schedules = json.load(db)

    return render_template('calendar.html', year=year, month=month, month_days=month_days, schedules=schedules)

@app.route('/add_schedule', methods=['GET', 'POST'])
def add_schedule():
    if request.method == 'POST':
        # フォームからデータを取得
        title = request.form['title']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        details = request.form['details']

        # スケジュールを保存
        with open(DB_FILE, 'r') as db:
            schedules = json.load(db)
        schedules.append({
            'title': title,
            'start_date': start_date,
            'end_date': end_date,
            'details': details
        })
        with open(DB_FILE, 'w') as db:
            json.dump(schedules, db)

        return redirect(url_for('index'))

    return render_template('add_schedule.html')

@app.route('/view_schedules')
def view_schedules():
    # スケジュールを読み込み
    with open(DB_FILE, 'r') as db:
        schedules = json.load(db)

    return render_template('view_schedules.html', schedules=schedules)

if __name__ == '__main__':
    app.run(debug=True)
