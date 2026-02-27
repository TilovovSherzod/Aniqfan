# PowerShell script: virtualenv yaratish, o'rnatish va serverni ishga tushirish
if (-not (Test-Path .venv)) {
    python -m venv .venv
}

# Aktivatsiya (interactive shell uchun):
. .venv\Scripts\Activate.ps1

pip install -r requirements.txt

Write-Host "Django serverni ishga tushiryapman: http://127.0.0.1:8000"
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
