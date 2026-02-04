# Ecom CI/CD Pipeline Implementation

Complete CI/CD pipeline setup for your Python Streamlit E-commerce application with Docker support.

## 📦 Package Contents

This CI/CD implementation includes:

### Pipeline Configurations
- **`.github/workflows/ci-cd-pipeline.yml`** - GitHub Actions workflow
- **`Jenkinsfile`** - Jenkins declarative pipeline
- **`.gitlab-ci.yml`** - GitLab CI/CD configuration

### Docker & Deployment
- **`Dockerfile`** - Optimized multi-stage Docker build
- **`docker-compose.yml`** - Production-ready compose configuration
- **`.dockerignore`** - Docker build optimization
- **`deploy.sh`** - Automated deployment script with rollback
- **`nginx/nginx.conf`** - Nginx reverse proxy configuration

### Configuration Files
- **`.env.example`** - Environment variables template
- **`pyproject.toml`** - Python tool configurations (Black, isort, pytest, etc.)
- **`requirements-dev.txt`** - Development and CI/CD dependencies
- **`Makefile`** - Common operations automation

### Documentation
- **`CI-CD-IMPLEMENTATION-GUIDE.md`** - Comprehensive implementation guide
- **`README.md`** - This file

## 🚀 Quick Start

### Choose Your CI/CD Platform

#### Option 1: GitHub Actions (Recommended for GitHub)

1. Copy the workflow file:
   ```bash
   mkdir -p .github/workflows
   cp ci-cd-pipeline.yml .github/workflows/
   ```

2. Configure secrets in GitHub repository settings
3. Push to trigger the pipeline

#### Option 2: Jenkins

1. Copy `Jenkinsfile` to your repository root
2. Configure Jenkins credentials
3. Create a new Pipeline job pointing to your repository
4. Build the job

#### Option 3: GitLab CI/CD

1. Copy `.gitlab-ci.yml` to your repository root
2. Configure GitLab CI/CD variables
3. Push to trigger the pipeline

## 📋 Prerequisites

- Docker 24.0+ and Docker Compose 2.0+
- Python 3.11+
- Git
- SSH access to deployment servers
- Container registry access (GitHub CR, Docker Hub, etc.)

## 🔧 Setup Instructions

### 1. Initial Configuration

```bash
# Clone your repository
git clone https://github.com/omkumarkaushik/Ecom.git
cd Ecom

# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env

# Make deployment script executable
chmod +x deploy.sh
```

### 2. Local Testing

```bash
# Install dependencies
make install

# Run linting
make lint

# Run tests
make test

# Build Docker image
make build

# Run locally
make run
```

### 3. Deploy

```bash
# Deploy to staging
make deploy-staging

# Deploy to production (after approval)
make deploy-production
```

## 🏗️ Pipeline Architecture

```
Code Push → Lint & Security → Tests → Build → Scan → Deploy
     ↓           ↓             ↓       ↓       ↓       ↓
  GitHub      Flake8        pytest   Docker  Trivy  Staging
  GitLab      Black                                 Production
  Jenkins     Bandit
```

### Pipeline Stages

1. **Lint & Code Quality**
   - Black code formatting
   - Flake8 linting
   - isort import sorting

2. **Security Scanning**
   - Bandit (SAST)
   - Safety (dependency vulnerabilities)

3. **Testing**
   - pytest unit tests
   - Code coverage reporting

4. **Build**
   - Multi-stage Docker build
   - Image caching for speed
   - Automatic tagging

5. **Container Security**
   - Trivy vulnerability scanning
   - CVE detection

6. **Deployment**
   - Staging (automatic on develop)
   - Production (manual approval on main)
   - Health checks with auto-rollback

## 🔐 Security Features

- Non-root Docker containers
- Security scanning at multiple stages
- Dependency vulnerability checks
- Container image scanning
- Nginx with security headers
- Rate limiting and DDoS protection
- SSL/TLS termination
- Secret management via environment variables

## 📊 Monitoring

### Built-in Monitoring

- **Prometheus** - Metrics collection
- **Grafana** - Visualization dashboards
- **Docker logs** - Application logging
- **Health checks** - Automatic health monitoring

### Access Monitoring

```bash
# View Grafana dashboards
http://your-server:3000

# View Prometheus metrics
http://your-server:9090

# View application logs
docker-compose logs -f streamlit-app
```

