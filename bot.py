import json
import os
import random
import requests
from telegram.ext import Updater, CommandHandler

JSON_FILE = "vietlott_645.json"
LATEST_URL = "https://xoso.com.vn/xo-so-vietlott-mega-6-45.html"


# ---------------------------
# Helpers
# ---------------------------

def load_data():
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def fetch_latest_draw():
    """
    Crawl duy nhất trang kỳ quay mới nhất
    Format kết quả:
    {
        "draw_id": "...",
        "date": "...",
        "numbers": ["..", "..", ...]
    }
    """

    print("Fetching latest draw...")

    html = requests.get(LATEST_URL, timeout=10).text

    # Extract kỳ quay
    import re
    draw_id_match = re.search(r"Kỳ quay thưởng\s*:\s*.*?(\d+)", html)
    date_match = re.search(r"Ngày quay thưởng\s*:\s*.*?(\d{2}\/\d{2}\/\d{4})", html)
    numbers_match = re.findall(r'class="bong_tron.*?">(.*?)<', html)

    if not draw_id_match or not date_match or len(numbers_match) < 6:
        return None

    latest = {
        "draw_id": draw_id_match.group(1),
        "date": date_match.group(1),
        "numbers": numbers_match[:6]
    }

    return latest

def update_latest():
    """Đồng bộ duy nhất kỳ quay mới nhất vào file JSON"""
    data = load_data()
    latest = fetch_latest_draw()

    if latest is None:
        return None, "Không lấy được dữ liệu mới nhất từ Vietlott."

    # Nếu file rỗng hoặc draw_id mới → thêm vào
    if len(data) == 0 or data[-1]["draw_id"] != latest["draw_id"]:
        data.append(latest)
        save_data(data)
        print("New draw added:", latest["draw_id"])
    else:
        print("No new draw. Already up-to-date.")

    return latest, None

# ---------------------------
# BOT COMMANDS
# ---------------------------

def cmd_latest(update, context):
    latest, error = update_latest()
    if error:
        update.message.reply_text(error)
        return

    msg = (
        f"🎉 *Kỳ quay mới nhất Mega 6/45*\n"
        f"📅 Ngày: {latest['date']}\n"
        f"🆔 Kỳ: {latest['draw_id']}\n"
        f"🎰 Số trúng: {', '.join(latest['numbers'])}"
    )
    update.message.reply_text(msg, parse_mode="Markdown")

def cmd_random(update, context):
    nums = sorted(random.sample(range(1, 46), 6))
    nums = [f"{n:02d}" for n in nums]
    update.message.reply_text("🎲 Bộ số ngẫu nhiên:\n" + ", ".join(nums))

def cmd_stats(update, context):
    data = load_data()
    if not data:
        update.message.reply_text("Chưa có dữ liệu thống kê.")
        return

    freq = {f"{i:02d}": 0 for i in range(1, 46)}

    for item in data:
        for n in item["numbers"]:
            freq[n] += 1

    sorted_list = sorted(freq.items(), key=lambda x: x[1], reverse=True)

    msg = "📊 *Thống kê Mega 6/45*\n(số: tần suất)\n\n"
    msg += "\n".join([f"{n}: {c}" for n, c in sorted_list])
    update.message.reply_text(msg, parse_mode="Markdown")

def cmd_random_min(update, context):
    data = load_data()

    freq = {f"{i:02d}": 0 for i in range(1, 46)}
    for item in data:
        for n in item["numbers"]:
            freq[n] += 1

    sorted_nums = sorted(freq.items(), key=lambda x: x[1])
    least_30 = [n for n, _ in sorted_nums[:30]]

    pick = sorted(random.sample(least_30, 6))
    update.message.reply_text("🥶 Bộ số ít xuất hiện:\n" + ", ".join(pick))

def cmd_random_max(update, context):
    data = load_data()

    freq = {f"{i:02d}": 0 for i in range(1, 46)}
    for item in data:
        for n in item["numbers"]:
            freq[n] += 1

    sorted_nums = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    top_30 = [n for n, _ in sorted_nums[:30]]

    pick = sorted(random.sample(top_30, 6))
    update.message.reply_text("🔥 Bộ số xuất hiện nhiều:\n" + ", ".join(pick))

# ---------------------------
# MAIN
# ---------------------------

def main():
    # ---------------------------
    # CONFIG
    # ---------------------------

    # Lấy token từ biến môi trường TELEGRAM_TOKEN
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        raise RuntimeError("Vui lòng đặt biến môi trường TELEGRAM_TOKEN với token bot của bạn.")


    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("latest", cmd_latest))
    dp.add_handler(CommandHandler("random", cmd_random))
    dp.add_handler(CommandHandler("random_min", cmd_random_min))
    dp.add_handler(CommandHandler("random_max", cmd_random_max))
    dp.add_handler(CommandHandler("stats", cmd_stats))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
