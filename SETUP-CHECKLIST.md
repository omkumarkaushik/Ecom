# Quick Setup Checklist

## ✅ Pre-Deployment Checklist

### 1. Repository Setup
- [ ] Copy all files to your Ecom repository
- [ ] Create `.env` from `.env.example` and configure
- [ ] Make `deploy.sh` executable: `chmod +x deploy.sh`
- [ ] Commit and push to your repository

### 2. Choose Your CI/CD Platform

#### GitHub Actions
- [ ] Files already in `.github/workflows/`
- [ ] Configure repository secrets (see below)
- [ ] Push to trigger pipeline

#### Jenkins
- [ ] `Jenkinsfile` is in root
- [ ] Install required Jenkins plugins
- [ ] Configure Jenkins credentials
- [ ] Create pipeline job

#### GitLab CI/CD
- [ ] `.gitlab-ci.yml` is in root
- [ ] Configure GitLab CI/CD variables
- [ ] Push to trigger pipeline

### 3. Required Secrets/Variables

#### For GitHub Actions:
```
Repository Settings → Secrets → Actions:
- STAGING_SSH_KEY
- STAGING_HOST
- STAGING_USER
- STAGING_URL
- PROD_SSH_KEY
- PROD_HOST
- PROD_USER
- PROD_URL
- SLACK_WEBHOOK (optional)
```

#### For Jenkins:
```
Manage Jenkins → Credentials:
- docker-registry-credentials (username/password)
- ssh-deployment-key (SSH private key)
- staging-host (secret text)
- prod-host (secret text)
```

#### For GitLab:
```
Settings → CI/CD → Variables:
- STAGING_SSH_PRIVATE_KEY
- STAGING_HOST
- STAGING_USER
- PROD_SSH_PRIVATE_KEY
- PROD_HOST
- PROD_USER
- SLACK_WEBHOOK_URL (optional)
```

### 4. Server Preparation

On each deployment server (staging & production):

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create application directory
sudo mkdir -p /opt/ecom-app
sudo chown $USER:$USER /opt/ecom-app

# Copy files to server
scp -r docker-compose.yml .env nginx/ user@server:/opt/ecom-app/

# Setup SSH access
ssh-copy-id user@server
```

### 5. First Deployment

#### Local Testing First:
```bash
# Test locally
make install
make lint
make test
make build
make run

# Verify application runs at http://localhost:8501
```

#### Deploy to Staging:
```bash
# Push to develop branch
git checkout develop
git push origin develop

# Or manually deploy
./deploy.sh staging deploy
```

#### Deploy to Production:
```bash
# Push to main branch (requires approval in CI/CD)
git checkout main
git merge develop
git push origin main

# Or manually deploy
./deploy.sh production deploy
```

### 6. Post-Deployment Verification

- [ ] Application accessible at expected URL
- [ ] Health check endpoint responding: `curl http://your-server:8501/_stcore/health`
- [ ] Logs show no errors: `docker-compose logs -f`
- [ ] Monitoring dashboards accessible (Grafana/Prometheus)
- [ ] SSL/TLS certificate configured (if using Nginx)

### 7. Monitoring Setup (Optional)

```bash
# Access monitoring
Grafana: http://your-server:3000 (admin/admin)
Prometheus: http://your-server:9090

# Configure alerts in Grafana
# Set up notification channels (Slack, Email, etc.)
```

## 🔧 Configuration Tips

### Environment Variables (.env)
```bash
# Must configure:
- POSTGRES_PASSWORD (change from default)
- REDIS_PASSWORD (change from default)
- SECRET_KEY (generate secure key)
- GRAFANA_PASSWORD (change from default)

# Optional:
- APP_PORT (default: 8501)
- PROMETHEUS_PORT (default: 9090)
- GRAFANA_PORT (default: 3000)
```

### SSL/TLS Setup
```bash
# Generate self-signed certificate (testing)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem

# For production, use Let's Encrypt
certbot certonly --standalone -d your-domain.com
```

## 🐛 Troubleshooting

### Pipeline Fails
1. Check logs in CI/CD interface
2. Verify all secrets/variables are set
3. Test locally with `make ci`

### Deployment Fails
1. Check SSH connectivity: `ssh user@server`
2. Verify Docker is running: `docker ps`
3. Check server logs: `./deploy.sh production logs`

### Application Won't Start
1. Check environment variables
2. Verify Docker Compose syntax
3. Check container logs: `docker-compose logs`

## 📞 Need Help?

- Check [CI-CD-IMPLEMENTATION-GUIDE.md](CI-CD-IMPLEMENTATION-GUIDE.md) for detailed instructions
- Review [README.md](README.md) for common operations
- Use `make help` to see available commands

## 🎯 Quick Commands Reference

```bash
make install          # Install dependencies
make test            # Run tests
make build           # Build Docker image
make run             # Start application
make deploy-staging  # Deploy to staging
make deploy-production  # Deploy to production
make clean           # Clean build artifacts

./deploy.sh production deploy    # Manual deploy
./deploy.sh production rollback  # Rollback
./deploy.sh production status    # Check status
./deploy.sh production logs      # View logs
```

---

**Ready to deploy? Start with the checklist above! 🚀**
