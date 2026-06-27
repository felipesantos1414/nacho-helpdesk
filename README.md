# 🐾 Nacho — AI HelpDesk Assistant

> **CS50x Final Project** | An intelligent IT support assistant with a Beagle personality
> Video demo: https://www.youtube.com/watch?v=EXc5OcwLSFs

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Claude AI](https://img.shields.io/badge/Claude-AI-D97757?style=flat)](https://anthropic.com)

---

## 📖 About the Project

**Nacho** is a bilingual (🇧🇷 PT / 🇬🇧 EN) IT HelpDesk chatbot built as the final project for CS50x. It solves the **14 most common IT problems** using keyword matching against a SQLite database, with optional AI-enhanced responses via the Anthropic Claude API.

The project was designed to simulate a real corporate helpdesk tool, complete with a chat interface, an admin dashboard, and session-based security to prevent off-topic usage.

### Why Nacho?
The assistant is named after a real Beagle dog. The color palette, personality, and UI were all inspired by the breed — brown, warm, and always ready to help. 🐾

---

## ✨ Features

| Feature | Description |
|---|---|
| 💬 Smart chat | Keyword-based matching against 14 IT problems |
| 🌐 Bilingual | Full PT 🇧🇷 / EN 🇬🇧 support — UI and responses |
| 🤖 AI-enhanced | Optional Claude API for natural language responses |
| 📊 Admin dashboard | Live stats: interactions, resolution rate, top issues |
| 🔒 Session security | Auto-closes after 3 off-topic messages |
| 👍 Feedback system | Per-response helpful/not helpful rating |
| 📱 Responsive | Works on desktop and mobile |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3 + Flask |
| Database | SQLite (14 problems, bilingual solutions) |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| AI | Anthropic Claude API (optional) |
| Deploy | Render + Gunicorn |

---

## 🚀 Running Locally

**1. Clone and install**
```bash
git clone https://github.com/felipesantos1414/nacho-helpdesk.git
cd nacho-helpdesk
pip install -r requirements.txt
```

**2. (Optional) Add Claude API key for AI responses**
```bash
# Windows
set ANTHROPIC_API_KEY=your-key-here

# Mac/Linux
export ANTHROPIC_API_KEY=your-key-here
```

**3. Run**
```bash
python app.py
```

- Chat: http://localhost:5000
- Dashboard: http://localhost:5000/dashboard

> Without the API key, Nacho uses the database solutions directly — works perfectly.

---

## 🗂️ Project Structure

```
nacho-helpdesk/
├── app.py                  # Flask app — routes, chat logic, AI integration
├── requirements.txt
├── render.yaml             # Render.com deploy config
├── database/
│   └── init_db.py          # SQL schema + 14 bilingual problems seed
├── templates/
│   ├── index.html          # Chat interface
│   └── dashboard.html      # Admin statistics panel
└── static/
    ├── css/
    │   ├── style.css       # Global styles (Beagle color theme)
    │   └── dashboard.css   # Dashboard styles
    ├── js/
    │   ├── chat.js         # Chat logic + i18n language system
    │   ├── translations.js # PT/EN translation strings
    │   └── dashboard.js    # Dashboard animations
    └── images/
        └── nacho-photo.png # The real Nacho 🐾
```

---

## 🧠 The 14 HelpDesk Problems

1. VPN access issues
2. Printer not printing
3. Forgotten password
4. Wi-Fi connection error
5. Slow computer
6. Email not working
7. Camera in video calls
8. Software installation blocked
9. Blue screen (BSOD)
10. Missing or deleted files
11. No access to system/platform
12. Microphone not working
13. Windows update stuck
14. Network share not accessible

---

## 🔐 Security Model

- Each conversation has a **unique UUID session**
- After **3 off-topic messages**, the session is automatically closed
- Nacho **only answers IT/HelpDesk questions** — no general purpose use
- No sensitive data is stored — only message text and timestamps

---

## 🎨 Design

Color palette inspired by the Beagle breed:

| Role | Color |
|---|---|
| Sidebar / Header | `#4A2512` Dark brown |
| Accents | `#A0522D` Warm brown |
| Backgrounds | `#F5EBE0` Cream |
| CTA buttons | `#E8712A` Orange |

---

## 📸 Screenshots

> Chat interface with dark WhatsApp-style header and bilingual support

---

## 👤 Author

**Felipe Santos**
CS50x — Harvard University (2025)

---

*Nacho approved! 🐾*
