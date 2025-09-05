import os
import logging
import time
from collections import defaultdict
from typing import Set, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import OperationalError
from datetime import datetime, timezone
import secrets
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_USER = os.getenv("DB_USER", "frauduser")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "frauddb")
DB_PORT = os.getenv("DB_PORT", "5432")
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "5000"))

if not DB_PASS:
    raise ValueError("DB_PASS environment variable is required and cannot be empty")

if len(DB_PASS) < 16:
    raise ValueError("DB_PASS must be at least 16 characters long")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    pool_pre_ping=True,
    echo=False,
    connect_args={
        "connect_timeout": 10,
        "application_name": "fraud_monitor_bot",
        "sslmode": "prefer"
    }
)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String(50), nullable=False, index=True)
    user = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=False, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    def __repr__(self):
        return f"<Message(id={self.id}, chat_id={self.chat_id}, user={self.user[:20]}...)>"

rate_limit_storage = defaultdict(list)

def sanitize_input(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    
    sanitized = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    if len(sanitized) > MAX_MESSAGE_LENGTH:
        sanitized = sanitized[:MAX_MESSAGE_LENGTH] + "... [TRUNCATED]"
    
    return sanitized

def generate_content_hash(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def is_rate_limited(chat_id: str, limit_per_minute: int = 30) -> bool:
    now = time.time()
    chat_requests = rate_limit_storage[chat_id]
    
    chat_requests[:] = [req_time for req_time in chat_requests if now - req_time < 60]
    
    if len(chat_requests) >= limit_per_minute:
        return True
    
    chat_requests.append(now)
    return False

def validate_chat_id(chat_id: str) -> bool:
    if not chat_id or not isinstance(chat_id, str):
        return False
    
    try:
        int(chat_id)
    except ValueError:
        return False
    
    allowed_chats = os.getenv("ALLOWED_CHAT_IDS", "")
    if allowed_chats:
        allowed_list = [chat.strip() for chat in allowed_chats.split(",")]
        return chat_id in allowed_list
    
    return True

def wait_for_db(max_retries=30, initial_delay=1):
    """Wait for database to become available with exponential backoff"""
    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            return True
        except OperationalError as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed to connect to database after {max_retries} attempts: {e}")
                raise
            
            delay = min(initial_delay * (2 ** attempt), 30)
            logger.info(f"Database not ready (attempt {attempt + 1}/{max_retries}). Retrying in {delay} seconds...")
            time.sleep(delay)
    
    return False

def init_db():
    try:
        wait_for_db()
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()

def store_message_securely(chat_id: str, user: str, content: str) -> bool:
    try:
        if not validate_chat_id(chat_id):
            logger.warning(f"Invalid or unauthorized chat ID: {chat_id}")
            return False
        
        if is_rate_limited(chat_id):
            logger.warning(f"Rate limit exceeded for chat: {chat_id}")
            return False
        
        sanitized_content = sanitize_input(content)
        sanitized_user = sanitize_input(user)[:100]
        
        if not sanitized_content:
            logger.warning("Empty content after sanitization")
            return False
        
        content_hash = generate_content_hash(sanitized_content)
        
        db = next(get_db_session())
        
        existing = db.query(Message).filter(
            Message.content_hash == content_hash,
            Message.chat_id == chat_id
        ).first()
        
        if existing:
            logger.info("Duplicate message detected, skipping storage")
            return True
        
        message = Message(
            chat_id=chat_id,
            user=sanitized_user,
            content=sanitized_content,
            content_hash=content_hash
        )
        db.add(message)
        db.commit()
        logger.info("Message stored securely")
        return True
        
    except Exception as e:
        logger.error(f"Failed to store message securely: {e}")
        return False
    finally:
        db.close()