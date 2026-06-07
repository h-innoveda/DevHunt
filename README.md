# DevHunt — AI Assistant

A local-first, self-hosted AI assistant for problem solving, debugging, learning, and answering any question. Powered by Google's free Gemini & Gemma models. No subscriptions. No data sent to third-party services. Runs entirely on your machine.

---

## Created By

| | |
|---|---|
| **Name** | Hitesh Solanki |
| **Website** | [hiteshsolanki.in](https://hiteshsolanki.in) |
| **Email** | solankihiteshpankajbhai7@gmail.com |
| **Mobile** | +91 9327810431 |

---

## What it does

- **AI Assistant** — streaming chat that answers any question, helps debug errors, explains concepts, and writes code
- **Knowledge Base (RAG)** — index your PDFs, notes, and URLs so the AI can reference them in answers
- **Learning Path** — AI-generated day-by-day learning roadmap tailored to your goals
- **Quest Board** — Kanban-style task board with AI auto-detection of tasks from chat
- **Terminal Stats** — study hours, streaks, consistency score, skills progress
- **API Key Manager** — rotate multiple Gemini API keys with automatic cooldown on rate limits
- **Chat History Viewer** — browse all past conversations in-app
- **Backup & Restore** — export everything to a single JSON file, import it back anytime
- **System Logs** — real-time log viewer with filters by level and category

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, Flask 3.0 |
| AI SDK | `google-genai` v2.8+ |
| Models | Gemini 3.1 Flash-Lite (default), Gemini 2.5 Flash (RAG), Gemma 4 26B |
| Embeddings | `gemini-embedding-2` |
| Database | SQLite (local, zero-config) |
| Frontend | Vanilla HTML / CSS / JS — no framework, no build step |

---

## Project Structure

```
Local-AI/
├── backend/
│   ├── app.py                # Flask API server — all endpoints
│   ├── config.py             # Paths, constants, encryption setup
│   ├── requirements.txt      # Python dependencies
│   ├── core/
│   │   ├── chat_engine.py    # Chat + streaming response logic
│   │   ├── rag_pipeline.py   # PDF/URL/note indexing + similarity search
│   │   ├── key_manager.py    # API key rotation, cooldown, encryption
│   │   ├── model_selector.py # Picks the right model per query type
│   │   ├── learning_path.py  # AI-generated roadmap logic
│   │   ├── todo_manager.py   # Quest board CRUD
│   │   ├── profile_manager.py# User profile & settings
│   │   ├── analytics.py      # Study stats & skills matrix
│   │   ├── intent_detector.py# Detects task intent from chat messages
│   │   ├── logger.py         # System log writer/reader
│   │   └── db.py             # SQLite init & connection helper
│   └── data/
│       ├── devhunt.db        # SQLite database (auto-created)
│       ├── keys.json         # Encrypted API keys (auto-created)
│       ├── profile.json      # User profile (auto-created)
│       ├── settings.json     # App settings (auto-created)
│       └── learning_path.json# Current roadmap (auto-created)
├── frontend/
│   ├── index.html            # Main dashboard
│   ├── logs.html             # System logs page
│   ├── app.js                # All frontend logic
│   └── styles.css            # Dark theme UI
├── run.bat                   # Windows launcher — starts server + opens browser
├── run.sh                    # Linux/macOS launcher
└── README.md
```

---

## Setup

### Prerequisites

- Python 3.10 or higher
- A Google Gemini API key (free) — get one at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

### 1. Get the project

```bash
git clone <your-repo-url>
cd Local-AI
```

### 2. Create virtual environment and install dependencies

```bash
cd backend
python -m venv venv
```

**Windows:**
```cmd
venv\Scripts\pip install -r requirements.txt
```

**Linux / macOS:**
```bash
venv/bin/pip install -r requirements.txt
```

### 3. Run the app

**Windows — double-click `run.bat`** or from terminal:
```cmd
run.bat
```

**Linux / macOS:**
```bash
bash run.sh
```

**Manual start:**
```bash
# Windows
cd backend && venv\Scripts\python app.py

# Linux/macOS
cd backend && venv/bin/python app.py
```

The server starts at **http://localhost:5000** and the launcher scripts automatically detect and open your browser.

### 4. Add your API key

1. Open **http://localhost:5000**
2. Go to **Settings & Nodes** in the sidebar
3. Paste your Gemini API key and click **+ Register Key**

---

## Free Tier Model Limits

| Model | Use case | RPM | Daily limit |
|---|---|---|---|
| `gemini-3.1-flash-lite` | All regular chat (default) | 15 | 500/day |
| `gemini-2.5-flash` | RAG queries | 5 | 20/day |
| `gemma-4-26b-a4b-it` | Heavy reasoning | 15 | 1,500/day |
| `gemini-embedding-2` | Vector embeddings | 100 | 1,000/day |

Add multiple API keys from different Google accounts — DevHunt automatically rotates them when rate limits are hit.

---

## Key Features

### Streaming Chat
Responses appear token-by-token as the model generates them — no waiting for the full response.

### Knowledge Base
Upload PDF files, paste URLs to scrape, or write notes. The AI references them in answers and cites the source.

### API Key Rotation
Multiple keys can be registered. When one hits its rate limit, the system automatically switches to the next available key.

### Backup & Restore
Export everything — chat history, API keys (encrypted), profile, settings, and learning path — as a single JSON file. Import it back on any machine.

### System Logs
Live log viewer at `/logs` with filters by level (INFO / SUCCESS / WARN / ERROR) and category (api_call / key_event / chat / rag / backup).

---

## API Reference

### Chat
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/chat` | Send message, get full response |
| POST | `/api/chat/stream` | Send message, stream tokens (SSE) |
| GET | `/api/chat/history` | Get chat history for a session |
| DELETE | `/api/chat/history` | Clear chat history for a session |

### Keys
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/keys` | List all registered keys |
| POST | `/api/keys` | Add a new key |
| PUT | `/api/keys/<id>` | Enable or disable a key |
| DELETE | `/api/keys/<id>` | Remove a key |
| POST | `/api/keys/<id>/test` | Live-test a specific key |

### Backup
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/backup/export` | Download full backup JSON |
| POST | `/api/backup/import` | Upload and restore a backup |
| GET | `/api/history/export` | Download chat history JSON |

### System
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/logs` | Get system logs |
| DELETE | `/api/logs` | Clear system logs |
| POST | `/api/reset` | Reset all data (irreversible) |

---

## Notes

- No `.env` file needed. The encryption key for API key storage is auto-generated on first run and saved to `backend/data/.secret`. Keep this file if you want to restore encrypted key backups.
- All data stays local — nothing leaves your machine except the API calls to Google.
- The `data/` folder contains your database and settings. Back it up to preserve your history.

---

## License

MIT — free to use, modify, and distribute.

---

*Built by [Hitesh Solanki](https://hiteshsolanki.in)*
