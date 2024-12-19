from flask import Flask, render_template, request, redirect, url_for
import calendar
from datetime import datetime
import json
import os

# Flask アプリケーションの初期化
app = Flask(__name__)

# データベースファイルのパス
DB_FILE = 'database.json'

# データベースを初期化
if not os.path.exists(DB_FILE):
    with open(DB_FILE, 'w') as db:
        json.dump([], db)

# ルートエンドポイント ('/')：カレンダーを表示
@app.route('/')
def index():
    # 現在の年と月を取得
    now = datetime.now()
    year = now.year
    month = now.month

    # カレンダーを作成
    cal = calendar.Calendar(firstweekday=6)  # 日曜日を週の開始日に設定
    month_days = cal.monthdayscalendar(year, month)  # 月間のカレンダー構造を取得

    # データベースからスケジュールを読み込み
    with open(DB_FILE, 'r') as db:
        schedules = json.load(db)
        # カレンダーの HTML テンプレートをレンダリングし、値を渡す
    return render_template('calendar.html', year=year, month=month, month_days=month_days, schedules=schedules)

@app.route('/detail/<int:year>/<int:month>/<int:day>')
def detail(year, month, day):
    # データベースからスケジュールを読み込む
    with open(DB_FILE, 'r') as db:
        schedules = json.load(db)

    # 対象日をdatetimeオブジェクトに変換
    target_date = datetime(year, month, day)

    # 対象日のスケジュールをフィルタリング
    filtered_schedules = []
    for schedule in schedules:
        start = datetime.strptime(schedule['start_date'], "%Y-%m-%d")
        end = datetime.strptime(schedule['end_date'], "%Y-%m-%d")
        # 開始日 <= 対象日 <= 終了日 であれば対象
        if start <= target_date <= end:
            filtered_schedules.append(schedule)

    # detail.htmlをレンダリングする際にfiltered_schedulesを渡す
    return render_template('detail.html', year=year, month=month, day=day, schedules=filtered_schedules)



# スケジュール追加ページ ('/add_schedule')：スケジュールを追加するフォームを表示し、データを保存
@app.route('/add_schedule', methods=['GET', 'POST'])
def add_schedule():
    if request.method == 'POST':  # POST メソッドでデータが送信された場合
        # フォームからスケジュールデータを取得
        title = request.form['title']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        details = request.form['details']

        # スケジュールを保存
        with open(DB_FILE, 'r') as db:
            schedules = json.load(db)

        # 新しいスケジュールをリストに追加
        schedules.append({
            'title': title,
            'start_date': start_date,
            'end_date': end_date,
            'details': details
        })

        # 更新されたスケジュールリストをデータベースに保存
        with open(DB_FILE, 'w') as db:
            json.dump(schedules, db, indent=4, ensure_ascii=False)


        # カレンダーページにリダイレクト
        return redirect(url_for('index'))

    # GET メソッドの場合、スケジュール追加ページを表示
    return render_template('add_schedule.html')

# スケジュール確認ページ ('/view_schedules')：登録済みのスケジュールを一覧表示
@app.route('/view_schedules')
def view_schedules():
    # スケジュールを読み込み
    with open(DB_FILE, 'r') as db:
        schedules = json.load(db)

    # スケジュール確認ページをレンダリングし、スケジュールリストを渡す
    return render_template('view_schedules.html', schedules=schedules)

if __name__ == '__main__':
    # デバッグモードで Flask アプリケーションを実行
    app.run(debug=True, port=11454)
