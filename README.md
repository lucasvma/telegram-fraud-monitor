# 🔐 Fraud Monitoring System - Telegram Bot

> Secure and robust system for monitoring Telegram messages with intelligent fraud detection, OCR processing, and secure data storage.

[![Security](https://img.shields.io/badge/Security-Hardened-green.svg)](https://github.com/lucasvma/telegram-fraud-monitor)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Security Features](#-security-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Security](#-security)
- [Monitoring](#-monitoring)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

The **Fraud Monitoring System** is a complete solution for detecting and alerting about possible fraud attempts in Telegram conversations. The system uses advanced text processing and OCR techniques to analyze both text messages and images.

### ✨ Key Features

- **🔍 Intelligent Fraud Detection**: Real-time suspicious pattern analysis
- **📷 OCR Processing**: Text extraction and analysis from images
- **🛡️ Advanced Security**: Rate limiting, input validation, and security logging
- **📊 Secure Storage**: PostgreSQL database with content hashing for deduplication
- **🚨 Real-time Alerts**: Immediate notifications when fraud is detected
- **📈 Monitoring**: Detailed logs and security metrics

---

## 🛡️ Security Features

### 🔒 Authentication and Authorization
- ✅ Telegram token validation
- ✅ Configurable authorized chat list
- ✅ Chat ID-based access control

### 🚦 Rate Limiting and Validation
- ✅ Configurable messages per minute limit
- ✅ Strict input data validation
- ✅ Content sanitization to prevent injections
- ✅ File and image size validation

### 🔐 Data Protection
- ✅ SHA-256 hashing for secure deduplication
- ✅ Sensitive data encryption
- ✅ Security event logging
- ✅ Automatic temporary file cleanup

### 🐳 Container Hardening
- ✅ Non-root user execution
- ✅ Read-only file system
- ✅ Resource limits (CPU/Memory)
- ✅ Isolated network and restricted ports

---

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram API  │───▶│  Fraud Monitor  │───▶│   PostgreSQL    │
│                 │    │      Bot        │    │    Database     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  OCR Processor  │
                       │   (Tesseract)   │
                       └─────────────────┘
```

### 🧩 Components

- **Telegram Bot**: Main interface for receiving messages
- **Alert System**: Fraud pattern detection engine
- **OCR Processor**: Image processing with Tesseract
- **Database**: Secure storage with PostgreSQL
- **Security Layer**: Security layer with validations and rate limiting

---

## 📋 Prerequisites

- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Telegram Bot Token** (obtained via [@BotFather](https://t.me/botfather))
- **Secure password** for database (minimum 16 characters)

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/lucasvma/telegram-fraud-monitor.git
cd telegram-fraud-monitor
```

### 2. Configure Environment Variables

```bash
# Copy the configuration template
cp .env.example .env

# Edit the .env file with your credentials
nano .env
```

### 3. Secure Deployment

```bash
# Run the secure deployment script
chmod +x deploy.sh
./deploy.sh
```

---

## ⚙️ Configuration

### 🔑 Required Environment Variables

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_token_here

# Database
DB_PASS=your_secure_password_here
DB_USER=frauduser
DB_NAME=frauddb
```

### 🛡️ Security Settings

```bash
# Access Control
ALLOWED_CHAT_IDS=chat_id_1,chat_id_2,chat_id_3

# Rate Limiting
RATE_LIMIT_MESSAGES_PER_MINUTE=30
MAX_MESSAGE_LENGTH=5000
MAX_IMAGE_SIZE_MB=10

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/fraud_monitor.log
```

### 📷 OCR Settings

```bash
# Supported languages
OCR_LANGUAGES=eng+por
OCR_MAX_TEXT_LENGTH=2000
```

---

## 💻 Usage

### Docker Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down

# Complete rebuild
docker-compose up --build --force-recreate
```

### 📊 Monitoring

```bash
# Service status
docker-compose ps

# Security logs
docker-compose logs app | grep "SECURITY_EVENT"

# Database metrics
docker-compose exec db psql -U frauduser -d frauddb -c "SELECT COUNT(*) FROM messages;"
```

---

## 🔒 Security

### 🚨 Security Alerts

The system monitors and alerts about:

- **Unauthorized access attempts**
- **Rate limit exceeded**
- **Detected fraud patterns**
- **Suspicious or oversized files**
- **Critical system errors**

### 📝 Security Logs

All security events are logged with:

```
SECURITY_EVENT: [TYPE] | Chat: [ID] | User: [USER] | Details: [DETAILS]
```

### 🔄 Credential Rotation

```bash
# Generate new secure password
openssl rand -base64 32

# Update .env and restart
docker-compose down

# Edit .env
docker-compose up -d
```

---

## 📈 Monitoring

### 📊 Available Metrics

- **Messages processed per minute**
- **Fraud detections**
- **OCR processing performed**
- **Security events**
- **System performance**

### 🔍 Useful Queries

```sql
-- Messages per chat
SELECT chat_id, COUNT(*) FROM messages GROUP BY chat_id;

-- Fraud detections per day
SELECT DATE(timestamp), COUNT(*) FROM messages 
WHERE content LIKE '%FRAUD%' GROUP BY DATE(timestamp);

-- Top users by activity
SELECT user, COUNT(*) FROM messages GROUP BY user ORDER BY COUNT(*) DESC;
```
---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Contributors

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/lucasvma">
        <img src="https://avatars3.githubusercontent.com/u/32389328?s=180&u=8f4fac64a0b29b3aad86ea457c26fdfb963b1965&v=4" width="100px;" alt=""/>
        <br />
        <sub><b>Lucas Ventura</b></sub>
      </a>
      <br />
      <a title="Code">💻</a>
      <a title="Security">🔒</a>
      <a title="Documentation">📖</a>
      <a title="Architecture">🏗️</a>
    </td>
  </tr>
</table>

---

## 🔗 Documentation Links

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)
- [OWASP Security Guidelines](https://owasp.org/)

---

<div align="center">

**🛡️ Developed with focus on security and performance**

[⬆ Back to top](#-fraud-monitoring-system---telegram-bot)

</div>