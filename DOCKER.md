# Docker Deployment Guide

## نحوه اجرای برنامه با Docker

### پیش‌نیازها
- Docker installed
- Docker Compose (optional)

### روش 1: استفاده از Docker Compose (توصیه می‌شود)

```bash
cd /workspaces/pdf2excel
docker-compose up --build
```

سپس به آدرس `http://localhost:8000` بروید.

### روش 2: استفاده از Docker بدون Compose

**ساخت image:**
```bash
cd /workspaces/pdf2excel
docker build -t pdf-to-excel:latest .
```

**اجرای container:**
```bash
docker run -p 8000:8000 pdf-to-excel:latest
```

سپس به آدرس `http://localhost:8000` بروید.

### روش 3: استفاده از shell script

```bash
cd /workspaces/pdf2excel
chmod +x start.sh
./start.sh
```

## Docker Image Details

- **Base Image (Frontend):** `node:18-alpine`
- **Base Image (Backend):** `python:3.11-slim`
- **Port:** 8000
- **Health Check:** هر 30 ثانیه یک بار

## Volumes

اگر بخواهید فایل‌های آپلود شده را ذخیره کنید:

```bash
docker run -p 8000:8000 -v ./uploads:/app/uploads pdf-to-excel:latest
```

## Environment Variables

اگر نیاز به تغییر متغیرهای محیط دارید:

```bash
docker run -p 8000:8000 \
  -e PYTHONUNBUFFERED=1 \
  pdf-to-excel:latest
```

## بررسی وضعیت

```bash
# دیدن حاضر Container ها
docker ps

# دیدن logs
docker logs <container-id>

# Health check
curl http://localhost:8000/api/health
```

## حذف Container و Image

```bash
# حذف running container
docker stop <container-id>
docker rm <container-id>

# حذف image
docker rmi pdf-to-excel:latest
```

## Docker Compose Commands

```bash
# شروع کردن
docker-compose up

# شروع در background
docker-compose up -d

# توقف کردن
docker-compose down

# دیدن logs
docker-compose logs -f

# اعادہ build
docker-compose up --build
```

## Troubleshooting

**Port is already in use:**
```bash
docker run -p 9000:8000 pdf-to-excel:latest
# سپس به http://localhost:9000 بروید
```

**Permission denied:**
```bash
sudo docker build -t pdf-to-excel:latest .
sudo docker-compose up
```

**Health check failed:**
```bash
docker logs <container-id>
```

## Production Deployment

برای deployment در production:

1. استفاده از environment variables برای configuration
2. استفاده از reverse proxy (nginx) برای SSL
3. استفاده از persistent volumes برای data
4. تنظیم resource limits

مثال:
```bash
docker run -p 8000:8000 \
  -v uploads:/app/uploads \
  --restart always \
  --memory="1g" \
  --cpus="2" \
  pdf-to-excel:latest
```
