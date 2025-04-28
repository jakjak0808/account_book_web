# services/calculation_service.py

def calculate_total_expenses(accountbook):
    return sum(expense.amount for expense in accountbook.expenses)

def calculate_total_incomes(accountbook):
    return sum(income.amount for income in accountbook.incomes)

def calculate_total_withdrawals(accountbook):
    return sum(withdrawal.amount for withdrawal in accountbook.withdrawals)

def calculate_expected_expenses(accountbook):
    return sum(expected.amount for expected in accountbook.expected_expenses)

def print_summary(accountbook):
    total_expenses = calculate_total_expenses(accountbook)
    total_incomes = calculate_total_incomes(accountbook)
    total_withdrawals = calculate_total_withdrawals(accountbook)
    expected_expenses = calculate_expected_expenses(accountbook)
    balance = accountbook.calculate_balance()

    print("\n📋 가계부 요약")
    print("----------------------------")
    print(f"총 지출: {total_expenses:,} 원")
    print(f"총 수익: {total_incomes:,} 원")
    print(f"총 인출: {total_withdrawals:,} 원")
    print(f"예상 지출 합계: {expected_expenses:,} 원")
    print(f"현재 잔액 (현금 + 통장): {balance:,} 원")
    print("----------------------------\n")