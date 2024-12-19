from flask import Flask, render_template, request
import calendar
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    # 現在の年と月を取得
    if request.method == 'POST':
        year = int(request.form['year'])
        month = int(request.form['month'])

    else:
        now = datetime.now()
        year = now.year
        month = now.month

    # カレンダーを作成
    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)

    return render_template('calendar.html', year=year, month=month, month_days=month_days)

if __name__ == '__main__':
    app.run(debug=True)