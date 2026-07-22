# INSTRUCTION.md - Complete Beginner's Setup Guide

Welcome! This guide assumes you have **never** used Python, Visual Studio
Code, Git, FastAPI, the OpenAI API, or AI vision/OCR tools before. Every
step is spelled out in full - you will not need to guess anything.

Follow the sections in order. Each one builds on the last.

---

## Table of contents

1. [Installing Python](#1-installing-python)
2. [Installing Visual Studio Code](#2-installing-visual-studio-code)
3. [Installing Git](#3-installing-git)
4. [Required VS Code extensions](#4-required-vs-code-extensions)
5. [Opening the project](#5-opening-the-project)
6. [Creating a virtual environment](#6-creating-a-virtual-environment)
7. [Activating the virtual environment](#7-activating-the-virtual-environment)
8. [Installing dependencies](#8-installing-dependencies)
9. [Creating the .env file](#9-creating-the-env-file)
10. [Obtaining an OpenAI API key](#10-obtaining-an-openai-api-key)
11. [Running the application](#11-running-the-application)
12. [Uploading your first image](#12-uploading-your-first-image)
13. [Testing every feature](#13-testing-every-feature)
14. [Exporting results](#14-exporting-results)
15. [Common errors](#15-common-errors)
16. [Troubleshooting](#16-troubleshooting)
17. [FAQ](#17-faq)
18. [Security recommendations](#18-security-recommendations)
19. [Project architecture](#19-project-architecture)
20. [Next learning steps](#20-next-learning-steps)

---

## 1. Installing Python

Python is the programming language this application is written in. You need
version **3.12 or newer**.

### Windows

1. Open your web browser and go to **https://www.python.org/downloads/**.
2. Click the yellow **"Download Python 3.x.x"** button.
3. Open the downloaded file (it will be named something like
   `python-3.12.x-amd64.exe`).
4. **Important:** On the first installer screen, check the box at the
   bottom that says **"Add python.exe to PATH"**. This step is easy to
   miss and causes most beginner problems later.

   | Screen | What to do |
   |---|---|
   | Install screen | ☑ Check "Add python.exe to PATH" |
   | Install screen | Click "Install Now" |
   | Finish screen | Click "Close" |

5. To confirm it worked, open the **Start Menu**, type `cmd`, and press
   Enter to open Command Prompt. Type:

   ```bash
   python --version
   ```

   Expected output:

   ```
   Python 3.12.4
   ```

   (Any version 3.12 or higher is fine.)

### macOS

1. Go to **https://www.python.org/downloads/** in your browser.
2. Click **"Download Python 3.x.x"** for macOS.
3. Open the downloaded `.pkg` file and follow the installer prompts,
   clicking "Continue" and "Install" on each screen.
4. Open the **Terminal** app (press `Cmd + Space`, type "Terminal", press
   Enter).
5. Confirm the installation:

   ```bash
   python3 --version
   ```

   Expected output:

   ```
   Python 3.12.4
   ```

> **Note:** On macOS, the command is `python3`, not `python`. This guide
> shows both where they differ.

---

## 2. Installing Visual Studio Code

Visual Studio Code ("VS Code") is the free code editor you will use to open
and run this project.

1. Go to **https://code.visualstudio.com/**.
2. Click the big **Download** button (it detects your operating system
   automatically).
3. Run the installer:
   - **Windows:** open the `.exe` file, accept the agreement, keep all
     default options checked (especially "Add to PATH"), click "Next"
     through the screens, then "Install".
   - **macOS:** open the downloaded `.zip`, drag `Visual Studio Code.app`
     into your **Applications** folder.
4. Launch VS Code:
   - **Windows:** Start Menu -> "Visual Studio Code"
   - **macOS:** Applications -> "Visual Studio Code" (or Spotlight search)

You should see a welcome screen. That confirms VS Code is installed.

---

## 3. Installing Git

Git lets you download ("clone") this project's code and, later, track your
own changes. It is optional if you already have the project folder on your
computer, but strongly recommended.

### Windows

1. Go to **https://git-scm.com/download/win**. The download should start
   automatically.
2. Run the installer. The default options are fine for beginners - keep
   clicking "Next" and finish with "Install".
3. Open a **new** Command Prompt window and check:

   ```bash
   git --version
   ```

   Expected output (version number may differ):

   ```
   git version 2.45.0.windows.1
   ```

### macOS

1. Open **Terminal**.
2. Type:

   ```bash
   git --version
   ```

3. If Git is not already installed, macOS will prompt you to install the
   "Command Line Developer Tools." Click **Install** and wait for it to
   finish, then run the command again to confirm.

---

## 4. Required VS Code extensions

Extensions add features to VS Code. Install these two:

1. Open VS Code.
2. Click the **Extensions** icon in the left sidebar (it looks like four
   squares, one detached).
3. Search for and install each of the following (click **Install** on each):

   | Extension | Publisher | Why you need it |
   |---|---|---|
   | Python | Microsoft | Python language support, running/debugging |
   | Pylance | Microsoft | Fast, smart Python autocomplete and error checking |

   Optional but helpful:

   | Extension | Publisher | Why you might want it |
   |---|---|---|
   | Ruff | Astral Software | Highlights style/quality issues in Python code |

This project also includes a `.vscode/extensions.json` file, so when you
open the project folder, VS Code will automatically suggest installing
these for you - just click **"Install"** on the notification that appears.

---

## 5. Opening the project

If you downloaded this project as a `.zip` file:

1. Right-click the `.zip` file and choose **"Extract All..."** (Windows) or
   double-click it (macOS) to unzip it into a folder named
   `image-caption-generator`.

If you are using Git to clone it:

```bash
git clone https://github.com/your-username/image-caption-generator.git
```

Then open the folder in VS Code:

1. In VS Code, go to **File -> Open Folder...** (macOS: **File -> Open...**).
2. Select the `image-caption-generator` folder.
3. Click **"Select Folder"** (Windows) or **"Open"** (macOS).

You should now see the project files listed in the left-hand Explorer
panel, including `main.py`, `README.md`, and `requirements.txt`.

---

## 6. Creating a virtual environment

A **virtual environment** ("venv") is an isolated, private copy of Python
just for this project, so its packages don't conflict with anything else
on your computer. Think of it as a clean toolbox just for this app.

1. Open a terminal inside VS Code: **Terminal -> New Terminal** (or press
   `` Ctrl+` `` on Windows/Linux, `` Cmd+` `` on macOS).
2. Make sure the terminal's current folder is your project folder (it
   should already be, since you opened the project in VS Code).
3. Run:

   **Windows:**
   ```bash
   python -m venv venv
   ```

   **macOS:**
   ```bash
   python3 -m venv venv
   ```

4. Wait a few seconds. This creates a new folder named `venv/` inside your
   project. You will see it appear in the Explorer panel on the left.

> You only need to do this **once** per project. The `Start App` scripts
> described in [Section 11](#11-running-the-application) will also do this
> for you automatically if you skip this step.

---

## 7. Activating the virtual environment

"Activating" tells your terminal to use the isolated Python copy instead of
your computer's main Python installation.

**Windows (Command Prompt):**
```bash
venv\Scripts\activate
```

**Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

After running this, your terminal prompt should now start with `(venv)`,
like this:

```
(venv) C:\Users\you\image-caption-generator>
```

```
(venv) you@MacBook image-caption-generator %
```

If you see `(venv)` at the start of the line, it worked. You will need to
activate the virtual environment every time you open a new terminal window
to work on this project (the `Start App` scripts do this automatically).

---

## 8. Installing dependencies

"Dependencies" are the external packages this project needs (FastAPI,
the OpenAI SDK, etc.). With your virtual environment **activated** (see
Section 7), run:

```bash
pip install -r requirements.txt
```

You will see a series of lines like `Collecting fastapi...`,
`Installing collected packages...`, ending with something like:

```
Successfully installed fastapi-0.115.6 openai-1.59.7 pydantic-2.10.4 ...
```

This step downloads everything the app needs. It typically takes under a
minute on a normal internet connection.

---

## 9. Creating the .env file

The `.env` file stores your personal configuration - most importantly,
your OpenAI API key - **outside** of the code, so it's never accidentally
shared or committed to Git.

1. In the project folder, find the file named **`.env.example`**.
2. Make a copy of it named exactly **`.env`** (no other text before or
   after - just a period and "env").

   **Windows (Command Prompt):**
   ```bash
   copy .env.example .env
   ```

   **macOS / Linux:**
   ```bash
   cp .env.example .env
   ```

3. Open `.env` in VS Code by clicking it in the Explorer panel. It will
   look like this:

   ```ini
   OPENAI_API_KEY=sk-your-api-key-here
   OPENAI_MODEL=gpt-4o-mini
   OPENAI_TIMEOUT_SECONDS=60

   APP_NAME=Image Caption Generator
   APP_VERSION=1.0.0
   APP_ENV=development
   HOST=127.0.0.1
   PORT=8000

   MAX_UPLOAD_MB=8
   ALLOWED_IMAGE_TYPES=image/jpeg,image/png,image/webp

   DATABASE_PATH=data/history.db

   LOG_LEVEL=INFO
   ```

4. Leave everything as-is for now - you'll fill in `OPENAI_API_KEY` in the
   next section.

---

## 10. Obtaining an OpenAI API key

An **API key** is like a password that lets this application make requests
to OpenAI's vision models on your behalf. OpenAI meters usage by this key
and (typically) bills a small amount per request.

1. Go to **https://platform.openai.com/signup** and create an account (or
   sign in if you already have one).
2. Once logged in, go to **https://platform.openai.com/api-keys**.
3. Click **"Create new secret key"**.
4. Give it a name (e.g. "image-caption-generator") and click **"Create
   secret key"**.
5. **Copy the key immediately** - it starts with `sk-` and is only shown
   once. Store it somewhere safe (like a password manager).
6. You may also need to add billing details at
   **https://platform.openai.com/account/billing** before the key will
   work - OpenAI's vision models are paid, usage-based services.
7. Open your `.env` file in VS Code and replace the placeholder line:

   ```ini
   OPENAI_API_KEY=sk-your-api-key-here
   ```

   with your real key, e.g.:

   ```ini
   OPENAI_API_KEY=sk-proj-abc123...your-real-key...xyz
   ```

8. Save the file (`Ctrl+S` / `Cmd+S`).

> **Never share this key or commit it to GitHub.** Treat it like a
> password. See [Section 18](#18-security-recommendations) for more.

---

## 11. Running the application

You have two options.

### Option A: One-click startup scripts (easiest)

- **Windows:** double-click **`Start App.bat`** in the project folder.
- **macOS:** double-click **`Start App (Mac).command`** in the project
  folder. (If macOS blocks it the first time, right-click the file, choose
  **"Open"**, then confirm **"Open"** in the security dialog.)

These scripts automatically create the virtual environment, activate it,
install dependencies, check your `.env` file, and start the server -
everything from Sections 6-11 in one step. A terminal window will open and
stay open showing progress and logs; if something goes wrong, the window
stays open so you can read the error message.

### Option B: Manual startup (more control)

With your virtual environment activated (Section 7) and dependencies
installed (Section 8):

```bash
uvicorn main:app --reload
```

You should see output ending with something like:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### Opening the app

Open your web browser and go to:

```
http://127.0.0.1:8000
```

You should see the **Image Caption Generator** interface, with a large
upload area at the top.

**Expected output when everything is correctly configured:** a clean web
page with a dashed "viewfinder" upload box, a set of dropdown menus below
it (Mode, Tone, Language, Live preview), a disabled "Generate caption"
button (it enables once you pick an image), and an empty "History" section
at the bottom.

---

## 12. Uploading your first image

1. Click anywhere inside the dashed upload box, **or** drag an image file
   from your computer directly onto it.
2. Choose a JPEG, PNG, or WEBP image up to 8 MB.
3. A preview of your image will appear inside the box, and the
   **"Generate caption"** button will become active (no longer greyed out).
4. Click **"Generate caption"**.
5. After a moment (typically 2-6 seconds), a result card will appear below
   showing:
   - **Caption** - a short, natural description
   - **Alt text** - an accessibility-friendly description
   - **Tags** - keyword chips describing the contents
   - **Confidence** - a visual indicator bar

---

## 13. Testing every feature

Work through this checklist to confirm everything works end to end.

| # | Feature | How to test | Expected result |
|---|---|---|---|
| 1 | Image upload | Drag a photo onto the upload box | Preview appears, Generate button enables |
| 2 | Camera upload | Click "Use camera", allow permission | Browser camera opens, a photo is captured and previewed |
| 3 | Standard caption | Set Mode = "Standard caption", click Generate | Short one/two sentence caption appears |
| 4 | Detailed description | Set Mode = "Detailed description", click Generate | A "Detailed description" section appears with multiple sentences |
| 5 | Accessibility mode | Set Mode = "Accessibility mode", click Generate | Result card header reads "Alt text" and content is objective/descriptive |
| 6 | Tone options | Try "Creative" and "Technical" tones | Caption wording noticeably changes style |
| 7 | Streaming | Check "Stream caption as it's written", click Generate | A "Live preview" card fills in text progressively before the final card appears |
| 8 | Copy caption | Click the "Copy" button | A toast reading "Copied to clipboard" appears; paste elsewhere to confirm |
| 9 | Download caption | Click the "Download" button | A `caption.txt` file is saved to your Downloads folder |
| 10 | History | Generate 2-3 captions, then look at the History section | Each generated caption is listed with filename and timestamp |
| 11 | History download | Click the download icon on a history row | A `.txt` file downloads with that record's full details |
| 12 | History delete | Click the delete icon on a history row | The row disappears; refresh confirms it stays gone |
| 13 | Dark mode | Click the sun/moon icon top-right | The entire interface switches color themes instantly |
| 14 | Responsive design | Resize your browser window narrower, or open on a phone | Layout reflows to a single column, all controls remain usable |

---

## 14. Exporting results

There are two ways to save a caption outside the app:

1. **Copy to clipboard** - click **Copy** next to the caption, then paste
   (`Ctrl+V` / `Cmd+V`) into any document, email, or chat.
2. **Download as a text file** - click **Download** to save a `.txt` file
   containing the caption, detailed description, alt text, tags, and mood.
   You can also download any past result from the **History** list using
   its download icon, which additionally includes the model name and
   timestamp.

---

## 15. Common errors

| Error message | What it means | Fix |
|---|---|---|
| `'python' is not recognized as an internal or external command` | Python is not installed, or wasn't added to PATH | Reinstall Python and check "Add python.exe to PATH" (Section 1) |
| `The server is missing an OPENAI_API_KEY` (banner in the app) | `.env` still has the placeholder key, or is missing | Follow Section 9 and 10 to set a real key, then restart the app |
| `ModuleNotFoundError: No module named 'fastapi'` | Dependencies weren't installed, or your venv isn't activated | Run Section 7 (activate) then Section 8 (install) again |
| `Address already in use` / `port 8000 is already in use` | Another program (often a previous run of this app) is using port 8000 | Close the other terminal window, or change `PORT` in `.env` |
| `The vision service returned an error: Incorrect API key provided` | Your API key is invalid, expired, or mistyped | Generate a new key (Section 10) and paste it carefully into `.env` |
| `Image is too large` | Your file exceeds the 8 MB limit | Use a smaller image, or raise `MAX_UPLOAD_MB` in `.env` |
| `Unsupported image format` | You uploaded something other than JPEG/PNG/WEBP | Convert or choose a different image |
| Camera button does nothing | Browser blocked camera permission, or no camera is present | Check your browser's site permissions and allow camera access |
| macOS says "app can't be opened because it is from an unidentified developer" | macOS Gatekeeper is blocking the `.command` script | Right-click the file -> Open -> confirm Open |

---

## 16. Troubleshooting

**The page loads but shows a red banner about the API key.**
Your `.env` file is missing a valid `OPENAI_API_KEY`. Fix it (Sections 9-10)
and restart the app - environment variables are only read on startup.

**Nothing happens when I click "Generate caption."**
Open your browser's developer console (`F12` or `Cmd+Option+I`) and check
the "Console" and "Network" tabs for errors. Confirm the terminal running
the app is still open and shows no errors.

**The terminal window closes immediately when I double-click the startup
script.**
This usually means an error occurred instantly (e.g. Python not found).
Open a regular terminal, navigate to the project folder, and run the
script manually so the output stays visible:

```bash
# Windows (Command Prompt)
"Start App.bat"

# macOS (Terminal)
bash "Start App (Mac).command"
```

**Dependency installation fails partway through.**
Check your internet connection. If you're behind a corporate proxy or
firewall, you may need to configure `pip` to use it, or try again on a
different network.

**I changed `.env` but nothing changed.**
Environment variables are loaded once when the app starts. Stop the server
(`Ctrl+C` in the terminal) and start it again.

**I want to start over completely.**
Delete the `venv/` folder and the `data/` folder's `.db` file, then repeat
Sections 6-9.

---

## 17. FAQ

**Do I need to know how to code to use this app?**
No - end users just need Sections 1-13. Understanding the code (Section 19)
is only necessary if you want to modify or extend the project.

**Does this cost money?**
Running the app itself is free. Each caption generation makes a request to
OpenAI's API, which is billed per OpenAI's own pricing (see
https://openai.com/api/pricing/). Vision requests on small models are
typically fractions of a cent each, but costs depend on your usage volume.

**Can I use a different AI provider instead of OpenAI?**
The vision integration lives entirely in `openai_client.py`. You could
adapt this file to call a different provider's vision API, as long as it
returns comparable structured output - but that requires code changes and
is not covered by this guide.

**Where is my caption history stored?**
Locally, in a SQLite database file at `data/history.db` on your own
computer. Nothing is stored on any external server except the images
briefly sent to OpenAI for analysis (OpenAI's own data retention policy
applies to that transient request).

**What does "OCR" mean, and does this app use it?**
OCR ("Optical Character Recognition") is the process of reading text out
of an image. This app doesn't run a separate OCR engine - the vision model
itself can read and describe text it sees in a photo as part of its normal
understanding of the image.

**Can multiple people use this app at once?**
The included setup runs a single local server intended for one person's
use on their own computer. Running it for multiple simultaneous users
would require additional work (a shared deployment, authentication, rate
limiting) beyond the scope of this project.

**Why doesn't the app save my uploaded photos?**
By design, for privacy: only the generated caption text is stored in
history, not the image itself.

---

## 18. Security recommendations

- **Never commit `.env` to Git or share it.** It contains your private API
  key. The included `.gitignore` already excludes it, but always double
  check before sharing your project folder.
- **Rotate your API key** if you ever suspect it has been exposed (visit
  https://platform.openai.com/api-keys and delete/regenerate it).
- **Set spending limits** on your OpenAI account
  (https://platform.openai.com/account/limits) so an unexpected usage spike
  can't result in a large bill.
- **Don't expose this app to the public internet** as-is. It has no user
  authentication; anyone who can reach it could generate captions using
  your API key and budget. Keep `HOST=127.0.0.1` for local-only use.
- **Keep dependencies up to date** periodically with
  `pip install -r requirements.txt --upgrade` to receive security fixes.

---

## 19. Project architecture

This project follows **Clean Architecture**: code is organized in layers,
with business logic kept independent of frameworks and infrastructure.

```
Browser (HTML/CSS/JS)
        │  HTTP requests
        ▼
routes.py            -> translates HTTP requests into service calls
        │
        ▼
caption_service.py   -> business logic: validate -> call AI -> save
        │                              │
        ▼                              ▼
openai_client.py               database.py
(OpenAI Responses API)         (SQLite storage)
```

- **`main.py`** creates the FastAPI application, wires up routers, and
  handles startup/shutdown and error translation.
- **`routes.py`** defines each HTTP endpoint (`/api/caption`,
  `/api/history`, etc.) and delegates all real work to `caption_service.py`.
- **`caption_service.py`** contains the actual business rules: validating
  uploads, calling the AI, and persisting results. It knows nothing about
  HTTP or SQL directly.
- **`openai_client.py`** is the only file that talks to OpenAI. It builds
  prompts, defines the structured JSON schema, and parses responses.
- **`database.py`** is the only file that talks to SQLite.
- **`schemas.py`** defines the shape of data flowing through the app using
  Pydantic v2 models.
- **`exceptions.py`** defines typed errors so failures are handled
  consistently and translated into clean HTTP responses in `main.py`.
- **`config.py`** reads all settings from environment variables in one
  place.
- **`static/` and `templates/`** contain the plain HTML/CSS/JavaScript
  frontend - no build step or framework required.

This separation means, for example, you could swap SQLite for another
database, or add a second AI provider, by changing only one file, without
touching the web layer or the frontend.

---

## 20. Next learning steps

If this project sparked your interest in the technologies it uses, here
are good next places to learn more:

| Topic | Where to learn more |
|---|---|
| Python basics | https://docs.python.org/3/tutorial/ |
| FastAPI | https://fastapi.tiangolo.com/tutorial/ |
| Pydantic (data validation) | https://docs.pydantic.dev/latest/ |
| REST APIs in general | https://developer.mozilla.org/en-US/docs/Glossary/REST |
| OpenAI API & vision models | https://platform.openai.com/docs |
| SQL and SQLite | https://www.sqlitetutorial.net/ |
| Git & GitHub basics | https://docs.github.com/en/get-started |
| HTML/CSS/JavaScript | https://developer.mozilla.org/en-US/docs/Learn |
| Clean Architecture concepts | Search "Clean Architecture Robert C. Martin" for the original book and talks |

A natural next project: try adding a new caption **mode** (for example,
"social media caption" with hashtags) by extending `schemas.py`,
`openai_client.py`, and the dropdown in `templates/index.html`. That one
small change touches every layer of the architecture and is a great way to
learn how the pieces fit together.

---

You're all set. If you run into anything not covered here, re-read
[Section 15](#15-common-errors) and [Section 16](#16-troubleshooting), or
check the interactive API docs at `http://127.0.0.1:8000/docs` once the
app is running.
