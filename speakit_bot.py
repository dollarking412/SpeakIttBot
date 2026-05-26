import os
import logging
import requests
import urllib.parse
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
BOT_TOKEN = os.environ.get("SPEAKIT_BOT_TOKEN")

if not BOT_TOKEN:
    logger.error("SPEAKIT_BOT_TOKEN environment variable not set!")
    exit(1)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎤 *SpeakIt Bot Active!*\n\n"
        "Send me any text and I'll convert it to speech.\n\n"
        "📝 *How to use:*\n"
        "• Send any text message\n"
        "• I'll convert it to voice\n"
        "• You'll receive an audio file\n\n"
        "Just type anything and I'll speak it!",
        parse_mode="Markdown"
    )

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 *How to use SpeakIt Bot*\n\n"
        "Simply send me any text and I'll convert it to speech.\n\n"
        "*Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show this help\n\n"
        "*Limitations:*\n"
        "• Minimum 3 characters\n"
        "• Maximum 1000 characters",
        parse_mode="Markdown"
    )

# Convert text to speech
async def text_to_speech(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # Skip if it's a command
    if text.startswith('/'):
        return
    
    # Validate text
    if len(text) < 3:
        await update.message.reply_text("⚠️ Please send at least 3 characters.")
        return
    
    if len(text) > 1000:
        await update.message.reply_text("⚠️ Text too long! Maximum 1000 characters.")
        return
    
    # Send processing message
    processing_msg = await update.message.reply_text("🎵 Converting text to speech...")
    
    try:
        # Using free TTS API (no API key required)
        encoded_text = urllib.parse.quote(text)
        url = f"https://api.streamelements.com/kappa/v2/speech?voice=Brian&text={encoded_text}"
        
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            # Save audio file
            audio_file = f"speech_{update.message.message_id}.mp3"
            with open(audio_file, "wb") as f:
                f.write(response.content)
            
            # Send audio as voice message
            with open(audio_file, "rb") as audio:
                await update.message.reply_voice(voice=audio, caption="🎤 Here's your text-to-speech audio!")
            
            # Clean up
            os.remove(audio_file)
            await processing_msg.delete()
        else:
            await processing_msg.edit_text("❌ Failed to convert text to speech. Please try again.")
    except Exception as e:
        logger.error(f"TTS error: {e}")
        await processing_msg.edit_text("❌ An error occurred. Please try again later.")

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.message:
        await update.message.reply_text("❌ An error occurred. Please try again later.")

# Main function
def main():
    print("🎤 Starting SpeakIt Bot...")
    print(f"Bot Token configured: {'Yes' if BOT_TOKEN else 'No'}")
    
    # Create application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_to_speech))
    app.add_error_handler(error_handler)
    
    # Start bot
    print("✅ SpeakIt Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
