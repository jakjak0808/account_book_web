# services/save_load_service.py

import json
import os

def save_accountbook(accountbook, filename='data/accountbook.json'):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(accountbook.to_dict(), f, ensure_ascii=False, indent=2)
    print(f"✅ 데이터가 '{filename}'에 저장되었습니다.")

def load_accountbook(accountbook, filename='data/accountbook.json'):
    if not os.path.exists(filename):
        print(f"⚠️ '{filename}' 파일이 없습니다. 새로 시작합니다.")
        return
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
        accountbook.load_from_dict(data)
    print(f"✅ '{filename}'에서 데이터가 불러와졌습니다.")