# 📖 Natiq Quran API

<div align="center">

![Natiq Logo](https://img.shields.io/badge/Natiq-Quran%20API-green?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMMTMuMDkgOC4yNkwyMCA5TDEzLjA5IDE1Ljc0TDEyIDIyTDEwLjkxIDE1Ljc0TDQgOUwxMC45MSA4LjI2TDEyIDJaIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4K)

**A comprehensive open-source Quran API providing easy access to Quranic content**

[![API Status](https://img.shields.io/badge/API-Active-brightgreen)](https://github.com/NatiqQuran/nq-api)
 [![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](LICENSE)
[![Contributors](https://img.shields.io/github/contributors/NatiqQuran/nq-api)](https://github.com/NatiqQuran/nq-api/graphs/contributors)
[![Stars](https://img.shields.io/github/stars/NatiqQuran/nq-api?style=social)](https://github.com/NatiqQuran/nq-api/stargazers)

[🌐 Website](https://natiq.net/) • [🛠️ Developer Portal](https://developer.natiq.net) • [📦 SDK](https://github.com/NatiqQuran/nq-sdk) • [📖 Documentation](#api-documentation) • [🐛 Issues](https://github.com/NatiqQuran/nq-api/issues) • [💬 Discussions](https://github.com/NatiqQuran/nq-api/discussions)

</div>

##  Description

**Natiq Quran API** is a powerful, open-source RESTful API designed to provide developers with seamless access to the Holy Quran's content—including full Arabic text, multilingual translations, and audio recitations.

This API is at the heart of the **Natiq ecosystem**, powering various digital Islamic tools such as:

* ✅ **Natiq SDKs** for effortless integration into your mobile, web, or backend apps
* 🌍 **[natiq.net](https://natiq.net)** — our fully-featured platform built on top of this API
* ⚙️ Conversion and content tools to help you extend and customize Quranic data
* 📱 Frontend apps using **Next.js** and **PWA** technologies

Whether you're building an educational platform, a personal Quran app, or integrating spiritual content into your existing products, `nq-api` provides a fast, developer-friendly, and scalable foundation.

If you're looking to get started quickly without hosting the API yourself, consider using our SDK or ready-to-use hosted services at [natiq.net](https://natiq.net). But if you want full control, continue below to self-host it easily.

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

---
## 📑 Table of Contents

* [API Endpoints](#api-endpoints)
* [Key Features](#key-features)
---

## API Endpoints

The following are the main API endpoints available:

-   `/users/`: User management.
-   `/groups/`: Group management.
-   `/mushafs/`: Mushaf (Quran version) information.
-   `/surahs/`: List of Surahs.
-   `/ayahs/`: List of Ayahs.
-   `/words/`: List of words.
-   `/translations/`: Available translations.
-   `/ayah-translations/`: Ayah translations.
-   `/recitations/`: Recitation information.
-   `/auth/`: Authentication endpoints.
-   `/profile/`: User profiles.
-   `/phrases/`: Quranic phrases.

## Project Structure

```
nq-api/
├── account/         # User management app
├── api/             # Core API configuration and routing
├── core/            # Core functionalities
├── data/            # Data files
├── quran/           # Quran-related app (Surahs, Ayahs, etc.)
├── .dockerignore
├── .gitignore
├── docker-compose.yaml
├── Dockerfile
├── entrypoint.prod.sh
├── install.sh
├── LICENSE
├── manage.py
├── nginx.conf
├── README.md
└── requirements.txt
```

## Installation & Setup

### With Dokcer
