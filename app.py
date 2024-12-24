from flask import Flask, render_template, request, redirect, url_for
import calendar
from datetime import datetime
import json
import os

app = Flask(__name__)

# データベースファイルのパス
DB_FILE = 'database.json'
COMPLETED_FILE = 'completed.json'  # 完了リスト用の新しいJSONファイル

# データベースを初期化
if not os.path.exists(DB_FILE):
    with open(DB_FILE, 'w') as db:
        json.dump([], db)

# 完了リストを初期化
if not os.path.exists(COMPLETED_FILE):
    with open(COMPLETED_FILE, 'w') as completed:
        json.dump([], completed)

@app.route('/', methods=['GET', 'POST'])
def index():
    # POSTリクエストで年と月を取得する処理を追加
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

    # カレンダーの年・月とスケジュール情報をテンプレートに渡す
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

# 変更点: 日付詳細ページのエンドポイントを追加
@app.route('/detail/<int:year>/<int:month>/<int:day>', methods=['GET', 'POST'])
def detail(year, month, day):
    # データベースからスケジュールを読み込む
    with open(DB_FILE, 'r') as db:
        schedules = json.load(db)

    # 完了リストを読み込む
    with open(COMPLETED_FILE, 'r') as completed:
        completed_schedules = json.load(completed)

    # POSTリクエストでスケジュールの状態変更または削除処理を追加
    if request.method == 'POST':
        action = request.form['action']  # フォームからアクションタイプを取得
        title = request.form['title']  # スケジュールのタイトルを取得
        if action == 'complete':
            # 完了リストに移動
            for schedule in schedules:
                if schedule['title'] == title:
                    completed_schedules.append(schedule)
                    schedules.remove(schedule)
                    break
        elif action == 'uncomplete':
            # 完了リストから元に戻す
            for schedule in completed_schedules:
                if schedule['title'] == title:
                    schedules.append(schedule)
                    completed_schedules.remove(schedule)
                    break
        elif action == 'delete':
            # スケジュールを削除
            schedules = [schedule for schedule in schedules if schedule['title'] != title]
            completed_schedules = [schedule for schedule in completed_schedules if schedule['title'] != title]

        # 更新されたスケジュールをデータベースに保存
        with open(DB_FILE, 'w') as db:
            json.dump(schedules, db, indent=4, ensure_ascii=False)
        with open(COMPLETED_FILE, 'w') as completed:
            json.dump(completed_schedules, completed, indent=4, ensure_ascii=False)

        # 同じ詳細ページにリダイレクトして更新を反映
        return redirect(url_for('detail', year=year, month=month, day=day))

    # 指定された日付に一致するスケジュールを抽出
    selected_date = f"{year}-{month:02d}-{day:02d}"
    filtered_schedules = [
        schedule for schedule in schedules
        if schedule['start_date'] <= selected_date <= schedule['end_date']
    ]

    # 完了したスケジュールのうち、選択された日付に一致するものを抽出
    filtered_completed_schedules = [
        schedule for schedule in completed_schedules
        if schedule['start_date'] <= selected_date <= schedule['end_date']
    ]

    return render_template(
        'detail.html',
        year=year,
        month=month,
        day=day,
        schedules=filtered_schedules,
        completed_schedules=filtered_completed_schedules
    )

# 完了したスケジュールページを追加
@app.route('/completed_schedules', methods=['GET', 'POST'])
def completed_schedules():
    # 完了したスケジュールを読み込む
    with open(COMPLETED_FILE, 'r') as completed:
        completed_schedules = json.load(completed)

    # POSTリクエストが送られた場合の処理を追加
    if request.method == 'POST':
        title_to_restore = request.form['title']  # 元に戻す対象のスケジュールタイトルを取得

        # completed.jsonから該当スケジュールを削除
        schedule_to_restore = None
        for schedule in completed_schedules:
            if schedule['title'] == title_to_restore:
                schedule_to_restore = schedule
                completed_schedules.remove(schedule)
                break

        # database.jsonに追加
        if schedule_to_restore:
            with open(DB_FILE, 'r') as db:
                schedules = json.load(db)
            schedules.append(schedule_to_restore)
            with open(DB_FILE, 'w') as db:
                json.dump(schedules, db, indent=4, ensure_ascii=False)

        # 完了スケジュールファイルを更新
        with open(COMPLETED_FILE, 'w') as completed:
            json.dump(completed_schedules, completed, indent=4, ensure_ascii=False)

        # 完了スケジュールページにリダイレクト
        return redirect(url_for('completed_schedules'))

    # 完了スケジュールページを表示
    return render_template('completed_schedules.html', completed_schedules=completed_schedules)



if __name__ == '__main__':
    # デバッグモードでFlaskアプリケーションを実行
    app.run(debug=True,port=25565)
