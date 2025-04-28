# models/accountbook.py

from .expense import Expense
from .income import Income
from .withdrawal import Withdrawal
from .expected_expense import ExpectedExpense

class AccountBook:
    def __init__(self):
        self.cash = 0                  # 현재 현금
        self.bank = 0                  # 현재 통장 잔액
        self.expenses = []             # 지출 리스트
        self.incomes = []              # 수익 리스트
        self.withdrawals = []          # 인출 리스트
        self.expected_expenses = []    # 예상 지출 리스트

    # 현재 자금 설정
    def set_initial_funds(self, cash, bank):
        self.cash = cash
        self.bank = bank

    # 지출 추가
    def add_expense(self, date, category, amount, memo=""):
        expense = Expense(date, category, amount, memo)
        self.expenses.append(expense)
        self.cash -= amount

    # 수익 추가
    def add_income(self, date, source, amount, memo=""):
        income = Income(date, source, amount, memo)
        self.incomes.append(income)
        self.cash += amount

    # 통장에서 인출
    def withdraw_from_bank(self, date, amount, memo=""):
        if self.bank >= amount:
            self.bank -= amount
            self.cash += amount
            withdrawal = Withdrawal(date, amount, memo)
            self.withdrawals.append(withdrawal)
        else:
            print("❌ 은행 잔액이 부족합니다.")

    # 예상 지출 추가
    def add_expected_expense(self, date, category, amount, memo=""):
        expected = ExpectedExpense(date, category, amount, memo)
        self.expected_expenses.append(expected)

    # 잔액 계산
    def calculate_balance(self):
        return self.cash + self.bank

    # 전체 데이터를 dict로 변환 (나중에 저장할 때 사용)
    def to_dict(self):
        return {
            'cash': self.cash,
            'bank': self.bank,
            'expenses': [e.to_dict() for e in self.expenses],
            'incomes': [i.to_dict() for i in self.incomes],
            'withdrawals': [w.to_dict() for w in self.withdrawals],
            'expected_expenses': [ex.to_dict() for ex in self.expected_expenses]
        }

    # dict를 다시 불러오기
    def load_from_dict(self, data):
        self.cash = data.get('cash', 0)
        self.bank = data.get('bank', 0)
        self.expenses = [Expense(**e) for e in data.get('expenses', [])]
        self.incomes = [Income(**i) for i in data.get('incomes', [])]
        self.withdrawals = [Withdrawal(**w) for w in data.get('withdrawals', [])]
        self.expected_expenses = [ExpectedExpense(**ex) for ex in data.get('expected_expenses', [])]