# محوّل الصور — Image Converter

## التشغيل المحلي
```bash
pip install -r requirements.txt
python app.py
```
ثم افتح: http://localhost:5000

## النشر على Hostinger / VPS

### 1. رفع الملفات
```bash
scp -r image-converter/ user@yourserver.com:/var/www/image-converter/
```

### 2. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 3. تشغيل بـ Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 4. Nginx config
```nginx
server {
    listen 80;
    server_name yoursite.com;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /var/www/image-converter/static/;
        expires 30d;
    }
}
```

### 5. SSL (مجاني)
```bash
certbot --nginx -d yoursite.com
```

## النشر على Railway / Render (مجاني)
1. ارفع على GitHub
2. اربط الـ repo بـ Railway أو Render
3. أضف متغير `PORT=5000`

## هيكل الملفات
```
image-converter/
├── app.py              # Flask backend
├── requirements.txt
├── templates/
│   └── index.html      # الواجهة + SEO
└── static/
    ├── uploads/        # مؤقت
    └── outputs/        # الصور المحوّلة
```

## ميزات SEO المضمّنة
- Title + Meta Description محسّنة
- Open Graph (Facebook/Twitter)
- Schema.org WebApplication + FAQPage
- Canonical URL
- Semantic HTML (header, main, section, footer)
- FAQ Accordion مع Schema markup
