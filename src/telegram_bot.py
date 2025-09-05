import os
import logging
import asyncio
import hashlib
from typing import Optional
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from database import init_db, store_message_securely, validate_chat_id, is_rate_limited
from alert_system import check_alerts
from ocr_processor import extract_text_from_image

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
log_file = os.getenv("LOG_FILE", "/app/logs/fraud_monitor.log")

logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - [PID:%(process)d]',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MAX_IMAGE_SIZE_MB = int(os.getenv("MAX_IMAGE_SIZE_MB", "10"))
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_MESSAGES_PER_MINUTE", "30"))
OCR_LANGUAGES = os.getenv("OCR_LANGUAGES", "eng+por")
OCR_MAX_TEXT_LENGTH = int(os.getenv("OCR_MAX_TEXT_LENGTH", "2000"))

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

if len(TOKEN) < 40:
    raise ValueError("Invalid TELEGRAM_BOT_TOKEN format")

def log_security_event(event_type: str, chat_id: str, user: str, details: str):
    """Log security-related events"""
    logger.warning(f"SECURITY_EVENT: {event_type} | Chat: {chat_id} | User: {user} | Details: {details}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages with security validations"""
    try:
        if not update.message:
            return
            
        chat_id = str(update.message.chat_id)
        user = update.message.from_user.username or update.message.from_user.first_name or "Unknown"
        
        if not validate_chat_id(chat_id):
            log_security_event("UNAUTHORIZED_CHAT", chat_id, user, "Chat not in allowed list")
            await update.message.reply_text("Unauthorized chat. Access denied.")
            return
        
        if is_rate_limited(chat_id, RATE_LIMIT_PER_MINUTE):
            log_security_event("RATE_LIMIT_EXCEEDED", chat_id, user, f"Exceeded {RATE_LIMIT_PER_MINUTE} messages/minute")
            await update.message.reply_text("Rate limit exceeded. Please slow down.")
            return
        
        if update.message.text:
            content = update.message.text
            logger.info(f"Processing text message from {user} in chat {chat_id}")
            
            if store_message_securely(chat_id, user, content):
                if check_alerts(content):
                    await update.message.reply_text("Potential fraud detected! Please be careful.")
                    log_security_event("FRAUD_PATTERN_DETECTED", chat_id, user, f"Text: {content[:100]}...")
            else:
                logger.error("Failed to store message securely")
        
        elif update.message.photo:
            await handle_image_message(update, context, chat_id, user)
        
        elif update.message.document:
            if update.message.document.mime_type and update.message.document.mime_type.startswith('image/'):
                await handle_document_image(update, context, chat_id, user)
            else:
                logger.info(f"Non-image document received from {user}, ignoring")
        
    except Exception as e:
        logger.error(f"Error handling message: {e}", exc_info=True)
        try:
            await update.message.reply_text("Internal error occurred. Please try again later.")
        except:
            pass

async def handle_image_message(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: str, user: str):
    try:
        logger.info(f"Processing image from {user} in chat {chat_id}")
        
        photo = update.message.photo[-1]
        
        if photo.file_size and photo.file_size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
            log_security_event("OVERSIZED_IMAGE", chat_id, user, f"Size: {photo.file_size} bytes")
            await update.message.reply_text(f"Image too large. Maximum size: {MAX_IMAGE_SIZE_MB}MB")
            return
        
        file = await context.bot.get_file(photo.file_id)
        
        temp_dir = "/tmp/fraud_bot_secure"
        os.makedirs(temp_dir, exist_ok=True)
        
        file_hash = hashlib.sha256(f"{photo.file_id}{chat_id}{user}".encode()).hexdigest()[:16]
        file_path = f"{temp_dir}/{file_hash}.jpg"
        
        logger.info(f"Downloading image to: {file_path}")
        await file.download_to_drive(file_path)
        
        if not os.path.exists(file_path):
            logger.error("Failed to download image file")
            await update.message.reply_text("Failed to download image.")
            return
        
        file_size = os.path.getsize(file_path)
        if file_size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
            log_security_event("OVERSIZED_DOWNLOADED_IMAGE", chat_id, user, f"Size: {file_size} bytes")
            os.remove(file_path)
            await update.message.reply_text(f"Downloaded image too large. Maximum size: {MAX_IMAGE_SIZE_MB}MB")
            return
        
        logger.info(f"Image downloaded successfully, size: {file_size} bytes")
        
        logger.info("Starting OCR processing...")
        extracted_text = extract_text_from_image(file_path)
        
        if extracted_text:
            if len(extracted_text) > OCR_MAX_TEXT_LENGTH:
                extracted_text = extracted_text[:OCR_MAX_TEXT_LENGTH] + "... [OCR TRUNCATED]"
            
            logger.info(f"OCR extracted text ({len(extracted_text)} chars)")
            
            ocr_content = f"[IMAGE OCR]: {extracted_text}"
            if store_message_securely(chat_id, user, ocr_content):
                await update.message.reply_text(f"Image processed! Extracted {len(extracted_text)} characters of text.")
                
                if check_alerts(extracted_text):
                    await update.message.reply_text("Potential fraud detected in image! Please be careful.")
                    log_security_event("FRAUD_PATTERN_DETECTED_OCR", chat_id, user, f"OCR: {extracted_text[:100]}...")
            else:
                logger.error("Failed to store OCR result securely")
        else:
            logger.info("No text extracted from image")
            await update.message.reply_text("Image processed, but no text was found.")
            
    except Exception as e:
        logger.error(f"OCR processing failed: {e}", exc_info=True)
        await update.message.reply_text("Failed to process image. Please try again.")
    finally:
        try:
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to clean up temp file: {e}")

async def handle_document_image(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: str, user: str):
    try:
        document = update.message.document
        
        if document.file_size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
            log_security_event("OVERSIZED_DOCUMENT", chat_id, user, f"Size: {document.file_size} bytes")
            await update.message.reply_text(f"Document too large. Maximum size: {MAX_IMAGE_SIZE_MB}MB")
            return
        
        logger.info(f"Processing document image from {user} in chat {chat_id}")
        
    except Exception as e:
        logger.error(f"Document processing failed: {e}", exc_info=True)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    error_msg = f"Update {update} caused error {context.error}"
    logger.error(error_msg)
    
    if update and update.message:
        chat_id = str(update.message.chat_id)
        user = update.message.from_user.username or "Unknown"
        log_security_event("BOT_ERROR", chat_id, user, str(context.error))

def main():
    try:
        logger.info("Initializing database...")
        init_db()
        
        logger.info("Creating Telegram application...")
        app = Application.builder().token(TOKEN).build()
        
        app.add_handler(MessageHandler(filters.ALL, handle_message))
        app.add_error_handler(error_handler)
        
        logger.info("Fraud Monitor Bot started successfully with security hardening")
        
        app.run_polling(
            drop_pending_updates=True,
            allowed_updates=['message'],
            timeout=30,
            read_timeout=30,
            write_timeout=30,
            connect_timeout=30
        )
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()