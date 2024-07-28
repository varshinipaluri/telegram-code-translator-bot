import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import openai
from config import OPENAI_API_KEY

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Telegram bot token
TELEGRAM_TOKEN = '7445545544:AAEI9HD-7HRXtdnX-k0cql6NHT7XqYXpRUs'

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Start command handler
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Hello! I am your Code Translator Bot. Send me code to translate.')

# Translate command handler
async def translate_code(update: Update, context: CallbackContext) -> None:
    user_input = update.message.text
    language_query = "Translate the following code from {source} to {target} and explain if necessary:\n"
    
    try:
        if "from" in user_input and "to" in user_input:
            parts = user_input.split()
            source_lang = parts[parts.index("from") + 1]
            target_lang = parts[parts.index("to") + 1]
            code = user_input[user_input.index("to") + len(target_lang) + 1:].strip()
            prompt = language_query.format(source=source_lang, target=target_lang) + code
        else:
            prompt = "Translate the following code and explain if necessary:\n" + user_input
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        translation = response['choices'][0]['message']['content'].strip()
        await update.message.reply_text(translation)
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        if "quota" in str(e):
            await update.message.reply_text("An error occurred: You have exceeded your API quota. Please check your plan and billing details.")
        else:
            await update.message.reply_text(f"An error occurred: {e}")

def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_code))

    logger.info("Starting the bot...")
    application.run_polling()

if __name__ == '__main__':
    main()
