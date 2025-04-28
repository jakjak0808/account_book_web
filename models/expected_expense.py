# models/expected_expense.py

class ExpectedExpense:
    def __init__(self, date, category, amount, memo=""):
        self.date = date              # 예정된 지출 날짜
        self.category = category      # 지출 항목 (예: 월세, 보험료)
        self.amount = amount          # 지출 금액
        self.memo = memo              # 메모 (선택)

    def to_dict(self):
        return {
            "date": self.date,
            "category": self.category,
            "amount": self.amount,
            "memo": self.memo
        }