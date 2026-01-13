# 🚀 Guía de Despliegue - Chatbot Diabetes

## Opciones de Despliegue

### 1. 🐳 Docker (Recomendado)

#### Crear Dockerfile para Backend

Crear `backend/Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
```

#### Crear docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - ./backend/models:/app/models
      - ./backend/data:/app/data

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://localhost:5000
```

**Iniciar con Docker Compose**:
```bash
docker-compose up
```

---

### 2. ☁️ Heroku

#### Backend en Heroku

```bash
# 1. Inicializar git
git init

# 2. Crear Procfile en backend
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# 3. Crear app en Heroku
heroku create mi-chatbot-diabetes

# 4. Deploy
git push heroku main
```

#### Frontend en Netlify/Vercel

```bash
cd frontend

# Con Netlify
netlify deploy --prod --dir=build

# Con Vercel
vercel --prod
```

---

### 3. 🚂 Railway

#### Crear railway.toml

```toml
[build]
builder = "heroku.buildpacks"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
```

#### Deploy

```bash
railway init
railway up
```

---

### 4. 💻 VPS (Linux)

#### Preparación del servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python y Node
sudo apt install python3.10 python3-pip nodejs npm

# Instalar PM2 (process manager)
sudo npm install -g pm2
```

#### Deploy Backend

```bash
cd /opt/chatbot/backend

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo service para Systemd
sudo nano /etc/systemd/system/chatbot-backend.service
```

```ini
[Unit]
Description=Chatbot Diabetes Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/chatbot/backend
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 5000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Activar servicio
sudo systemctl enable chatbot-backend
sudo systemctl start chatbot-backend
```

#### Deploy Frontend

```bash
cd /opt/chatbot/frontend

npm install
npm run build

# Servir con Nginx
sudo apt install nginx
sudo cp build/* /var/www/html/
sudo systemctl restart nginx
```

---

### 5. 🐍 AWS

#### EC2 + S3 + Lambda

**Backend en EC2**:
```bash
# AMI: Ubuntu 20.04 LTS
# Instancia: t2.micro (free tier)

# Seguir pasos de VPS Linux arriba
```

**Frontend en S3 + CloudFront**:
```bash
# Build
npm run build

# Subir a S3
aws s3 sync build/ s3://mi-bucket/

# Invalidar CloudFront
aws cloudfront create-invalidation --distribution-id E123 --paths "/*"
```

---

## 📋 Variables de Entorno

### Backend (.env)

```env
# Flask/FastAPI
DEBUG=False
ENVIRONMENT=production

# Database (opcional)
DATABASE_URL=postgresql://user:pass@localhost/dbname

# API
API_PORT=5000
API_HOST=0.0.0.0

# Security
SECRET_KEY=tu_clave_secreta_aqui
```

### Frontend (.env)

```env
REACT_APP_API_URL=https://api.tudominio.com
REACT_APP_ENVIRONMENT=production
```

---

## 🔒 Seguridad en Producción

### Backend Security

```python
# main.py - Agregar estas líneas
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.https import HTTPSMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com"]
)

# Usar HTTPS
app.add_middleware(HTTPSMiddleware, redirect=True)

# Rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
```

### Frontend Security

```javascript
// Agregar headers de seguridad en nginx.conf
add_header X-Frame-Options "SAMEORIGIN";
add_header X-Content-Type-Options "nosniff";
add_header X-XSS-Protection "1; mode=block";
```

---

## 📊 Monitoreo

### Logs

```bash
# Backend en Linux
sudo journalctl -u chatbot-backend -f

# Frontend
tail -f /var/log/nginx/access.log
```

### Herramientas

- **PM2**: Monitorar procesos Node/Python
- **NewRelic**: APM (Application Performance Monitoring)
- **DataDog**: Observabilidad
- **Sentry**: Error tracking

---

## 🔄 CI/CD Pipeline

### GitHub Actions

Crear `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Test Backend
        run: |
          cd backend
          pip install -r requirements.txt
          python -m pytest
      
      - name: Test Frontend
        run: |
          cd frontend
          npm install
          npm test
      
      - name: Deploy Backend
        run: |
          # Deploy to Heroku/Railway/etc
          git push heroku main
      
      - name: Deploy Frontend
        run: |
          # Deploy to Netlify/Vercel/etc
          npm run build
          netlify deploy --prod
```

---

## 📈 Escalamiento

### Cuando crece el tráfico

1. **Backend**:
   - Usar Kubernetes para auto-scaling
   - Load Balancer (nginx, HAProxy)
   - Cache con Redis
   - DB con replicación

2. **Frontend**:
   - CDN global (CloudFlare, Fastly)
   - Lazy loading
   - Code splitting
   - Compression (gzip)

3. **Data**:
   - Caché de modelos
   - Predicciones batch
   - Async tasks con Celery

---

## ✅ Checklist de Despliegue

- [ ] Variables de entorno configuradas
- [ ] Base de datos setup (si aplica)
- [ ] Modelo entrenado guardado
- [ ] SSL/HTTPS habilitado
- [ ] CORS configurado correctamente
- [ ] Logs centralizados
- [ ] Monitoreo setup
- [ ] Backups automatizados
- [ ] Health checks configurados
- [ ] DNS apuntando correctamente
- [ ] Rate limiting habilitado
- [ ] CSRF protection activa

---

## 🎯 Ejemplo Completo: AWS

```bash
# 1. EC2 Instance
- Ubuntu 20.04 LTS
- t2.micro (free tier)
- Security Group: 80, 443, 5000

# 2. Backend
ssh ec2-user@instance
cd /opt/chatbot/backend
pip install -r requirements.txt
pm2 start "uvicorn main:app --host 0.0.0.0"

# 3. Frontend
cd /opt/chatbot/frontend
npm run build
sudo cp -r build/* /var/www/html/

# 4. Nginx
sudo apt install nginx
# Configurar proxy a backend

# 5. SSL
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d tudominio.com

# 6. Monitor
pm2 save
pm2 startup
```

---

## 📞 Soporte de Despliegue

Para problemas específicos:
1. Revisar logs del servicio
2. Verificar variables de entorno
3. Comprobar conectividad de red
4. Verificar permisos de archivos

---

**Última actualización**: Enero 2026  
**Versión**: 2.0.0
