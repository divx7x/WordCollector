import os
import logging
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Настраиваем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

# Хранилище для слов
word_pairs = []

# Обработчик сообщений
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global word_pairs
    text = update.message.text.strip()

    if " - " in text:
        parts = text.split(" - ", 1)
    else:
        await update.message.reply_text("❌ Формат неверный. Используйте: слово - перевод")
        return

    if len(parts) == 2:
        word, translation = parts
        word_pairs.append({"Word/Phrase": word, "Translation": translation})
        await update.message.reply_text(f"✅ Добавлено: {word} — {translation}")
    else:
        await update.message.reply_text("❌ Ошибка обработки. Проверьте формат.")

# Команда для выгрузки данных в CSV
async def export_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global word_pairs
    if not word_pairs:
        await update.message.reply_text("⚠️ Нет данных для экспорта.")
        return

    df = pd.DataFrame(word_pairs)
    file_path = "word_pairs.csv"
    df.to_csv(file_path, index=False, header=False)

    await update.message.reply_document(open(file_path, "rb"))
    await update.message.reply_text("✅ CSV файл успешно отправлен!")

# Основная функция
def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("❌ BOT_TOKEN не задан! Убедитесь, что переменная окружения установлена.")
        raise ValueError("❌ Ошибка: BOT_TOKEN не задан!")

    use_webhook = os.getenv("USE_WEBHOOK", "true").lower() == "true"
    port = int(os.environ.get("PORT", 8443))

    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(CommandHandler("export", export_csv))

    if use_webhook:
        webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME', 'wordcollector.onrender.com')}/{token}"
        logger.info(f"🚀 Запуск Webhook на {webhook_url} (PORT: {port})")

        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=token,
            webhook_url=webhook_url
        )
    else:
        logger.info("🔄 Запуск Long Polling...")
        app.run_polling()

if __name__ == "__main__":
    main()