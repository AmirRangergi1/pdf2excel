# خلاصه تغییرات: Single Origin + Docker Integration

## چه تغییری داده شده است؟

### 1. معماری جدید
**قبل:**
```
Frontend: http://localhost:5173
Backend:  http://localhost:8000
مسئله: CORS issues
```

**بعد:**
```
Frontend + Backend: http://localhost:8000
یک Origin = بدون CORS
```

### 2. تغییرات Backend (main.py)

#### اضافه شده:
```python
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Serve static frontend files
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="static")

# Health check endpoint
@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "PDF to Excel Converter API"}
```

### 3. تغییرات Start Scripts

#### start.sh (Linux/Mac)
- Build Frontend اول (`npm run build`)
- سپس Backend را شروع کن
- Frontend files از `frontend/dist` serve می‌شود

#### start.bat (Windows)
- همان logic برای Windows

### 4. Docker Support

#### Dockerfile (Multi-stage)
```dockerfile
# Stage 1: Build Frontend
FROM node:18-alpine AS frontend-builder
# Build Vue.js app → dist folder

# Stage 2: Production
FROM python:3.11-slim
# Copy built frontend
# Run Python backend
```

#### docker-compose.yml
```yaml
services:
  pdf-to-excel:
    build: .
    ports:
      - "8000:8000"
    healthcheck: ...
```

#### .dockerignore
Optimization برای Docker image

### 5. فایل‌های اضافی

- **DOCKER.md** - راهنمای کامل Docker
- **.dockerignore** - بهینه‌سازی image

## چگونه استفاده کنم؟

### روش 1: Local Development (بدون Docker)
```bash
cd /workspaces/pdf2excel
chmod +x start.sh
./start.sh
```
→ http://localhost:8000

### روش 2: Docker Compose
```bash
cd /workspaces/pdf2excel
docker-compose up --build
```
→ http://localhost:8000

### روش 3: Docker Standalone
```bash
docker build -t pdf-to-excel .
docker run -p 8000:8000 pdf-to-excel
```
→ http://localhost:8000

### روش 4: Windows
```bash
cd /workspaces/pdf2excel
start.bat
```
→ http://localhost:8000

## فایل‌های تغییر یافته

| فایل | تغییر |
|------|-------|
| `backend/main.py` | اضافه: StaticFiles mount + health check |
| `start.sh` | بروزرسانی: Build frontend + serve |
| `start.bat` | بروزرسانی: Build frontend + serve |
| `frontend/vite.config.js` | قبلی: proxy timeout (حفظ شد) |
| `frontend/src/App.vue` | قبلی: Axios timeout (حفظ شد) |

## فایل‌های جدید

| فایل | نوع | توضیح |
|------|-----|-------|
| `Dockerfile` | Docker | بسته‌بندی تمام برنامه |
| `docker-compose.yml` | Docker | سهل‌تر اجرا با Compose |
| `.dockerignore` | Docker | بهینه‌سازی image |
| `DOCKER.md` | Documentation | راهنمای Docker |

## مزایای جدید

✅ **CORS-free**: هر دو در یک origin  
✅ **Production-ready**: Multi-stage Docker build  
✅ **سهل deployment**: docker-compose  
✅ **Health checks**: Docker monitoring  
✅ **Optimized**: کوچک‌تر image size  
✅ **Scalable**: Kubernetes compatible  

## سرعت اجرا

| روش | زمان |
|-----|-----|
| `./start.sh` | ~30-60 ثانیه |
| `docker-compose up` | 60-120 ثانیه (اول) |
| `docker run` | <5 ثانیه (بعدی) |

## نقاط مهم

1. **Build Process**: Frontend حالا در runtime بناء می‌شود
2. **Single Port**: هر دو service روی 8000
3. **No CORS**: یک origin = بدون cross-origin مسائل
4. **Production**: آماده برای production deployment

## بیشتر اطلاعات

- [README.md](README.md) - معلومات کامل
- [DOCKER.md](DOCKER.md) - Docker راهنما
- [FIX_TIMEOUT_408.md](FIX_TIMEOUT_408.md) - Timeout مسائل

---

**تاریخ:** 7 ژانویه 2026  
**نسخه:** 2.0 (Single Origin + Docker)
