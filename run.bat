cd /d "%~dp0"

if not exist venv (
    python -m venv venv
    venv\Scripts\activate
    pip install --upgrade pip
    pip install flask web3 python-dotenv reportlab Pillow pypdf PyMuPDF numpy PyWavelets
) else (
    call venv\Scripts\activate.bat
)

python Web_Form/app.py
