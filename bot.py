import json
from telegram.ext import Updater, CommandHandler

import os
TOKEN = os.getenv("TELEGRAM_TOKEN")


# ---------------------- LOAD JSON ----------------------
def load_results():
    with open("vietlott_645.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_stats():
    with open("statistics_645.json", "r", encoding="utf-8") as f:
        return json.load(f)

# ---------------------- COMMANDS ----------------------
def start(update, context):
    update.message.reply_text(
        "Xin chào! Bot Vietlott đã sẵn sàng.\n\n"
        "Các lệnh hỗ trợ:\n"
        "/latest - Kỳ mở thưởng mới nhất\n"
        "/stats - Thống kê tần suất xuất hiện\n"
        "/top6 - 6 số xuất hiện nhiều nhất"
    )

def latest(update, context):
    data = load_results()
    latest_draw = data[0]  # giả sử file json bạn lưu đảo ngược

    resp = (
        f"Kỳ mở thưởng gần nhất:\n"
        f"Ngày: {latest_draw['date']}\n"
        f"Kỳ: {latest_draw['draw_id']}\n"
        f"Số: {', '.join(latest_draw['numbers'])}"
    )

    update.message.reply_text(resp)

def stats(update, context):
    stats = load_stats()["statistics"]
    total = load_stats()["total_draws"]

    lines = [f"Thống kê {total} kỳ (Top 10 tần suất):\n"]

    # sắp xếp nhiều → ít
    sorted_stats = sorted(stats, key=lambda x: x["count"], reverse=True)

    for item in sorted_stats[:10]:
        lines.append(f"Số {item['number']} → {item['count']} lần ({item['percent']}%)")

    update.message.reply_text("\n".join(lines))

def top6(update, context):
    stats = load_stats()["statistics"]
    sorted_stats = sorted(stats, key=lambda x: x["count"], reverse=True)

    top = sorted_stats[:6]

    resp = "🎯 *Top 6 số xuất hiện nhiều nhất*\n"

    for i, item in enumerate(top, 1):
        resp += f"{i}. Số {item['number']} → {item['count']} lần\n"

    update.message.reply_text(resp, parse_mode="Markdown")

# ---------------------- MAIN ----------------------
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("latest", latest))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("top6", top6))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
