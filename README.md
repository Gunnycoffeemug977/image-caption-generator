# Image Caption Generator

An enterprise-grade AI image captioning service. Upload a photo or capture one
with your camera, and a vision-capable AI model returns a structured caption,
a detailed description, accessibility-ready alt text, mood, and topic tags -
in real time, with an optional live streaming preview.

Built with **FastAPI**, the **OpenAI Responses API** (vision), **SQLite**, and
a dependency-free HTML/CSS/JavaScript frontend. No build tooling, no
frontend framework, no bloat.

> New to Python, VS Code, Git, or APIs? Read **[INSTRUCTION.md](INSTRUCTION.md)**
> instead - it is a from-zero, step-by-step setup guide written for complete
> beginners.

---

## Table of contents

- [Features](#features)
- [How vision models understand images](#how-vision-models-understand-images)
- [How image captioning works in this app](#how-image-captioning-works-in-this-app)
- [Architecture](#architecture)
- [Project structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the app](#running-the-app)
- [API reference](#api-reference)
- [Testing](#testing)
- [Security notes](#security-notes)
- [License](#license)

---

## Features

| Category | Capability |
|---|---|
| Input | Drag-and-drop upload, click-to-browse upload, live camera capture |
| AI captioning | Standard caption, detailed description, accessibility-first alt text |
| AI output | Structured JSON output (caption, description, alt text, tags, mood, confidence) |
| AI streaming | Token-by-token live preview via Server-Sent Events |
| Output actions | Copy to clipboard, download as a `.txt` file |
| History | Every generated caption is stored locally in SQLite and browsable/downloadable/deletable |
| UI | Dark mode with system-preference detection, fully responsive layout |

## How vision models understand images

Modern multimodal large language models (LLMs) are trained on both text and
images at once. Instead of the older two-stage pipeline (a separate CNN
extracts image "features," then a language model turns those features into
words), a **vision-language model** encodes the image directly into the same
representation space the model uses for text, and reasons over both together
in a single forward pass.

In practice this means the model can:

- Identify objects, people, settings, and actions in a scene
- Read text that appears inside the image
- Reason about spatial relationships ("the cup is to the left of the laptop")
- Infer mood, style, and context, not just literal contents
- Follow natural-language instructions about *how* to describe what it sees

This application sends the uploaded image to the model as a base64-encoded
`input_image` content part alongside a text instruction, using OpenAI's
**Responses API**. The model returns everything in a single call - no
separate object-detection step is needed.

## How image captioning works in this app

1. The browser sends the image file to `POST /api/caption` as `multipart/form-data`.
2. The backend validates the file (type, size) using magic-byte sniffing -
   never trusting the browser-supplied MIME type alone.
3. The image is base64-encoded into a `data:` URL and sent to the OpenAI
   Responses API with:
   - A system instruction tailored to the selected **mode**
     (`standard`, `detailed`, `accessibility`) and **tone**
     (`neutral`, `creative`, `technical`)
   - A **strict JSON Schema** response format, so the model's reply is
     always valid, predictable structured data - not free-form text to parse
4. The structured result (caption, description, alt text, tags, mood) is
   returned to the browser and simultaneously saved to a local SQLite
   database as history.
5. Optionally, `POST /api/caption/stream` asks the same model to narrate the
   image as plain text, streamed to the browser via Server-Sent Events, for
   an immediate "watching it think" preview while the structured request
   completes in the background.

## Architecture

The backend follows **Clean Architecture**: dependencies point inward, and
business logic never imports a web framework or a database driver directly.

```
┌─────────────────────────────────────────────────────────────┐
│  Interface adapters   routes.py, templates/, static/        │
│  (HTTP <-> domain translation, request/response shaping)    │
├─────────────────────────────────────────────────────────────┤
│  Application services  caption_service.py                   │
│  (use cases: validate -> call vision AI -> persist)         │
├─────────────────────────────────────────────────────────────┤
│  Domain                schemas.py, exceptions.py            │
│  (pure data models and typed errors, no I/O)                │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure        openai_client.py, database.py        │
│  (OpenAI SDK calls, SQLite persistence)                     │
└─────────────────────────────────────────────────────────────┘
```

- **`routes.py`** knows about HTTP, but nothing about SQLite or OpenAI.
- **`caption_service.py`** knows the business rules (validate -> generate ->
  store) but nothing about FastAPI or SQL.
- **`openai_client.py`** and **`database.py`** are swappable infrastructure -
  either could be replaced (e.g. Postgres instead of SQLite) without
  touching the service layer.
- **`dependencies.py`** is the composition root that wires these layers
  together for FastAPI's dependency injection system.

This keeps the codebase testable (see `tests/test_services.py`, which tests
business logic with zero HTTP or network dependencies) and easy to extend.

## Project structure

```
image-caption-generator/
├── main.py # FastAPI app: routing, lifespan, error handling
├── routes.py # HTTP route handlers (interface adapters)
├── caption_service.py # Application service / use cases
├── openai_client.py # OpenAI Responses API (vision) wrapper
├── database.py # SQLite repository (async-safe)
├── dependencies.py # Dependency-injection wiring
├── config.py # Environment-driven settings (Pydantic v2)
├── schemas.py # Pydantic v2 request/response models
├── exceptions.py # Typed domain exceptions
├── utils.py # Image validation & formatting helpers
├── logging_config.py # Centralized logging setup
├── requirements.txt # Production dependencies
├── requirements-dev.txt # + testing dependencies
├── .env.example # Environment variable template
├── Start App.bat # One-click launcher (Windows)
├── Start App (Mac).command # One-click launcher (macOS)
├── static/ # CSS, JavaScript, favicon
│   ├── style.css
│   ├── app.js
│   └── favicon.svg
├── templates/
│   └── index.html # Single-page application shell
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   └── test_services.py
├── data/ # SQLite database lives here (gitignored)
├── INSTRUCTION.md # Beginner-friendly setup walkthrough
└── README.md
```

## Installation

Requires **Python 3.12+**.

```bash
git clone https://github.com/your-username/image-caption-generator.git
cd image-caption-generator

python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env # then edit .env and add your OPENAI_API_KEY
```

Prefer a guided, zero-assumptions walkthrough? See **[INSTRUCTION.md](INSTRUCTION.md)**.

## Configuration

All configuration is via environment variables (loaded from `.env`). See
[`.env.example`](.env.example) for the full list. The essentials:

| Variable | Description | Default |
|---|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key (required) | - |
| `OPENAI_MODEL` | Vision-capable model name | `gpt-4o-mini` |
| `MAX_UPLOAD_MB` | Maximum upload size in megabytes | `8` |
| `DATABASE_PATH` | SQLite file location | `data/history.db` |
| `HOST` / `PORT` | Bind address | `127.0.0.1` / `8000` |

## Running the app

```bash
uvicorn main:app --reload
```

Then open **http://127.0.0.1:8000** in your browser.

Windows and macOS users can instead double-click **`Start App.bat`** or
**`Start App (Mac).command`**, which set up the virtual environment,
install dependencies, and launch the app automatically.

## API reference

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | The web application |
| `GET` | `/api/health` | Health check and configuration status |
| `POST` | `/api/caption` | Generate a structured caption for an uploaded image |
| `POST` | `/api/caption/stream` | Stream a plain-text caption preview (SSE) |
| `GET` | `/api/history` | List paginated caption history |
| `GET` | `/api/history/{id}` | Fetch a single history record |
| `GET` | `/api/history/{id}/download` | Download a history record as `.txt` |
| `DELETE` | `/api/history/{id}` | Delete a history record |

Interactive OpenAPI docs are available at **`/docs`** while the server is
running.

## Testing

```bash
pip install -r requirements-dev.txt
pytest
```

The test suite mocks the OpenAI vision client, so it runs fully offline and
does not require an API key or network access.

## Security notes

- Never commit your `.env` file - it is excluded via `.gitignore`.
- The API key lives only in server-side environment variables; it is never
  sent to the browser.
- Uploaded image bytes are validated by magic-byte sniffing, not by trusting
  the client-supplied filename or `Content-Type` header.
- Uploaded images are sent directly to the OpenAI API and are not written to
  disk by this application.

## License

Released under the [MIT License](LICENSE).
