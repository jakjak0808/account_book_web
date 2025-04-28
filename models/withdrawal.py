# models/withdrawal.py

class Withdrawal:
    def __init__(self, date, amount, memo=""):
        self.date = date            # 인출 날짜
        self.amount = amount        # 인출 금액
        self.memo = memo            # 메모 (선택)

    def to_dict(self):
        return {
            "date": self.date,
            "amount": self.amount,
            "memo": self.memo
        }