import requests
from bs4 import BeautifulSoup
import pymysql
from datetime import datetime
import os
import time

# 프로젝트 설정 파일 경로
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYMBOLS_FILE = os.path.join(PROJECT_ROOT, 'config', 'symbols.txt')

# DB 연결 정보
DB_CONFIG = {
    'host': os.environ["DB_HOST"],
    'port': int(os.getenv("DB_PORT", "3306")),
    'user': os.environ["DB_USER"],
    'password': os.environ["DB_PASSWORD"],
    'db': os.environ["DB_NAME"],
    'charset': 'utf8'
}

# 가격 가져오기
def get_price_from_naver(symbol):
    url = f"https://finance.naver.com/item/main.nhn?code={symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        name = soup.select_one("div.wrap_company h2").text.strip()
        price = soup.select_one("p.no_today span.blind").text.strip().replace(",", "")
        return {
            "symbol": symbol,
            "name": name,
            "price": float(price)
        }
    except Exception as e:
        print(f"[오류] {symbol}: {e}")
        return None

# 이전 가격 가져오기
def get_previous_price(symbol):
    try:
        db = pymysql.connect(**DB_CONFIG)
        cur = db.cursor()
        sql = "SELECT last_price FROM stock WHERE symbol = %s"
        cur.execute(sql, (symbol,))
        row = cur.fetchone()
        db.close()
        return float(row[0]) if row else None
    except:
        return None

# 저장/업데이트
def insert_or_update(stock_data, change_rate):
    try:
        db = pymysql.connect(**DB_CONFIG)
        cur = db.cursor()
        now = datetime.now()

        sql = """
        INSERT INTO stock (symbol, name, last_price, change_rate, updated_at)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            last_price = VALUES(last_price),
            change_rate = VALUES(change_rate),
            updated_at = VALUES(updated_at)
        """
        cur.execute(sql, (
            stock_data['symbol'],
            stock_data['name'],
            stock_data['price'],
            change_rate,
            now
        ))
        db.commit()
        db.close()
    except Exception as e:
        print(f"[DB 오류] {stock_data['symbol']}: {e}")

# 메인 루프
def main():
    if not os.path.exists(SYMBOLS_FILE):
        print(f"❌ 종목 파일이 없습니다: {SYMBOLS_FILE}")
        return

    with open(SYMBOLS_FILE, 'r') as f:
        symbols = [line.strip().split('#')[0].strip() for line in f if line.strip()]

    print("주가 업데이트 시작 (30초 마다 갱신)")

    while True:
        print(f"\n🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 기준:")
        for symbol in symbols:
            stock_data = get_price_from_naver(symbol)
            if stock_data:
                previous_price = get_previous_price(symbol)
                current_price = stock_data['price']
                if previous_price:
                    change = ((current_price - previous_price) / previous_price) * 100
                else:
                    change = 0.0
                insert_or_update(stock_data, round(change, 2))
                print(f"  {stock_data['name']:<10} | {current_price:>8,.0f}원 | {change:+.2f}%")

        # 30초 대기
        time.sleep(30)

if __name__ == "__main__":
    main()
