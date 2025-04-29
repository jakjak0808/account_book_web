from flask import Flask, render_template, request, redirect, session
import os
import json
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATA_FILE = 'data/accountbook.json'
CURRENCIES_FILE = 'data/currencies.json'
PURCHASE_PLAN_FILE = 'data/purchase_plan.json'

# 🚀 Frankfurter API 기반 환율 가져오기 함수
def get_exchange_rate(base_currency):
    url = f"https://api.frankfurter.app/latest?from={base_currency}&to=THB"
    try:
        response = requests.get(url)
        data = response.json()
        if 'rates' not in data or 'THB' not in data['rates']:
            print(f"환율 가져오기 실패: {base_currency} ➔ THB 변환 불가")
            return None
        rate = data['rates']['THB']
        return rate
    except Exception as e:
        print("환율 가져오기 오류:", e)
        return None

@app.route('/')
def loading():
    return render_template('loading.html')

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        code = request.form.get('code')
        if code == '0620':
            session['authenticated'] = True
            next_page = session.pop('next_page', '/index')
            return redirect(next_page)
        else:
            return render_template('auth.html', error='인증번호가 틀렸습니다.')
    return render_template('auth.html')
# 기록 추가 페이지
@app.route('/add', methods=['GET', 'POST'])
def add_record():
    if request.method == 'POST':
        # 폼에서 받은 데이터 처리
        title = request.form['title']
        amount = request.form['amount']
        entry_type = request.form['type']
        
        # 현재 날짜 자동 설정 (서버에서 처리)
        date = datetime.today().strftime('%Y-%m-%d')  # 현재 날짜를 자동으로 설정

        # 데이터 파일에 저장하는 로직
        new_record = {
            'title': title,
            'amount': float(amount),
            'type': entry_type,
            'date': date  # 현재 날짜 저장
        }

        # 기존 기록 불러오기
        records = []
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                records = json.load(f)

        records.append(new_record)

        # 기록을 data.json 파일에 저장
        with open(DATA_FILE, 'w') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

        return redirect('/index')  # 메인 페이지로 리디렉션

    return render_template('add.html')  # GET 요청 시 add.html 폼을 보여줌
# 기록 저장
@app.route('/save', methods=['POST'])
def save_record():
    # 폼에서 데이터를 받아옵니다. 값이 없을 경우 빈 문자열을 반환
    date = request.form.get('date', '').strip()

    # date가 비어있다면 현재 날짜를 자동으로 설정
    if not date:
        date = datetime.today().strftime('%Y-%m-%d')  # 오늘 날짜로 설정

    entry_type = request.form.get('type', '').strip()
    amount = request.form.get('amount', '').strip()
    title = request.form.get('title', '').strip()

    # 데이터가 유효한지 확인
    if not date or not entry_type or not amount or not title:
        print(f"Received data: date={date}, entry_type={entry_type}, amount={amount}, title={title}")  # 디버깅
        return "모든 필드를 채워주세요!", 400  # 필수 항목이 빠졌으면 오류 반환

    try:
        amount = float(amount)  # 금액은 숫자로 변환
    except ValueError:
        return "금액이 잘못되었습니다.", 400  # 금액이 잘못된 형식일 경우 오류 반환

    # 새 기록 추가
    new_record = {
        'date': date,
        'type': entry_type,
        'amount': amount,
        'title': title
    }

    # 기존 기록 불러오기
    records = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            records = json.load(f)

    # 새 기록 추가
    records.append(new_record)

    # 기록을 파일에 저장
    with open(DATA_FILE, 'w') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    # 기록을 저장한 후 메인 페이지로 리디렉션
    return redirect('/index')

