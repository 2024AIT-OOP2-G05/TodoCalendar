from flask import Flask, render_template
import calendar
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    # 現在の年と月を取得
    now = datetime.now()
    year = now.year
    month = now.month

    # カレンダーを作成
    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)

    return render_template('calendar.html', year=year, month=month, month_days=month_days)

@app.route('/detail/<int:year>/<int:month>/<int:day>')
def detail(year, month, day):
    # ここでdayに紐づく詳細情報を取得して表示する処理を書く
    # とりあえず、デモとして日付を表示するだけ
    return render_template('detail.html', year=year, month=month, day=day)

if __name__ == '__main__':
    app.run(debug=True)
