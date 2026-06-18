# 🌌 DevHunt — Local-First AI Assistant for Developers

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform: Windows | macOS | Linux](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()
[![Docker: Available](https://img.shields.io/badge/Docker-Available-2496ED.svg)](https://hub.docker.com/r/hitessolanki/dev-hunt)

**DevHunt** is a local-first, self-hosted developer productivity workspace. Designed for absolute privacy, it combines **Streaming Chat**, a **Knowledge Base (RAG)**, **Quest Board (Todo Kanban)**, and a **Learning Path generator** into a single cohesive system powered by free-tier Gemini API keys and local embedding pipelines.

> **No subscriptions. No third-party data tracking. Everything is stored on your machine.**

---

## 🚀 Key Features

- **🛠️ Self-Healing Setup** — Auto-verify Python, rebuild venv, skip dependency checks on re-runs
- **🖥️ Hunt Terminal CLI** — Cross-platform shell commands, todo management, API testing
- **🗺️ Interactive Learning Paths** — AI-generated learning roadmaps with daily milestones
- **🧠 Long-Term Memory** — Consolidated facts & preferences from conversations to SQLite
- **📡 Auto-Updater** — Git pull releases with announcements tab
- **🔄 Key Rotation** — Multiple Gemini API keys with round-robin & rate-limit handling
- **📚 Knowledge Base (RAG)** — Index PDFs/notes, split-screen document analysis
- **🌐 URL Scraper** — Web documentation ingestion with SSL fallback
- **📊 Activity Logging** — Comprehensive SQLite logs with filters (chat, terminal, todos)
- **🎮 Game Arcade** — Developer-themed offline games with canvas rendering
- **📐 Layout Customization** — Collapsible sidebar, tabbed editing, code formatting
- **🎨 Multi-Theme** — Industrial Slate, Minimalist Light, Devil Version, Cyberpunk Neon
- **🔤 Custom Fonts** — 8 Google Fonts with dynamic UI typography selection

---

## 📋 System Requirements

### Required
- **OS**: Windows 10/11, macOS Big Sur+, or Ubuntu 20.04+
- **Python**: 3.10 or higher
- **Internet**: Required for Gemini API communication
- **Browser**: Chrome, Edge, Firefox, or Safari

### Optional (for Docker)
- **Docker**: Latest version (for containerized deployment)
- **Docker Compose**: For multi-container orchestration

---

## ⚡ Quick Start

### Option A: Native Installation (Development)

1. **Clone Repository**
   ```bash
   git clone https://github.com/h-innoveda/DevHunt.git
   cd web-hunt
   ```

2. **Run Launcher**
   
   **Windows:**
   ```cmd
   run.bat
   ```
   
   **macOS/Linux:**
   ```bash
   chmod +x run.sh && ./run.sh
   ```

3. **Register API Key**
   - Get free key: [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Navigate to Settings → Register Key

4. **Connect CLI (Optional)**
   ```cmd
   hunter.bat -dt     # Windows
   ./hunter -dt       # macOS/Linux
   ```

### Option B: Docker Deployment (Production)

1. **Build & Run**
   ```bash
   docker build -t hitessolanki/dev-hunt:latest .
   docker run -d -p 1225:8080 --name dev-hunt hitessolanki/dev-hunt:latest
   ```
   
   Open: `http://localhost:1225`

2. **Docker Compose (Persistent)**
   ```yaml
   version: '3.8'
   services:
     dev-hunt:
       image: hitessolanki/dev-hunt:latest
       container_name: dev-hunt
       ports:
         - "1225:8080"
       volumes:
         - dev-hunt-data:/app/backend/data
         - dev-hunt-uploads:/app/backend/uploads
       environment:
         - PYTHONUNBUFFERED=1
       restart: unless-stopped
   volumes:
     dev-hunt-data:
     dev-hunt-uploads:
   ```
   
   ```bash
   docker-compose up -d
   ```

3. **Docker Image Info**
   - Base: `python:3.11-slim` (~70–90 MB)
   - Runtime: tesseract, poppler (~50–150 MB)
   - Python packages: ~350–600 MB
   - **Final size: ~534.9 MB compressed**
   - Multi-stage build (builder discarded)

4. **Push to Docker Hub**
   ```bash
   docker push hitessolanki/dev-hunt:latest
   ```

---

## 📁 Repository Structure

```
web-hunt/
├── backend/
│   ├── app.py                      # Flask API (40+ endpoints)
│   ├── config.py                   # Configuration & encryption
│   ├── requirements.txt             # Python dependencies
│   ├── check_requirements.py        # Fast dependency checker
│   ├── hunter_cli.py               # CLI connection client
│   ├── core/
│   │   ├── chat_engine.py          # SSE streaming & tag extraction
│   │   ├── rag_pipeline.py         # Vector ingestion & search
│   │   ├── key_manager.py          # API key rotation
│   │   ├── todo_manager.py         # Quest board CRUD
│   │   ├── learning_path.py        # AI roadmap generation
│   │   ├── update_manager.py       # Git auto-updater
│   │   ├── terminal_engine.py      # Hunt CLI execution
│   │   ├── memory_manager.py       # Long-term memory
│   │   ├── profile_manager.py      # User settings
│   │   ├── analytics.py            # Usage & streaks
│   │   ├── document_analyzer.py    # Document processing
│   │   ├── intent_detector.py      # Intent classification
│   │   ├── logger.py               # Activity logging
│   │   ├── model_selector.py       # Model selection
│   │   └── db.py                   # SQLite management
│   └── data/
│       └── learning_path.json      # Default learning paths
├── frontend/
│   ├── index.html                  # Main UI
│   ├── logs.html                   # Logs dashboard
│   ├── docs.html                   # Documentation
│   ├── app.js                      # SSE handlers & state
│   ├── arcade.js                   # Game canvas logic
│   ├── styles.css                  # Themes & styling
│   └── assets/                     # Images & resources
├── docs/
│   ├── api_analysis.md             # API security analysis
│   ├── app_endpoints.md            # Endpoint documentation
│   ├── chat_engine.md              # Chat system docs
│   ├── memory_manager.md           # Memory system docs
│   ├── terminal_engine.md          # Terminal docs
│   ├── hunt_terminal_docs.md       # CLI commands reference
│   └── roadmap.md                  # Development roadmap
├── run.bat                         # Windows launcher
├── run.sh                          # Unix launcher
├── hunter.bat                      # Windows CLI connector
├── hunter                          # Unix CLI connector
├── notifications.json              # System notifications
└── README.md                       # This file
```

---

## 🔌 API Endpoints

DevHunt provides 40+ REST/SSE endpoints organized by domain:

### Chat Endpoints
- `POST /api/chat` — Synchronous chat
- `POST /api/stream` — Streaming chat with SSE
- `GET /api/chat/history` — Conversation history

### Knowledge Base (RAG)
- `POST /api/rag/ingest` — Index documents
- `POST /api/rag/query` — Search knowledge base
- `GET /api/rag/sources` — List indexed sources

### Terminal
- `POST /api/terminal/run` — Execute commands
- `GET /api/terminal/cwd` — Get current directory
- `POST /api/terminal/navigate` — Change directory

### IDE / File Management
- `GET /api/ide/file` — Read file
- `POST /api/ide/file` — Write file
- `POST /api/ide/delete` — Delete file
- `POST /api/ide/rename` — Rename file
- `GET /api/ide/tree` — File tree

### Todo / Quest Board
- `GET /api/todo/list` — Get todos
- `POST /api/todo/create` — Create todo
- `PATCH /api/todo/:id` — Update todo
- `DELETE /api/todo/:id` — Delete todo

### Analytics
- `GET /api/analytics/stats` — Usage statistics
- `GET /api/analytics/streaks` — Activity streaks

See [docs/app_endpoints.md](docs/app_endpoints.md) for complete documentation.

---

## 🔐 Security Features

- **Path Traversal Prevention** — Validated file access with `os.path.realpath()`
- **Command Injection Prevention** — Shell=False subprocess execution with operator validation
- **Request Size Limits** — 32MB max payload to prevent DoS
- **Encrypted API Keys** — Fernet encryption for stored credentials
- **Non-Root Docker User** — Container runs as appuser
- **CORS Configuration** — Configurable origin restrictions
- **Debug Mode Disabled** — Production-ready default settings

---

## 📚 Documentation

- **[API Endpoints](docs/app_endpoints.md)** — Full REST/SSE endpoint reference
- **[Chat Engine](docs/chat_engine.md)** — Streaming & message handling
- **[Terminal Engine](docs/terminal_engine.md)** — Command execution & navigation
- **[Hunt CLI](docs/hunt_terminal_docs.md)** — Command-line interface reference
- **[Memory Manager](docs/memory_manager.md)** — Long-term memory system
- **[Roadmap](docs/roadmap.md)** — Development milestones

---

## 🔄 Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :5000
kill -9 <PID>
```

### Virtual Environment Issues
```bash
# Rebuild venv
rm -rf backend/venv
python -m venv backend/venv
source backend/venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r backend/requirements.txt
```

### Docker Issues
```bash
# View logs
docker logs dev-hunt

# Rebuild image
docker build --no-cache -t hitessolanki/dev-hunt:latest .

# Check container status
docker ps -a
```

### Python Version Error
```bash
# Verify Python version
python --version

# If not 3.10+, download from https://www.python.org/
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see LICENSE file for details.

---

## 💬 Support

For issues, questions, or suggestions:

- **Issues**: [GitHub Issues](https://github.com/h-innoveda/DevHunt/issues)
- **Discussions**: [GitHub Discussions](https://github.com/h-innoveda/DevHunt/discussions)
- **Email**: hitesh.innoveda@gmail.com

---

## 🎯 Roadmap

- [ ] PostgreSQL migration (SQLite → PostgreSQL)
- [ ] Redis caching layer
- [ ] Authentication system
- [ ] Microservices architecture
- [ ] WebSocket support
- [ ] Advanced analytics dashboard
- [ ] Team collaboration features
- [ ] Mobile companion app

See [docs/roadmap.md](docs/roadmap.md) for detailed milestones.

---

**Made with ❤️ by [DevHunt Team](https://github.com/h-innoveda)**

Last updated: June 2026 | Version: 1.0.0