@app.route('/index')
def index():
    if not session.get('authenticated'):
        session['next_page'] = '/index'
        return redirect('/auth')

    balance = 0
    today_income = 0
    today_expense = 0
    month_income = 0
    month_expense = 0
    compare_text = "오늘 지출 데이터 없음"
    month_compare_text = "이번달 지출 데이터 없음"

    today = datetime.today().strftime('%Y-%m-%d')
    month = datetime.today().strftime('%Y-%m')

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)

        for entry in data:
            entry_date = entry.get('date', '')
            entry_type = entry.get('type')
            amount = entry.get('amount', 0)

            # entry_date가 None이 아니거나 빈 문자열이 아닌지 확인
            if entry_date:
                if entry_type == '수입':
                    balance += amount
                elif entry_type == '지출':
                    balance -= amount

                if entry_date == today:
                    if entry_type == '수입':
                        today_income += amount
                    elif entry_type == '지출':
                        today_expense += amount

                if entry_date.startswith(month):
                    if entry_type == '수입':
                        month_income += amount
                    elif entry_type == '지출':
                        month_expense += amount

        if today_income or today_expense:
            compare_text = "오늘은 수입보다 지출이 많습니다." if today_expense > today_income else "오늘은 지출보다 수입이 많습니다."
        if month_income or month_expense:
            month_compare_text = "이번달은 수입보다 지출이 많습니다." if month_expense > month_income else "이번달은 지출보다 수입이 많습니다."

    currencies = []
    if os.path.exists(CURRENCIES_FILE):
        with open(CURRENCIES_FILE, 'r') as f:
            currencies = json.load(f)

        for currency in currencies:
            rate = get_exchange_rate(currency['name'])
            if rate:
                try:
                    amount_in_thb = float(currency['amount']) * rate
                    currency['amount_thb'] = f"{amount_in_thb:,.2f}"
                except Exception as e:
                    print(f"{currency['name']} 변환 오류:", e)
                    currency['amount_thb'] = "변환 오류"
            else:
                currency['amount_thb'] = "환율 없음"

    return render_template(
        'index.html',
        balance=balance,
        today_income=today_income,
        today_expense=today_expense,
        month_income=month_income,
        month_expense=month_expense,
        compare_text=compare_text,
        month_compare_text=month_compare_text,
        currencies=currencies
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/auth')

# 🔥 검색 기능
@app.route('/search', methods=['GET'])
def search():
    if not session.get('authenticated'):
        session['next_page'] = '/search'
        return redirect('/auth')

    keyword = request.args.get('keyword', '')
    results = []

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        results = [entry for entry in data if keyword.lower() in entry.get('title', '').lower()]

    return render_template('search_results.html', keyword=keyword, results=results)

# 🔥 구매 계획 추가 페이지
@app.route('/purchase_plan')
def purchase_plan():
    if not session.get('authenticated'):
        session['next_page'] = '/purchase_plan'
        return redirect('/auth')
    return render_template('purchase_plan.html')

# 🔥 구매 계획 저장
@app.route('/save_purchase_plan', methods=['POST'])
def save_purchase_plan():
    if not session.get('authenticated'):
        session['next_page'] = '/save_purchase_plan'
        return redirect('/auth')

    item = request.form.get('item')
    purpose = request.form.get('purpose')
    online_price = request.form.get('online_price')
    offline_a = request.form.get('offline_a')
    offline_b = request.form.get('offline_b')

    new_plan = {
        'item': item,
        'purpose': purpose,
        'online_price': online_price,
        'offline_a': offline_a,
        'offline_b': offline_b,
        'status': '구매 대기'
    }

    plans = []
    if os.path.exists(PURCHASE_PLAN_FILE):
        with open(PURCHASE_PLAN_FILE, 'r') as f:
            plans = json.load(f)

    plans.append(new_plan)

    with open(PURCHASE_PLAN_FILE, 'w') as f:
        json.dump(plans, f, ensure_ascii=False, indent=2)

    return redirect('/purchase_list')

# 🔥 구매 계획 리스트 보기
@app.route('/purchase_list')
def purchase_list():
    if not session.get('authenticated'):
        session['next_page'] = '/purchase_list'
        return redirect('/auth')

    plans = []
    if os.path.exists(PURCHASE_PLAN_FILE):
        with open(PURCHASE_PLAN_FILE, 'r') as f:
            plans = json.load(f)

    return render_template('purchase_list.html', plans=plans)

# 🔥 통계 페이지
@app.route('/stats')
def stats():
    if not session.get('authenticated'):
        session['next_page'] = '/stats'
        return redirect('/auth')

    months = ["1월", "2월", "3월", "4월", "5월", "6월",
              "7월", "8월", "9월", "10월", "11월", "12월"]
    income_data = [0] * 12
    expense_data = [0] * 12

    income_types = []
    expense_types = []
    income_type_data = []
    expense_type_data = []

    days = []
    daily_income_data = []
    daily_expense_data = []

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)

        today = datetime.today()
        last_30_days = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(29, -1, -1)]
        days = [d[5:] for d in last_30_days]  # MM-DD 포맷

        income_daily_map = {day: 0 for day in last_30_days}
        expense_daily_map = {day: 0 for day in last_30_days}

        income_type_map = {}
        expense_type_map = {}

        for entry in data:
            entry_date = entry.get('date', '')
            entry_type = entry.get('type')
            title = entry.get('title', '')
            amount = entry.get('amount', 0)

            if not entry_date:
                continue

            date_obj = datetime.strptime(entry_date, '%Y-%m-%d')
            month_idx = date_obj.month - 1

            if entry_type == '수입':
                income_data[month_idx] += amount
                if title:
                    income_type_map[title] = income_type_map.get(title, 0) + amount
            elif entry_type == '지출':
                expense_data[month_idx] += amount
                if title:
                    expense_type_map[title] = expense_type_map.get(title, 0) + amount

            if entry_date in last_30_days:
                if entry_type == '수입':
                    income_daily_map[entry_date] += amount
                elif entry_type == '지출':
                    expense_daily_map[entry_date] += amount

        income_types = list(income_type_map.keys())
        expense_types = list(expense_type_map.keys())
        income_type_data = list(income_type_map.values())
        expense_type_data = list(expense_type_map.values())
        daily_income_data = list(income_daily_map.values())
        daily_expense_data = list(expense_daily_map.values())

    return render_template(
        'stats.html',
        months=months,
        income_data=income_data,
        expense_data=expense_data,
        income_types=income_types,
        expense_types=expense_types,
        income_type_data=income_type_data,
        expense_type_data=expense_type_data,
        days=days,
        daily_income_data=daily_income_data,
        daily_expense_data=daily_expense_data
    )
