# CI/CD Pipeline Implementation Guide for Ecom Project

## Table of Contents
1. [Overview](#overview)
2. [Pipeline Architecture](#pipeline-architecture)
3. [Setup Instructions](#setup-instructions)
4. [Configuration](#configuration)
5. [Deployment Process](#deployment-process)
6. [Monitoring & Rollback](#monitoring--rollback)
7. [Best Practices](#best-practices)

## Overview

This document provides comprehensive instructions for implementing CI/CD pipelines for the Ecom Streamlit application. We provide configurations for:

- **GitHub Actions** - Cloud-native CI/CD
- **Jenkins** - Self-hosted CI/CD server
- **GitLab CI/CD** - Integrated GitLab solution

### Pipeline Stages

1. **Lint & Code Quality** - Black, Flake8, isort, Pylint
2. **Security Scanning** - Bandit (SAST), Safety (dependency check)
3. **Testing** - Unit tests with pytest and coverage
4. **Build** - Docker image creation with multi-stage builds
5. **Container Security** - Trivy vulnerability scanning
6. **Deploy Staging** - Automated deployment to staging environment
7. **Deploy Production** - Manual approval deployment to production
8. **Notifications** - Slack/Email notifications on pipeline status

## Pipeline Architecture

```
┌─────────────┐
│   Commit    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│         Lint & Code Quality             │
│  ┌──────┐ ┌────────┐ ┌──────┐          │
│  │Black │ │Flake8  │ │isort │          │
│  └──────┘ └────────┘ └──────┘          │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│        Security Scanning                 │
│  ┌──────────┐ ┌─────────────────┐       │
│  │ Bandit   │ │ Safety Check    │       │
│  └──────────┘ └─────────────────┘       │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│            Unit Tests                    │
│  ┌────────────────────────────────┐     │
│  │ pytest + coverage              │     │
│  └────────────────────────────────┘     │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│         Build Docker Image               │
│  ┌────────────────────────────────┐     │
│  │ Multi-stage build + caching    │     │
│  └────────────────────────────────┘     │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│      Container Security Scan             │
│  ┌────────────────────────────────┐     │
│  │ Trivy vulnerability scanning   │     │
│  └────────────────────────────────┘     │
└──────────────────┬──────────────────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
         ▼                   ▼
┌────────────────┐  ┌────────────────┐
│    Staging     │  │   Production   │
│   (develop)    │  │     (main)     │
│   Automatic    │  │ Manual Approval│
└────────────────┘  └────────────────┘
```

## Setup Instructions

### 1. GitHub Actions Setup

#### Prerequisites
- GitHub repository
- GitHub Container Registry access
- SSH access to deployment servers

#### Steps

1. **Copy workflow file to your repository:**
   ```bash
   mkdir -p .github/workflows
   cp ci-cd-pipeline.yml .github/workflows/
   ```

2. **Configure Repository Secrets:**
   Go to Repository Settings → Secrets and Variables → Actions

   Add the following secrets:
   ```
   # Docker Registry
   GITHUB_TOKEN (automatically provided)
   
   # Staging Server
   STAGING_SSH_KEY        # Private SSH key for staging server
   STAGING_HOST           # Staging server hostname/IP
   STAGING_USER           # SSH username for staging
   STAGING_URL            # Staging application URL
   
   # Production Server
   PROD_SSH_KEY           # Private SSH key for production server
   PROD_HOST              # Production server hostname/IP
   PROD_USER              # SSH username for production
   PROD_URL               # Production application URL
   
   # Notifications
   SLACK_WEBHOOK          # Slack webhook URL for notifications
   ```

3. **Enable GitHub Container Registry:**
   - Go to your profile → Settings → Developer settings → Personal access tokens
   - Create token with `write:packages` scope
   - Configure your repository to use GHCR

4. **Push to trigger the pipeline:**
   ```bash
   git add .
   git commit -m "Add CI/CD pipeline"
   git push origin develop  # For staging
   git push origin main     # For production
   ```

### 2. Jenkins Setup

#### Prerequisites
- Jenkins server (version 2.400+)
- Docker installed on Jenkins server
- Required Jenkins plugins:
  - Docker Pipeline
  - SSH Agent
  - Slack Notification
  - Blue Ocean (optional, for better UI)
  - HTML Publisher
  - JUnit

#### Steps

1. **Install Jenkins Plugins:**
   ```
   Manage Jenkins → Plugins → Available Plugins
   Search and install: Docker Pipeline, SSH Agent, Slack Notification
   ```

2. **Configure Jenkins Credentials:**
   Go to Manage Jenkins → Credentials → System → Global credentials

   Add the following credentials:
   ```
   - Docker Registry Credentials (username/password)
     ID: docker-registry-credentials
   
   - SSH Private Key for Deployment
     ID: ssh-deployment-key
   
   - Staging Host Secret Text
     ID: staging-host
   
   - Production Host Secret Text
     ID: prod-host
   ```

3. **Create Jenkins Pipeline Job:**
   ```
   - New Item → Pipeline
   - Name: Ecom-CI-CD
   - Pipeline script from SCM
   - SCM: Git
   - Repository URL: your-repo-url
   - Script Path: Jenkinsfile
   ```

4. **Configure Slack Notifications:**
   ```
   Manage Jenkins → Configure System → Slack
   Workspace: your-workspace
   Credential: Add Slack token
   Default channel: #ecom-deployments
   ```

5. **Run Pipeline:**
   - Click "Build Now" or push to trigger webhook
   - Monitor build in Blue Ocean or classic view

### 3. GitLab CI/CD Setup

#### Prerequisites
- GitLab repository
- GitLab Runner configured
- Docker executor enabled

#### Steps

1. **Copy CI/CD configuration:**
   ```bash
   cp .gitlab-ci.yml /path/to/your/repo/
   ```

2. **Configure GitLab CI/CD Variables:**
   Go to Settings → CI/CD → Variables

   Add the following variables:
   ```
   # Registry (auto-configured)
   CI_REGISTRY
   CI_REGISTRY_USER
   CI_REGISTRY_PASSWORD
   
   # Staging
   STAGING_SSH_PRIVATE_KEY
   STAGING_HOST
   STAGING_USER
   
   # Production
   PROD_SSH_PRIVATE_KEY
   PROD_HOST
   PROD_USER
   
   # Notifications
   SLACK_WEBHOOK_URL
   ```

3. **Register GitLab Runner:**
   ```bash
   sudo gitlab-runner register
   # Choose Docker executor
   # Select docker:24-dind as image
   ```

4. **Push to trigger pipeline:**
   ```bash
   git add .
   git commit -m "Add GitLab CI/CD"
   git push origin develop  # For staging
   git push origin main     # For production
   ```

## Configuration

### Server Setup

#### 1. Prepare Deployment Server

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create application directory
sudo mkdir -p /opt/ecom-app
sudo chown $USER:$USER /opt/ecom-app
cd /opt/ecom-app

# Copy deployment files
# docker-compose.yml, .env, etc.
```

#### 2. Configure SSH Access

```bash
# On CI/CD server, generate SSH key
ssh-keygen -t ed25519 -C "cicd@ecom-app"

# Copy public key to deployment server
ssh-copy-id user@deployment-server

# Add private key to CI/CD secrets
cat ~/.ssh/id_ed25519  # Copy this to CI/CD secrets
```

#### 3. Setup Environment Variables

```bash
cd /opt/ecom-app
cp .env.example .env
nano .env

# Update all values with production credentials
```

### Docker Configuration

The Dockerfile includes:
- **Multi-stage builds** for smaller image size
- **Non-root user** for security
- **Health checks** for container monitoring
- **Build arguments** for versioning
- **Layer caching** for faster builds

### Monitoring Setup

#### 1. Prometheus Configuration

Create `monitoring/prometheus.yml`:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ecom-app'
    static_configs:
      - targets: ['streamlit-app:8501']
```

#### 2. Grafana Dashboards

Access Grafana at `http://your-server:3000`
- Default credentials: admin/admin
- Add Prometheus datasource
- Import pre-built Streamlit dashboards

## Deployment Process

### Automatic Deployment (Staging)

Triggered on push to `develop` branch:
1. Code pushed to develop
2. Pipeline runs all stages
3. If all checks pass, deploys to staging
4. Health check performed
5. Slack notification sent

### Manual Deployment (Production)

Triggered on push to `main` branch:
1. Code pushed to main
2. Pipeline runs all stages
3. Waits for manual approval
4. DevOps engineer approves deployment
5. Deploys to production with backup
6. Health check with auto-rollback
7. Notification sent

### Using Deployment Script

```bash
# Deploy to production
./deploy.sh production deploy

# Rollback to previous version
./deploy.sh production rollback

# View logs
./deploy.sh production logs

# Check status
./deploy.sh production status
```

## Monitoring & Rollback

### Health Checks

The application includes built-in health checks:
- Container health: Docker healthcheck
- Application health: Streamlit health endpoint
- Database connectivity (if applicable)

### Automatic Rollback

If health checks fail after deployment:
1. Pipeline stops
2. Previous container state restored
3. Backup configuration applied
4. Health check re-verified
5. Team notified

### Manual Rollback

```bash
# Using deployment script
./deploy.sh production rollback

# Using Docker Compose
cd /opt/ecom-app
docker-compose -f backups/docker-compose.state_TIMESTAMP.yml up -d
```

### Monitoring Dashboards

- **Grafana**: Real-time metrics and alerts
- **Prometheus**: Time-series data collection
- **Docker stats**: Container resource usage
- **Application logs**: via `docker-compose logs`

## Best Practices

### 1. Version Control
- Use semantic versioning (v1.0.0)
- Tag releases in Git
- Maintain CHANGELOG.md

### 2. Branch Strategy
```
main (production)
├── develop (staging)
│   ├── feature/new-feature
│   ├── bugfix/fix-issue
│   └── hotfix/critical-fix
```

### 3. Security
- Never commit secrets to Git
- Use secret management (AWS Secrets Manager, HashiCorp Vault)
- Scan dependencies regularly
- Keep base images updated
- Use non-root containers

### 4. Testing
- Write unit tests for critical functions
- Maintain >80% code coverage
- Run integration tests in staging
- Perform smoke tests post-deployment

### 5. Monitoring
- Set up alerts for critical metrics
- Monitor application logs
- Track deployment frequency
- Measure MTTR (Mean Time To Recovery)

### 6. Documentation
- Keep README.md updated
- Document API endpoints
- Maintain deployment runbook
- Update architecture diagrams

## Troubleshooting

### Common Issues

1. **Pipeline fails at build stage**
   ```bash
   # Check Docker daemon
   docker ps
   
   # Clear build cache
   docker builder prune -a
   ```

2. **Health check fails**
   ```bash
   # Check container logs
   docker-compose logs streamlit-app
   
   # Verify port accessibility
   curl http://localhost:8501/_stcore/health
   ```

3. **SSH connection fails**
   ```bash
   # Verify SSH key permissions
   chmod 600 ~/.ssh/id_rsa
   
   # Test connection
   ssh -vvv user@host
   ```

4. **Image pull fails**
   ```bash
   # Login to registry
   docker login ghcr.io
   
   # Check image exists
   docker manifest inspect ghcr.io/omkumarkaushik/ecom-app:latest
   ```

## Additional Resources

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Jenkins Pipeline Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [Streamlit Documentation](https://docs.streamlit.io/)

## Support

For issues or questions:
- Create an issue in the repository
- Contact: omkumarkaushik
- Slack: #ecom-support

---

**Last Updated**: February 2026
**Version**: 1.0.0
**Author**: Om Kumar Kaushik
