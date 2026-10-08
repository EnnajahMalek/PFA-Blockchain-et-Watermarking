#!/bin/bash
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install flask web3 python-dotenv reportlab Pillow pypdf PyMuPDF numpy PyWavelets
else
    source venv/bin/activate
fi

python3 Web_Form/app.py