## 🔄 Deployment Workflows

### Staging Deployment (Automatic)

```bash
git checkout develop
git commit -am "Feature: New functionality"
git push origin develop
# Pipeline automatically deploys to staging
```

### Production Deployment (Manual Approval)

```bash
git checkout main
git merge develop
git push origin main
# Pipeline waits for manual approval
# Approve in CI/CD interface
# Deployment proceeds with health checks
```

### Rollback

```bash
# Automatic rollback if health checks fail
# Or manual rollback:
./deploy.sh production rollback
```

## 🛠️ Common Operations

### Using Make Commands

```bash
make help              # Show all available commands
make install           # Install dependencies
make lint              # Run code quality checks
make format            # Auto-format code
make test              # Run tests with coverage
make build             # Build Docker image
make run               # Start application
make clean             # Clean build artifacts
make ci                # Run full CI pipeline locally
```

### Using Deployment Script

```bash
./deploy.sh production deploy     # Deploy to production
./deploy.sh production rollback   # Rollback production
./deploy.sh production logs       # View logs
./deploy.sh production status     # Check status
```

## 📁 Project Structure

```
Ecom/
├── .github/
│   └── workflows/
│       └── ci-cd-pipeline.yml
├── app/
│   └── # Your application code
├── data/
│   └── # Application data
├── nginx/
│   └── nginx.conf
├── monitoring/
│   ├── prometheus.yml
│   └── grafana/
├── .dockerignore
├── .env.example
├── .gitlab-ci.yml
├── docker-compose.yml
├── Dockerfile
├── Jenkinsfile
├── Makefile
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── streamlit_app.py
└── deploy.sh
```

## 🐛 Troubleshooting

### Pipeline Fails at Build Stage

```bash
# Check Docker daemon
docker ps

# Clear build cache
docker builder prune -a

# Rebuild without cache
make build-no-cache
```

### Health Check Fails

```bash
# Check container logs
docker-compose logs streamlit-app

# Verify Streamlit is running
curl http://localhost:8501/_stcore/health

# Check container status
docker-compose ps
```

### SSH Connection Issues

```bash
# Test SSH connection
ssh -vvv user@host

# Check SSH key permissions
chmod 600 ~/.ssh/id_rsa

# Verify SSH key is added to server
ssh-copy-id user@host
```

## 📚 Documentation

- **[CI-CD-IMPLEMENTATION-GUIDE.md](CI-CD-IMPLEMENTATION-GUIDE.md)** - Detailed implementation guide
- **[Docker Documentation](https://docs.docker.com/)**
- **[GitHub Actions](https://docs.github.com/en/actions)**
- **[Jenkins Pipeline](https://www.jenkins.io/doc/book/pipeline/)**
- **[GitLab CI/CD](https://docs.gitlab.com/ee/ci/)**

## 🔗 Integration Options

### Slack Notifications

Add Slack webhook URL to your CI/CD secrets:
```bash
SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Email Notifications

Configure in your CI/CD platform settings.

### Status Badges

Add to your repository README:
```markdown
![CI/CD Pipeline](https://github.com/omkumarkaushik/Ecom/workflows/Ecom%20CI/CD%20Pipeline/badge.svg)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This CI/CD implementation is provided as-is for your Ecom project.

## 👤 Author

**Om Kumar Kaushik**
- GitHub: [@omkumarkaushik](https://github.com/omkumarkaushik)
- Company: Optum

## 🎯 Features

✅ Multiple CI/CD platform support (GitHub Actions, Jenkins, GitLab)
✅ Automated testing and code quality checks
✅ Security scanning at multiple stages
✅ Docker multi-stage builds
✅ Production-ready Docker Compose setup
✅ Nginx reverse proxy with SSL
✅ Prometheus and Grafana monitoring
✅ Automatic rollback on failure
✅ Manual approval for production
✅ Slack/Email notifications
✅ Health checks and auto-recovery
✅ Backup and restore functionality
✅ Rate limiting and DDoS protection

## 📞 Support

For issues or questions:
- Open an issue in the repository
- Check the [CI-CD-IMPLEMENTATION-GUIDE.md](CI-CD-IMPLEMENTATION-GUIDE.md)
- Review troubleshooting section

---

**Happy Deploying! 🚀**
