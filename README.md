[![CI: GitHub Actions](https://github.com/NatiqQuran/nq-api/workflows/CI/badge.svg)](https://github.com/NatiqQuran/nq-api/actions)  [![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](LICENSE)

##  Description

`nq-api` is a high-performance Django-based RESTful API serving the complete Quranic text, translations, and audio files. It’s designed for developers and organizations to self-host and integrate Quranic data in web/mobile apps, services, or research. As part of the Natiq ecosystem, it pairs with frontends (Next.js, PWA), SDKs, and conversion tools.

## 🚀 Quick Installation

### Option 1: Direct Install (Recommended)
```bash
curl -fsSL https://raw.githubusercontent.com/NatiqQuran/nq-api/main/install.sh | bash
```

### Option 2: Download and Review
```bash
# Download the installer
curl -fsSL https://raw.githubusercontent.com/NatiqQuran/nq-api/main/install.sh -o install.sh

# Review the script (recommended for security)
cat install.sh

# Make executable and run
chmod +x install.sh
./install.sh
```

### Option 3: Skip Docker Installation
If Docker is already installed:
```bash
curl -fsSL https://raw.githubusercontent.com/NatiqQuran/nq-api/main/install.sh | bash -s -- no-install
```

## 📖 Installation Process

The script performs these steps automatically:

### 1. 🔍 **System Check**
- Verifies system compatibility
- Checks existing Docker installation
- Validates network connectivity

### 2. 🐳 **Docker Setup**
- Downloads and installs Docker CE
- Starts Docker daemon
- Installs Docker Compose

### 3. 📁 **Project Configuration**
- Creates `nq-api` project directory
- Downloads latest `docker-compose.yaml`
- Downloads nginx configuration

### 4. ⚙️ **Environment Setup**
- Generates secure `SECRET_KEY` (40 characters)
- Configures `DJANGO_ALLOWED_HOSTS` with server IP
- Sets up database credentials

### 5. 🚀 **Service Deployment**
- Pulls latest Docker images
- Starts all services (API, Database, Redis, Nginx)
- Runs database migrations
- Performs health checks

## 🏗️ Architecture

After installation, you'll have these services running:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │────│   Django API     │────│   PostgreSQL    │
│   Port: 80      │    │   Port: 8000     │    │   Port: 5432    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                │                ┌───────────────┐
                                └────────────────│     Redis     │
                                                 │   Port: 6379  │
                                                 └───────────────┘
```

### Manual Configuration

For custom settings, edit the configuration after installation:

```bash
cd nq-api
docker compose down        # Stop services
nano docker-compose.yaml  # Edit environment variables
docker compose up -d       # Restart with new config
```