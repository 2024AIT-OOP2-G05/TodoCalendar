@app.route('/view_schedules')
def view_schedules():
    # スケジュールを読み込む
    with open(DB_FILE, 'r') as db:
        schedules = json.load(db)

    # スケジュール確認ページを表示
    return render_template('view_schedules.html', schedules=schedules)