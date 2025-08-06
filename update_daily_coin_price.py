import requests
from datetime import datetime
import os

README_PATH = "README.md"
ARCHIVE_DIR = "archive"  # 날짜별 저장 폴더

# CoinMarketCap API 키
API_KEY = os.getenv("COINMARKETCAP_API_KEY")
CMC_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

def get_coin_data():
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": API_KEY,
    }
    params = {
        "start": 1,
        "limit": 500,           # 시총 500위까지
        "convert": "USD",
        "sort": "market_cap",
        "sort_dir": "desc"
    }
    response = requests.get(CMC_URL, headers=headers, params=params)
    data = response.json()["data"]
    # 24시간 상승률 기준 내림차순 정렬
    sorted_data = sorted(data, key=lambda x: x["quote"]["USD"]["percent_change_24h"], reverse=True)
    return sorted_data

def format_coin_markdown(coin_list, top_n=20):
    header = (
        "| 🔢 순위 | 🪙 코인명 | 🔣 심볼 | 💲 현재 가격 (USD) | 📈 24시간 상승률 (%) | 💰 시가총액 (USD) | 🔄 24시간 거래량 (USD) | 🔢 유통 공급량 |\n"
        "|--------|----------|--------|-------------------|--------------------|--------------------|-----------------------|-------------------|\n"
    )

    lines = []
    for i, coin in enumerate(coin_list[:top_n], 1):
        name = coin["name"]
        symbol = coin["symbol"]
        price = coin["quote"]["USD"]["price"]
        change_24h = coin["quote"]["USD"]["percent_change_24h"]
        market_cap = coin["quote"]["USD"]["market_cap"]
        volume_24h = coin["quote"]["USD"]["volume_24h"]
        circulating_supply = coin["circulating_supply"]

        # 상승률 이모지 표시
        if change_24h > 10:
            change_str = f"🟢 **{change_24h:.2f}**"
        elif change_24h > 0:
            change_str = f"🟩 {change_24h:.2f}"
        elif change_24h == 0:
            change_str = f"⚪ {change_24h:.2f}"
        else:
            change_str = f"🔴 {change_24h:.2f}"

        supply_str = f"{circulating_supply:,.0f}"

        line = (
            f"| {i} | {name} | {symbol} | ${price:,.4f} | {change_str} | "
            f"${market_cap:,.0f} | ${volume_24h:,.0f} | {supply_str} |"
        )
        lines.append(line)

    return header + "\n".join(lines)

def update_readme_and_archive():
    coins = get_coin_data()
    now = datetime.utcnow()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    date_str = now.strftime("%Y-%m-%d")

    markdown_table = format_coin_markdown(coins, top_n=20)

    content = f"""
# 📈 "라고 할 때 살걸..." — 시총 500위 코인 24시간 상승률 TOP 20 🚀

> 매일 아침 시가총액 상위 500위 중 24시간 상승률 기준 상위 20개 업데이트  
> ⏰ 업데이트 시간: **{now_str} (UTC)**

{markdown_table}

---

✨ *자동 업데이트 봇에 의해 관리됩니다.*
"""

    # README.md 업데이트
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"{README_PATH} 파일이 업데이트 되었습니다.")

    # archive 폴더 생성 (없으면)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    # 날짜만 파일명으로 아카이브 저장 (.md 확장자)
    archive_path = os.path.join(ARCHIVE_DIR, f"{date_str}.md")
    with open(archive_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"{archive_path} 파일로 아카이브 저장 완료!")

if __name__ == "__main__":
    update_readme_and_archive()
