# 📖 Natiq Quran API

<div align="center">

![Natiq Logo](https://img.shields.io/badge/Natiq-Quran%20API-green?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMMTMuMDkgOC4yNkwyMCA5TDEzLjA5IDE1Ljc0TDEyIDIyTDEwLjkxIDE1Ljc0TDQgOUwxMC45MSA4LjI2TDEyIDJaIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4K)

**A comprehensive open-source Quran API providing easy access to Quranic content**

• [🌐 Website](https://natiq.net/) • [🛠️ Developer Portal](https://developer.natiq.net) • [📖 Test api in browser](https://api.natiq.net) • [📦 SDK](https://github.com/NatiqQuran/nq-sdk) • [🐛 Issues](https://github.com/NatiqQuran/nq-api/issues)

[![Django CI](https://github.com/NatiqQuran/nq-api/actions/workflows/django.yml/badge.svg)](https://github.com/NatiqQuran/nq-api/actions/workflows/django.yml)
[![Docker Image CI](https://github.com/NatiqQuran/nq-api/actions/workflows/docker-image.yml/badge.svg)](https://github.com/NatiqQuran/nq-api/actions/workflows/docker-image.yml)
[![Docker Publish](https://github.com/NatiqQuran/nq-api/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/NatiqQuran/nq-api/actions/workflows/docker-publish.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Contributors](https://img.shields.io/github/contributors/NatiqQuran/nq-api)](https://github.com/NatiqQuran/nq-api/graphs/contributors)
[![Stars](https://img.shields.io/github/stars/NatiqQuran/nq-api?style=social)](https://github.com/NatiqQuran/nq-api/stargazers)

</div>

---

## 📑 Table of Contents

- [Description](#description)
  - [Key Features](#key-features)
  - [Developer Tools](#-developer-tools)
  - [Official SDK](#-official-sdk)
- [API Endpoints](#api-endpoints)
- [Project Structure](#%EF%B8%8F-developer-tools)
- [Install/Deploy Options](#installdeploy-options)
  - [With Docker](#with-docker)

---

## Description

**Natiq Quran API** is a powerful, open-source RESTful API designed to provide developers with seamless access to the Holy Quran's content—including full Arabic text, multilingual translations, and audio recitations.

This API is at the heart of the **Natiq ecosystem**, powering various digital Islamic tools such as:

- ✅ **Natiq SDKs** for effortless integration into your mobile, web, or backend apps
- 🌍 **[natiq.net](https://natiq.net)** — our fully-featured platform built on top of this API
- ⚙️ Conversion and content tools to help you extend and customize Quranic data
- 📱 Frontend apps using **Next.js** and **PWA** technologies

Whether you're building an educational platform, a personal Quran app, or integrating spiritual content into your existing products, `nq-api` provides a fast, developer-friendly, and scalable foundation.

> If you're looking to get started quickly, consider using our **[nq-sdk](https://github.com/NatiqQuran/nq-sdk)** or ready-to-use hosted services at **[api.natiq.net](https://api.natiq.net).**

### Key Features

- 📚 **Complete Quranic Text** - Access all 114 Surahs with original Arabic text
- 🌍 **Multi-language Support** - Translations in multiple languages
- 🔊 **Audio Integration** - Links to recitation files
- 📖 **Tafsir Support** - Commentary and explanations
- 📖 **Word-by-Word Data** - Get detailed information for each word in an Ayah
- ⚡ **High Performance** - Fast response times with optimized data structure
- 🔓 **Open Source** - Free to use and contribute
- 📱 **Developer Friendly** - Simple REST endpoints with JSON responses
- 🛡️ **Reliable** - Stable API with consistent uptime

### 🛠️ Developer Tools

**[developer.natiq.net](https://developer.natiq.net)** - Test all endpoints directly in your browser!

- 🎯 **Zero Setup Required** - Start testing immediately
- 🔍 **Live API Testing** - Interactive playground for all endpoints
- 📖 **Real-time Documentation** - See responses as you explore
- 💡 **Code Examples** - Copy-paste ready code snippets
- 🔧 **Request Builder** - Visual interface for API calls

### 📦 Official SDK

**[nq-sdk](https://github.com/NatiqQuran/nq-sdk)** - Official SDK for faster development

- ⚡ **Quick Integration** - Get started in minutes, not hours
- 🔄 **Auto-completion** - Full TypeScript support

## API Endpoints

The following are the main API endpoints available:

- `/users/`: User management.
- `/groups/`: Group management.
- `/mushafs/`: Mushaf (Quran version) information.
- `/surahs/`: List of Surahs.
- `/ayahs/`: List of Ayahs.
- `/words/`: List of words.
- `/translations/`: Available translations.
- `/ayah-translations/`: Ayah translations.
- `/recitations/`: Recitation information.
- `/auth/`: Authentication endpoints.
- `/profile/`: User profiles.
- `/phrases/`: Quranic phrases.

## Project Structure

```
nq-api/
├── 📁 account/         # User management app
├── 📁 api/             # Core API configuration and routing
├── 📁 core/            # Core functionalities
├── 📁 quran/           # Quran-related app (Surahs, Ayahs, etc.)
├── 📄 .dockerignore
├── 📄 .gitignore
├── 📄 Dockerfile       # Docker image configuration
├── 📄 LICENSE          # project license
├── 📄 README.md         # This file
├── 📄 docker-compose.yaml # Docker orchestration
├── 📄 entrypoint.prod.sh
├── 📄 manage.py         # Django management script
├── 📄 nginx.conf        # Django management script
└── 📄 requirements.txt  # Python dependencies
```

## Install/Deploy Options

### With Docker

---

#### 🔹 Step 1 – Update your system

```bash
sudo apt update
```

---

#### 🔹 Step 2 – Install Docker

If Docker is not already installed, you can install it with the official script:

```bash
curl -fsSL https://get.docker.com | sh
```

You can verify the installation with:

```bash
docker --version
```

---

#### 🔹 Step 3 – Create the project folder

```bash
mkdir -p nq-api
cd nq-api
```

---

#### 🔹 Step 4 – Download required files

```bash
curl -fsSL https://raw.githubusercontent.com/NatiqQuran/nq-api/refs/heads/main/docker-compose.yaml -o docker-compose.yaml
curl -fsSL https://raw.githubusercontent.com/NatiqQuran/nq-api/refs/heads/main/nginx.conf -o nginx.conf
```

---

#### 🔹 Step 5 – Review your docker-compose.yaml

Make sure the following values are properly set inside the `environment:` section under the `api` service:

* `SECRET_KEY`: Generate one using:

```bash
cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 40 | head -n 1
```

* `DJANGO_ALLOWED_HOSTS`: Get your public IP:

```bash
curl -s https://api.ipify.org
```

You can now edit the file and insert these values as shown below:

```yaml
api:
    image: natiqquran/nq-api:main 
```

```yaml
environment:
  SECRET_KEY: your-generated-secret
  DJANGO_ALLOWED_HOSTS: your-ip-address

```

Open the file with:

```bash
nano docker-compose.yaml
```

Or use any other editor you prefer.

---

#### 🔹 Step 6 – Run the containers

From inside the `nq-api` folder:

```bash
docker compose up -d
```

---

#### ✅ Done!

After a few seconds, the API should be up and running.

You can now access it at:

```
http://<your-server-ip>
```

Replace `<your-server-ip>` with your actual server IP or Domain address .