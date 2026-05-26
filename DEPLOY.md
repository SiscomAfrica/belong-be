# Deploy Belong Backend to EC2

Target: **t2.small** (1 vCPU, 2GB RAM) + 2GB swap
Domain: **api.belong.club**
Stack: Docker + Nginx + Let's Encrypt

---

## 1. AWS Setup

### Launch EC2

- **AMI**: Ubuntu 24.04 LTS (64-bit, x86)
- **Instance type**: t2.small
- **Storage**: 30 GB gp3
- **Key pair**: Create or select an existing SSH key
- **Security group** — allow:

| Type  | Port | Source    |
|-------|------|-----------|
| SSH   | 22   | Your IP   |
| HTTP  | 80   | 0.0.0.0/0 |
| HTTPS | 443  | 0.0.0.0/0 |

### Elastic IP

Allocate an Elastic IP and associate it with the instance. You need a static IP for DNS.

### DNS

Add an A record in your domain registrar:

```
Type: A
Name: api
Value: <your-elastic-ip>
TTL: 300
```

Verify propagation before proceeding:

```bash
dig api.belong.club +short
```

---

## 2. Server Setup

SSH into the instance:

```bash
ssh -i ~/.ssh/your-key.pem ubuntu@api.belong.club
```

### 2a. System updates

```bash
sudo apt update && sudo apt upgrade -y
```

### 2b. Create swap

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Tune for low-memory server
sudo sysctl vm.swappiness=10
sudo sysctl vm.vfs_cache_pressure=50
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
echo 'vm.vfs_cache_pressure=50' | sudo tee -a /etc/sysctl.conf
```

Verify:

```bash
free -h
# Should show ~2GB swap
```

### 2c. Install Docker

```bash
# Add Docker's official GPG key and repo
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin

# Run Docker without sudo
sudo usermod -aG docker $USER
newgrp docker
```

Verify:

```bash
docker --version
docker compose version
```

### 2d. Install Nginx + Certbot

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

---

## 3. Deploy the Application

### 3a. Clone the repo

```bash
cd /home/ubuntu
git clone https://github.com/YOUR_ORG/belong-backend.git
cd belong-backend
```

### 3b. Create production `.env`

```bash
nano .env
```

Paste the following and fill in real values:

```env
# Django
DJANGO_ENV=production
SECRET_KEY=<generate: python3 -c "import secrets; print(secrets.token_urlsafe(64))">
DEBUG=False
ALLOWED_HOSTS=api.belong.club

# Database
DATABASE_URL=postgres://belong:STRONG_DB_PASSWORD_HERE@postgres:5432/belong
POSTGRES_DB=belong
POSTGRES_USER=belong
POSTGRES_PASSWORD=STRONG_DB_PASSWORD_HERE

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# JWT
JWT_SIGNING_KEY=<generate: python3 -c "import secrets; print(secrets.token_urlsafe(64))">

# CORS
CORS_ALLOWED_ORIGINS=https://admin.belong.club

# M-Pesa
MPESA_CONSUMER_KEY=
MPESA_CONSUMER_SECRET=
MPESA_PASSKEY=
MPESA_SHORTCODE=174379
MPESA_ENV=sandbox
MPESA_CALLBACK_BASE_URL=https://api.belong.club

# Paystack
PAYSTACK_SECRET_KEY=
PAYSTACK_PUBLIC_KEY=

# KYC (Smile Identity)
SMILE_IDENTITY_API_KEY=
SMILE_IDENTITY_PARTNER_ID=
SMILE_IDENTITY_ENV=sandbox
SMILE_IDENTITY_CALLBACK_URL=https://api.belong.club/api/kyc/webhook

# LLM
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-sonnet-4-20250514
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o
```

Generate the secret keys:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 3c. Build and start

```bash
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

Watch the logs until all services are healthy:

```bash
docker compose -f docker-compose.prod.yml logs -f
```

### 3d. Run migrations and seed data

```bash
docker compose -f docker-compose.prod.yml exec api python manage.py migrate
docker compose -f docker-compose.prod.yml exec api python manage.py seed_funds
docker compose -f docker-compose.prod.yml exec api python manage.py seed_compliance
```

### 3e. Verify the API is running

```bash
curl http://localhost:8000/api/health/
# {"status": "healthy", "db": "ok"}
```

---

## 4. Nginx + SSL

