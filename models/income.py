# models/income.py

class Income:
    def __init__(self, date, source, amount, memo=""):
        self.date = date           # 수익 날짜
        self.source = source       # 수익 출처 (예: 월급, 이자)
        self.amount = amount       # 수익 금액
        self.memo = memo           # 메모 (선택)

    def to_dict(self):
        return {
            "date": self.date,
            "source": self.source,
            "amount": self.amount,
            "memo": self.memo
        }