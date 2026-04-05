# 🐳 Docker Deployment Guide

## Quick Start (2 Commands)

### **Option A: Using Docker Compose (Easiest)**

```bash
docker-compose up --build
```

Open: http://localhost:8501

---

### **Option B: Using Docker CLI**

```bash
# Build the image
docker build -t text-summarizer .

# Run the container
docker run -p 8501:8501 text-summarizer
```

Open: http://localhost:8501

---

## 📤 Deploy to Cloud

### **Docker Hub**
```bash
# Login
docker login

# Build and tag
docker build -t your-username/text-summarizer .

# Push
docker push your-username/text-summarizer

# Share: your-username/text-summarizer
```

---

### **AWS (Free Tier)**
1. Push to Docker Hub
2. Go to AWS Elastic Container Service (ECS)
3. Create task from Docker image
4. Deploy! 🚀

---

### **Heroku**
```bash
# Install Heroku CLI
# heroku create your-app-name
# heroku container:push web
# heroku container:release web
```

---

### **Railway.app (Easiest Cloud)**
1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub"
4. Connect your repo
5. Done! 🎉

---

## 🔑 Environment Variables in Docker

The container uses these by default:
```
MODEL_PATH=facebook/bart-large-cnn
```

To use your custom model:
```bash
docker run -p 8501:8501 \
  -e MODEL_PATH=your-username/your-model \
  text-summarizer
```

---

## 📊 Container Details

- **Base**: Python 3.10-slim
- **Port**: 8501 (Streamlit)
- **Memory**: ~8GB (for model)
- **GPU**: Optional (see docker-compose.yml)

---

## ✅ Verify Deployment

Once running, check:
1. Open http://localhost:8501
2. Test with sample text
3. Check logs for errors

---

## 🚢 Production Deployment Tips

1. **Use GPU** (uncomment in docker-compose.yml)
2. **Add authentication** (if needed)
3. **Set resource limits**
4. **Use health checks** (already in Dockerfile)

---

## 🆘 Troubleshooting

**Container won't start:**
```bash
docker logs text-summarizer
```

**Port already in use:**
```bash
docker run -p 8502:8501 text-summarizer
# Then open http://localhost:8502
```

**Out of memory:**
```bash
docker run -p 8501:8501 \
  -m 10g \
  text-summarizer
```

---

**Ready?** Run: `docker-compose up --build` or `docker build -t summarizer . && docker run -p 8501:8501 summarizer`
