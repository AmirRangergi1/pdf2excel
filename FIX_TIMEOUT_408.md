# حل مشکل 408 Timeout برای فایل‌های بزرگ

## مشکل
هنگام بارگذاری فایل‌های بزرگ (مثلا 9 مگابایت)، خطای زیر ظاهر می‌شود:
```
❌ Error: Request failed with status code 408
```

این خطا به معنای است که درخواست بیش از حد طول کشیده و timeout شده است.

## حل‌های اعمال شده

### 1. افزایش Timeout در Frontend
**فایل:** `frontend/vite.config.js`
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    timeout: 300000 // 5 دقیقه
  }
}
```

### 2. افزایش Axios Timeout
**فایل:** `frontend/src/App.vue`
```javascript
const response = await axios.post('/api/convert', formData, {
  responseType: 'blob',
  timeout: 300000, // 5 دقیقه برای فایل‌های بزرگ
  onUploadProgress: (progressEvent) => {
    // ...
  }
})
```

### 3. افزایش Uvicorn Timeout
**فایل:** `backend/main.py`
```python
uvicorn.run(
    app, 
    host="0.0.0.0", 
    port=8000,
    timeout_keep_alive=300,  # 5 دقیقه
    timeout_notify=300       # 5 دقیقه
)
```

### 4. بهبود تجربه کاربر
- نمایش درصد پیشرفت در حقیقی
- نمایش پیام‌های بهتر برای حالت‌های مختلف
- نمایش بهتر اندازه فایل

## آزمایش
پس از اعمال تغییرات:

1. **Frontend را مجدد راه‌اندازی کنید:**
```bash
cd frontend
npm run dev
```

2. **Backend را مجدد راه‌اندازی کنید:**
```bash
cd backend
source venv/bin/activate
python main.py
```

3. **فایل 9MB خود را آپلود کنید** و صبر کنید (ممکن است 2-3 دقیقه زمان ببرد)

## جزئیات تکنیکی

### Timeout 300000 میلی‌ثانیه = 5 دقیقه
- این مدت برای فایل‌های تا 50 مگابایت کافی است
- برای فایل‌های بزرگ‌تر، می‌توانید مقدار را افزایش دهید

### چگونگی کار
1. کاربر فایل را انتخاب می‌کند
2. فایل به سرور بارگذاری می‌شود
3. سرور PDF را تجزیه می‌کند و جداول را استخراج می‌کند
4. سرور فایل Excel را تولید می‌کند
5. کاربر فایل Excel را دانلود می‌کند

## اگر هنوز مشکل دارید

### بررسی لاگ‌ها:
```bash
# Backend terminal میں خطا دیکھیں
# Frontend browser console میں خطا دیکھیں (F12)
```

### بزرگ‌تر کردن timeout:
اگر فایل‌های بزرگ‌تر از 50 مگابایت دارید:

**frontend/vite.config.js:**
```javascript
timeout: 600000 // 10 دقیقه
```

**frontend/src/App.vue:**
```javascript
timeout: 600000 // 10 دقیقه
```

**backend/main.py:**
```python
timeout_keep_alive=600,  # 10 دقیقه
timeout_notify=600
```

## نکات مهم
- فایل‌های PDF بزرگ نیاز به زمان بیشتری برای پردازش دارند
- اتصال اینترنت پایدار برای انتقال فایل‌های بزرگ ضروری است
- اگر 5 دقیقه هنوز کافی نیست، timeout را افزایش دهید