@app.route('/update_purchase_plan', methods=['POST'])
def update_purchase_plan():
    if not session.get('authenticated'):
        session['next_page'] = '/purchase_list'
        return redirect('/auth')

    index = int(request.form.get('index'))
    product = request.form.get('product')
    purpose = request.form.get('purpose')
    online_price = request.form.get('online_price')
    amart_name = request.form.get('amart_name')
    amart_price = request.form.get('amart_price')
    bmart_name = request.form.get('bmart_name')
    bmart_price = request.form.get('bmart_price')
    other_price = request.form.get('other_price')

    # 추가 매장 데이터 받기
    extra_store_names = request.form.getlist('extra_store_name[]')
    extra_store_prices = request.form.getlist('extra_store_price[]')

    plans = []
    if os.path.exists(PURCHASE_PLAN_FILE):
        with open(PURCHASE_PLAN_FILE, 'r') as f:
            plans = json.load(f)

    if 0 <= index < len(plans):
        plans[index]['product'] = product
        plans[index]['purpose'] = purpose
        plans[index]['online_price'] = online_price
        plans[index]['amart_name'] = amart_name
        plans[index]['amart_price'] = amart_price
        plans[index]['bmart_name'] = bmart_name
        plans[index]['bmart_price'] = bmart_price
        plans[index]['other_price'] = other_price

        # 추가 매장 리스트 저장
        extra_stores = []
        for name, price in zip(extra_store_names, extra_store_prices):
            extra_stores.append({'store_name': name, 'store_price': price})

        plans[index]['extra_stores'] = extra_stores

        with open(PURCHASE_PLAN_FILE, 'w') as f:
            json.dump(plans, f, ensure_ascii=False, indent=2)

    return redirect('/purchase_list')
@app.route('/edit_purchase_plan/<int:index>')
def edit_purchase_plan(index):
    if not session.get('authenticated'):
        session['next_page'] = f'/edit_purchase_plan/{index}'
        return redirect('/auth')

    plans = []
    if os.path.exists(PURCHASE_PLAN_FILE):
        with open(PURCHASE_PLAN_FILE, 'r') as f:
            plans = json.load(f)

    if 0 <= index < len(plans):
        plan = plans[index]
        return render_template('purchase_edit.html', plan=plan, index=index)
    else:
        return redirect('/purchase_list')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
