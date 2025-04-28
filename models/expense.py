# models/expense.py

class Expense:
    def __init__(self, date, category, amount, memo=""):
        self.date = date
        self.category = category
        self.amount = amount
        self.memo = memo

    def to_dict(self):
        return {
            "date": self.date,
            "category": self.category,
            "amount": self.amount,
            "memo": self.memo
        }