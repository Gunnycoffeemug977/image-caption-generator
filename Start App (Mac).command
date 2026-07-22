#!/usr/bin/env bash
#
# Image Caption Generator - macOS startup script.
# Double-click this file in Finder (or run it in Terminal) to set up and
# launch the application automatically.

set -u
cd "$(dirname "$0")"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

error_exit() {
    echo ""
    echo -e "${RED}------------------------------------------------------------${NC}"
    echo -e "${RED}  Startup did not complete successfully.${NC}"
    echo -e "${RED}  Review the messages above, or see INSTRUCTION.md for help.${NC}"
    echo -e "${RED}------------------------------------------------------------${NC}"
    echo ""
    read -n 1 -s -r -p "Press any key to close this window..."
    exit 1
}

echo "============================================================"
echo "  Image Caption Generator - Startup"
echo "============================================================"
echo ""

# ---------------------------------------------------------------
# 1. Verify Python is installed
# ---------------------------------------------------------------
echo "[1/6] Checking for Python..."

PYTHON_BIN=""
for candidate in python3.13 python3.12 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
        PYTHON_BIN="$candidate"
        break
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo ""
    echo -e "${RED}ERROR: Python was not found on this computer.${NC}"
    echo "Please install Python 3.12 or newer from https://www.python.org/downloads/"
    echo "See INSTRUCTION.md for a full step-by-step guide."
    error_exit
fi

PY_VERSION=$("$PYTHON_BIN" --version 2>&1)
echo -e "      Found ${GREEN}${PY_VERSION}${NC} (using '$PYTHON_BIN')"
echo ""

# ---------------------------------------------------------------
# 2. Create a virtual environment if it does not already exist
# ---------------------------------------------------------------
echo "[2/6] Checking for virtual environment..."
if [ ! -f "venv/bin/activate" ]; then
    echo "      No virtual environment found. Creating one now..."
    "$PYTHON_BIN" -m venv venv
    if [ $? -ne 0 ]; then
        echo ""
        echo -e "${RED}ERROR: Failed to create the virtual environment.${NC}"
        error_exit
    fi
    echo "      Virtual environment created."
else
    echo "      Virtual environment already exists."
fi
echo ""

# ---------------------------------------------------------------
# 3. Activate the virtual environment
# ---------------------------------------------------------------
echo "[3/6] Activating virtual environment..."
# shellcheck disable=SC1091
source "venv/bin/activate"
if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}ERROR: Failed to activate the virtual environment.${NC}"
    error_exit
fi
echo "      Activated."
echo ""

# ---------------------------------------------------------------
# 4. Install dependencies
# ---------------------------------------------------------------
echo "[4/6] Installing dependencies (this may take a minute the first time)..."
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}ERROR: Failed to install required Python packages.${NC}"
    echo "Check your internet connection and try again."
    error_exit
fi
echo "      Dependencies installed."
echo ""

# ---------------------------------------------------------------
# 5. Verify the .env file exists and contains an API key
# ---------------------------------------------------------------
echo "[5/6] Checking configuration..."
if [ ! -f ".env" ]; then
    echo "      No .env file found. Creating one from .env.example..."
    cp ".env.example" ".env"
    echo ""
    echo -e "${YELLOW}============================================================${NC}"
    echo -e "${YELLOW}  ACTION REQUIRED${NC}"
    echo    "  A new .env file was created for you."
    echo    "  Open it in a text editor and set OPENAI_API_KEY to your"
    echo    "  own OpenAI API key, then run this script again."
    echo    "  See INSTRUCTION.md, section 'Obtaining an OpenAI API key'."
    echo -e "${YELLOW}============================================================${NC}"
    error_exit
fi

if grep -q "OPENAI_API_KEY=sk-your-api-key-here" ".env"; then
    echo ""
    echo -e "${YELLOW}============================================================${NC}"
    echo -e "${YELLOW}  ACTION REQUIRED${NC}"
    echo    "  Your .env file still contains the placeholder API key."
    echo    "  Open .env in a text editor and replace it with your real"
    echo    "  OpenAI API key, then run this script again."
    echo    "  See INSTRUCTION.md, section 'Obtaining an OpenAI API key'."
    echo -e "${YELLOW}============================================================${NC}"
    error_exit
fi
echo "      Configuration looks good."
echo ""

# ---------------------------------------------------------------
# 6. Launch the application
# ---------------------------------------------------------------
echo "[6/6] Starting the Image Caption Generator..."
echo "      Once started, open http://127.0.0.1:8000 in your browser."
echo "      Press CTRL+C in this window to stop the server."
echo ""
python main.py

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}ERROR: The application exited unexpectedly. See the messages above.${NC}"
    error_exit
fi

read -n 1 -s -r -p "Press any key to close this window..."
