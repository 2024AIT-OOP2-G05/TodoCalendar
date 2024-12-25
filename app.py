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

@app.route('/', methods=['GET', 'POST'])
def index():
    # POSTリクエストで年と月を取得する処理を追加
    # 変更点: 年と月を選択するフォームからのデータを取得しカレンダーを動的に更新
    if request.method == 'POST':
        year = int(request.form['year'])  # ユーザーが選択した年を取得
        month = int(request.form['month'])  # ユーザーが選択した月を取得
    else:
        # 初回アクセス時またはGETリクエスト時には現在の年と月を表示
        now = datetime.now()
        year = now.year
        month = now.month

    # カレンダーを作成
    cal = calendar.Calendar(firstweekday=6)  # 日曜日を週の開始日に設定
    month_days = cal.monthdayscalendar(year, month)  # 月間のカレンダー構造を取得

    # データベースからスケジュールを読み込む
    with open(DB_FILE, 'r') as db:
        schedules = json.load(db)

    # 変更点: カレンダーの年・月とスケジュール情報をテンプレートに渡す
    return render_template('calendar.html', year=year, month=month, month_days=month_days, schedules=schedules)

@app.route('/add_schedule', methods=['GET', 'POST'])
def add_schedule():
    if request.method == 'POST':
        # スケジュールデータをフォームから取得
        title = request.form['title']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        details = request.form['details']

        # データベースから現在のスケジュールを読み込む
        with open(DB_FILE, 'r') as db:
            schedules = json.load(db)

        # 新しいスケジュールをリストに追加
        schedules.append({
            'title': title,
            'start_date': start_date,
            'end_date': end_date,
            'details': details
        })

        # 更新されたスケジュールをデータベースに保存
        with open(DB_FILE, 'w') as db:
            json.dump(schedules, db, indent=4, ensure_ascii=False)

        # カレンダー表示にリダイレクト
        return redirect(url_for('index'))

    return render_template('add_schedule.html')

@app.route('/view_schedules')
def view_schedules():
    # スケジュールを読み込む
    with open(DB_FILE, 'r') as db:
        schedules = json.load(db)

    # スケジュール確認ページを表示
    return render_template('view_schedules.html', schedules=schedules)

if __name__ == '__main__':
    # デバッグモードでFlaskアプリケーションを実行
    app.run(debug=True)
