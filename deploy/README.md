Deployment guide for VPS (Ubuntu 22.04+)

Overview
--------
These instructions show a minimum-viable production deployment using Gunicorn + systemd and nginx as a reverse proxy. Static files are served by nginx (or whitenoise). This assumes you control the VPS and can create systemd services and configure nginx.

High-level steps
----------------
1. Create a system user and clone the repo.
2. Create and activate a Python virtualenv and install requirements.
3. Create an `.env` (or export environment variables) with at least SECRET_KEY and ALLOWED_HOSTS.
4. Run migrations and collectstatic.
5. Configure systemd service for Gunicorn and enable/start it.
6. Configure nginx site to proxy to Gunicorn socket and serve static files.
7. (Optional) Obtain SSL with certbot and enable HTTPS.

Example commands (run as root or with sudo where necessary)
----------------------------------------------------------
# create a system user
adduser --disabled-password --gecos "" mysiteuser
usermod -aG sudo mysiteuser

# switch to the site user, clone
sudo -u mysiteuser -H bash -lc 'git clone https://your-repo.git /home/mysiteuser/sayt'
cd /home/mysiteuser/sayt

# create venv and install
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

# create .env file (example below) or export env vars in systemd unit
cp deploy/.env.example .env
# edit .env and set DJANGO_SECRET_KEY (generate a secure one) and verify DJANGO_ALLOWED_HOSTS
# The example file already includes the domain for this project:
# DJANGO_ALLOWED_HOSTS=aniqqishloqxojaligi.uz,www.aniqqishloqxojaligi.uz

# migrate and collectstatic
. .venv/bin/activate
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# set permissions for media/static as needed
chown -R mysiteuser:mysiteuser /home/mysiteuser/sayt/media /home/mysiteuser/sayt/staticfiles

# enable and start gunicorn service (example)
systemctl daemon-reload
systemctl enable --now gunicorn.service

# configure nginx: copy deploy/nginx-site.conf to /etc/nginx/sites-available/aniqqishloqxojaligi
sudo cp deploy/nginx-site.conf /etc/nginx/sites-available/aniqqishloqxojaligi
# edit the file paths inside if your deploy path differs from /home/www-data/sayt
sudo ln -s /etc/nginx/sites-available/aniqqishloqxojaligi /etc/nginx/sites-enabled/aniqqishloqxojaligi
sudo nginx -t && sudo systemctl reload nginx

# optional: use certbot to obtain SSL
apt install certbot python3-certbot-nginx
certbot --nginx -d example.com -d www.example.com

Files in this folder
--------------------
- `gunicorn.service` - systemd service file (example)
- `nginx-site.conf` - nginx configuration (example)
- `.env.example` - example environment variables to copy and edit

Security notes
--------------
- Never keep DEBUG=True in production.
- Use a strong SECRET_KEY and keep it out of version control (use environment variables or a secrets manager).
- Configure ALLOWED_HOSTS to your domain(s).
- Use HTTPS in production and set SESSION_COOKIE_SECURE and CSRF_COOKIE_SECURE to True.

If you want, I can:
- generate the exact systemd unit and nginx config filled with your domain and paths,
- create a small startup script for the service,
- or automate the deployment steps in a script.

Package/upload workflow (zip method)
-----------------------------------
If you prefer to upload a zip to the VPS and extract it there, use the helper scripts in `scripts/`:

- `scripts/package_for_vps.sh` — Linux/Mac packaging script (creates a zip excluding .venv, media, .git, db, etc.).
- `scripts/package_for_vps.ps1` — PowerShell packaging script for Windows.

Example usage (locally):

```bash
# run from project root
./scripts/package_for_vps.sh ../sayt-deploy.zip
# then scp sayt-deploy.zip user@vps:/home/user/
```

On the VPS after upload:

```bash
# as deploy user
unzip sayt-deploy.zip -d sayt
cd sayt
# create venv, install deps
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp deploy/.env.example .env
# edit .env to set SECRET_KEY and ALLOWED_HOSTS
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

Then configure systemd/nginx as described above and start gunicorn/nginx.

