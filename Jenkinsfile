pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.11'
        DOCKER_REGISTRY = 'ghcr.io'
        IMAGE_NAME = "omkumarkaushik/ecom-app"
        DOCKER_CREDENTIALS_ID = 'docker-registry-credentials'
        SSH_CREDENTIALS_ID = 'ssh-deployment-key'
        STAGING_HOST = credentials('staging-host')
        PROD_HOST = credentials('prod-host')
        SLACK_CHANNEL = '#ecom-deployments'
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
        timeout(time: 1, unit: 'HOURS')
        disableConcurrentBuilds()
    }
    
    triggers {
        pollSCM('H/5 * * * *')
        githubPush()
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(
                        script: "git rev-parse --short HEAD",
                        returnStdout: true
                    ).trim()
                    env.BUILD_TAG = "${env.BRANCH_NAME}-${env.GIT_COMMIT_SHORT}-${env.BUILD_NUMBER}"
                }
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install flake8 pytest pytest-cov black isort pylint bandit safety
                    if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
                    if [ -f app/requirements.txt ]; then pip install -r app/requirements.txt; fi
                '''
            }
        }
        
        stage('Code Quality & Security') {
            parallel {
                stage('Lint - Black') {
                    steps {
                        sh '''
                            . venv/bin/activate
                            black --check --diff . || true
                        '''
                    }
                }
                
                stage('Lint - Flake8') {
                    steps {
                        sh '''
                            . venv/bin/activate
                            flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
                            flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics --format=pylint > flake8-report.txt
                        '''
                        recordIssues(tools: [flake8(pattern: 'flake8-report.txt')])
                    }
                }
                
                stage('Security - Bandit') {
                    steps {
                        sh '''
                            . venv/bin/activate
                            bandit -r . -f json -o bandit-report.json || true
                            bandit -r . -ll
                        '''
                    }
                }
                
                stage('Dependency Check') {
                    steps {
                        sh '''
                            . venv/bin/activate
                            safety check --json > safety-report.json || true
                        '''
                    }
                }
            }
        }
        
        stage('Unit Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    if [ -d "tests" ]; then
                        pytest tests/ --cov=. --cov-report=xml --cov-report=html --cov-report=term --junitxml=test-results.xml
                    else
                        echo "No tests directory found"
                    fi
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-results.xml'
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: false,
                        keepAll: true,
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    docker.withRegistry("https://${DOCKER_REGISTRY}", DOCKER_CREDENTIALS_ID) {
                        def customImage = docker.build(
                            "${DOCKER_REGISTRY}/${IMAGE_NAME}:${BUILD_TAG}",
                            "--build-arg BUILD_DATE=\$(date -u +'%Y-%m-%dT%H:%M:%SZ') " +
                            "--build-arg VCS_REF=${GIT_COMMIT_SHORT} " +
                            "--build-arg VERSION=${BUILD_TAG} " +
                            "--cache-from ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest " +
                            "."
                        )
                        
                        customImage.push()
                        customImage.push('latest')
                        
                        if (env.BRANCH_NAME == 'main') {
                            customImage.push('stable')
                        }
                    }
                }
            }
        }
        
        stage('Container Security Scan') {
            steps {
                script {
                    sh """
                        docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                        aquasec/trivy image \
                        --severity HIGH,CRITICAL \
                        --format json \
                        --output trivy-report.json \
                        ${DOCKER_REGISTRY}/${IMAGE_NAME}:${BUILD_TAG} || true
                    """
                }
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                script {
                    sshagent([SSH_CREDENTIALS_ID]) {
                        sh """
                            ssh -o StrictHostKeyChecking=no ubuntu@${STAGING_HOST} << 'ENDSSH'
                                cd /opt/ecom-app
                                export IMAGE_TAG=${BUILD_TAG}
                                docker-compose pull
                                docker-compose down
                                docker-compose up -d
                                docker-compose ps
                            ENDSSH
                        """
                    }
                }
            }
        }
        
        stage('Staging Tests') {
            when {
                branch 'develop'
            }
            steps {
                sh '''
                    sleep 10
                    curl -f http://${STAGING_HOST}:8501/health || echo "Health check endpoint not available"
                '''
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                input message: 'Deploy to Production?', ok: 'Deploy'
                
                script {
                    sshagent([SSH_CREDENTIALS_ID]) {
                        sh """
                            ssh -o StrictHostKeyChecking=no ubuntu@${PROD_HOST} << 'ENDSSH'
                                cd /opt/ecom-app
                                
                                # Backup current deployment
                                docker-compose config > docker-compose.backup.yml
                                
                                # Deploy new version
                                export IMAGE_TAG=${BUILD_TAG}
                                docker-compose pull
                                docker-compose up -d --no-deps --build
                                
                                # Health check
                                sleep 15
                                if ! curl -f http://localhost:8501/health; then
                                    echo "Health check failed, rolling back..."
                                    docker-compose down
                                    docker-compose -f docker-compose.backup.yml up -d
                                    exit 1
                                fi
                                
                                # Cleanup old images
                                docker image prune -f
                            ENDSSH
                        """
                    }
                }
            }
        }
        
        stage('Smoke Tests') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    sleep 10
                    curl -f http://${PROD_HOST}:8501/health || echo "Health check endpoint not available"
                '''
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        
        success {
            slackSend(
                channel: SLACK_CHANNEL,
                color: 'good',
                message: "✅ Pipeline SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}\nBranch: ${env.BRANCH_NAME}\nCommit: ${env.GIT_COMMIT_SHORT}"
            )
        }
        
        failure {
            slackSend(
                channel: SLACK_CHANNEL,
                color: 'danger',
                message: "❌ Pipeline FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}\nBranch: ${env.BRANCH_NAME}\nCommit: ${env.GIT_COMMIT_SHORT}"
            )
        }
        
        unstable {
            slackSend(
                channel: SLACK_CHANNEL,
                color: 'warning',
                message: "⚠️ Pipeline UNSTABLE: ${env.JOB_NAME} #${env.BUILD_NUMBER}\nBranch: ${env.BRANCH_NAME}\nCommit: ${env.GIT_COMMIT_SHORT}"
            )
        }
    }
}
