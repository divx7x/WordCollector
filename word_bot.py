import os
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Хранилище для слов
word_pairs = []

# Обработчик сообщений
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global word_pairs
    text = update.message.text.strip()

    # Проверяем формат сообщения
    if " - " in text:
        parts = text.split(" - ", 1)
    else:
        await update.message.reply_text("Сообщение не распознано. Используйте формат 'слово - перевод'.")
        return

    if len(parts) == 2:
        word, translation = parts
        word_pairs.append({"Word/Phrase": word, "Translation": translation})
        await update.message.reply_text(f"Добавлено: {word} — {translation}")
    else:
        await update.message.reply_text("Сообщение не распознано. Проверьте формат.")

# Команда для выгрузки данных в CSV
async def export_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global word_pairs
    if not word_pairs:
        await update.message.reply_text("Нет данных для экспорта.")
        return

    # Создание DataFrame и сохранение в файл без заголовков
    df = pd.DataFrame(word_pairs)
    file_path = "word_pairs.csv"
    df.to_csv(file_path, index=False, header=False)
    await update.message.reply_document(open(file_path, "rb"))
    await update.message.reply_text("CSV файл успешно создан и отправлен!")

# Основная функция
def main():
    # Читаем токен из переменной окружения
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("❌ Ошибка: BOT_TOKEN не задан!")

    port = int(os.environ.get("PORT", 8443))  # Порт, который использует Render

    # Создаем приложение
    app = ApplicationBuilder().token(token).build()

    # Добавляем обработчики
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(CommandHandler("export", export_csv))

    # Включаем Webhook вместо Polling
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME', 'wordcollector.onrender.com')}/{token}"
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=token,
        webhook_url=webhook_url
    )

if __name__ == "__main__":
    main()