### 4a. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/belong
```

Paste:

```nginx
upstream belong_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.belong.club;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name api.belong.club;

    ssl_certificate /etc/letsencrypt/live/api.belong.club/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.belong.club/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;

    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    client_max_body_size 10M;

    location / {
        proxy_pass http://belong_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_read_timeout 120s;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/belong /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
```

### 4b. Get SSL certificate

First, temporarily comment out the entire `server { listen 443 ... }` block and the `return 301` line in the port-80 block. Replace with a temporary pass-through so Certbot can verify:

```bash
sudo nano /etc/nginx/sites-available/belong
```

Temporary config (just for cert issuance):

```nginx
server {
    listen 80;
    server_name api.belong.club;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

```bash
sudo mkdir -p /var/www/certbot
sudo nginx -t && sudo systemctl restart nginx
```

Now issue the certificate:

```bash
sudo certbot --nginx -d api.belong.club --non-interactive --agree-tos -m your-email@belong.club
```

After Certbot succeeds, restore the full Nginx config from step 4a:

```bash
sudo nano /etc/nginx/sites-available/belong
# Paste the full config from step 4a back
sudo nginx -t && sudo systemctl reload nginx
```

### 4c. Auto-renew

Certbot installs a systemd timer automatically. Verify:

```bash
sudo systemctl status certbot.timer
```

Test renewal:

```bash
sudo certbot renew --dry-run
```

---

## 5. Verify Deployment

```bash
curl https://api.belong.club/api/health/
# {"status": "healthy", "db": "ok"}
```

Check all services:

```bash
docker compose -f docker-compose.prod.yml ps
```

Expected output — all 5 services running:

```
NAME              STATUS
api               Up (healthy)
postgres          Up (healthy)
redis             Up (healthy)
celery-worker     Up
celery-beat       Up
```

---

## 6. Operations

### View logs

```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Single service
docker compose -f docker-compose.prod.yml logs -f api
docker compose -f docker-compose.prod.yml logs -f celery-worker
```

### Deploy updates

```bash
cd /home/ubuntu/belong-backend
git pull origin main
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml exec api python manage.py migrate
```

### Restart a service

```bash
docker compose -f docker-compose.prod.yml restart api
docker compose -f docker-compose.prod.yml restart celery-worker
```

### Django shell

```bash
docker compose -f docker-compose.prod.yml exec api python manage.py shell
```

### Create admin user

```bash
docker compose -f docker-compose.prod.yml exec api python manage.py createsuperuser
```

### Database backup

```bash
docker compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U belong belong > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Database restore

```bash
cat backup_file.sql | docker compose -f docker-compose.prod.yml exec -T postgres \
  psql -U belong belong
```

### Check resource usage

```bash
docker stats --no-stream
free -h
df -h
```

---

## 7. Memory Budget (t2.small: 2GB RAM + 2GB Swap)

| Service        | Limit  | Expected |
|----------------|--------|----------|
| Django/Gunicorn | 512 MB | ~300 MB  |
| PostgreSQL      | 384 MB | ~200 MB  |
| Celery Worker   | 384 MB | ~200 MB  |
| Celery Beat     | 128 MB | ~60 MB   |
| Redis           | 96 MB  | ~30 MB   |
| Nginx + OS      | ~400 MB | ~300 MB |
| **Total**       | **~1.9 GB** | **~1.1 GB** |

Swap provides headroom for traffic spikes and Docker builds.

---

## 8. Security Checklist

- [ ] SSH: disable password auth, use key-only (`PasswordAuthentication no` in `/etc/ssh/sshd_config`)
- [ ] Firewall: `sudo ufw allow 22/tcp && sudo ufw allow 80/tcp && sudo ufw allow 443/tcp && sudo ufw enable`
- [ ] `.env` file permissions: `chmod 600 .env`
- [ ] PostgreSQL password is strong and unique
- [ ] SECRET_KEY and JWT_SIGNING_KEY are random 64+ char strings
- [ ] Fail2ban: `sudo apt install fail2ban` (protects SSH)
- [ ] Unattended upgrades: `sudo apt install unattended-upgrades`
- [ ] Docker socket is not exposed to the internet
- [ ] Security group restricts SSH to your IP only

---

## 9. Automated Daily Backups (Optional)

Create a cron job for daily DB backups:

```bash
sudo mkdir -p /home/ubuntu/backups
```

```bash
crontab -e
```

Add:

```
0 3 * * * docker compose -f /home/ubuntu/belong-backend/docker-compose.prod.yml exec -T postgres pg_dump -U belong belong | gzip > /home/ubuntu/backups/belong_$(date +\%Y\%m\%d).sql.gz && find /home/ubuntu/backups -mtime +7 -delete
```

This runs at 3 AM daily and keeps 7 days of backups.
