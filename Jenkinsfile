pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
metadata:
    labels:
        jenkins: agent
spec:
    serviceAccountName: default
    containers: 
    - name: devops-tools 
      image: tdtrackeracr.azurecr.io/azure-kubectl:1.0.0 
      command: 
      - cat 
      tty: true
    - name: python
      image: python:3.10-slim
      command:
      - cat
      tty: true
    - name: trufflehog
      image: trufflesecurity/trufflehog:latest
      command: 
      - cat
      tty: true
'''
        }
    }

    parameters {
    choice(name: 'FF_CATEGORY_DROPDOWN', choices: ['true', 'false'], description: 'Feature flag: show Category dropdown in UI')
}

    environment {
        ACR_NAME = 'tdtrackeracr'
        ACR_LOGIN_SERVER = 'tdtrackeracr.azurecr.io'
        IMAGE_NAME = 'technical-debt-tracker'
        APP_DIR = 'app'
        NAMESPACE = 'default'
        IMAGE_TAG = "${BUILD_NUMBER}"
        DEPLOYMENT_NAME = 'tdt-dev'
        CONTAINER_NAME = 'tdt-dev'
        AKS_CLUSTER_NAME = 'TDT-aks-cluster'
        AKS_RESOURCE_GROUP = 'TDT-RG-Terraform'
        SERVICE_NAME = 'tdt-dev-service'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/simra333/Technical_Debt_Tracker.git'
            }
        }
        stage('Run Unit Tests') {
            steps {
                container ('python') {
                    withCredentials([string(credentialsId: 'flask-secret-key', variable: 'SECRET_KEY')]) {
                        sh '''
                            python -m venv venv
                            . venv/bin/activate
                            pip install --upgrade pip
                            pip install -r requirements-dev.txt

                            pytest tests/ \
                                --junitxml=test-results.xml \
                                --cov=app \
                                --cov-report=xml
                        '''
                    }
                }
            }
            post {
                always {
                    junit 'test-results.xml'
                    publishCoverage adapters: [coberturaAdapter('coverage.xml')]
                }
            }
        }
        stage('Dependency Vulnerability Scan') {
            steps {
                container('python') {
                    sh '''
                        set -e
                        echo "Running dependency vulnerability scan..."
                        . venv/bin/activate
                        pip install pip-audit
                        pip-audit -r requirements.txt --strict -f json -o pip-audit-report.json

                        echo "No known vulnerabilities found"

                        echo ""
                        echo "=== Suggested Fixes (Dry Run) ==="

                        # Show what would be fixed (no changes applied)
                        pip-audit -r requirements.txt --fix --dry-run || true
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'pip-audit-report.json', allowEmptyArchive: true
                }
            }
        }
        stage('TruffleHog Scan') {
            steps{
                container('trufflehog') {
                    sh '''
                        echo "Scanning for secrets..."

                        trufflehog filesystem ${APP_DIR} --json > trufflehog-report.json 

                        if [ -s trufflehog-report.json ]; then
                            echo "WARNING: Secrets detected!"
                            cat trufflehog-report.json
                            exit 1
                        else
                            echo "No secrets detected by TruffleHog Scan."
                        fi
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'trufflehog-report.json', allowEmptyArchive: true
                }
            }
        }
        stage('Log in to Azure') {
            steps {
                container('devops-tools') {
                    sh '''
                        az login --identity
                        az account show
                    '''
                }
            }
        }
        stage('Build & Push to ACR') {
            steps {
                container('devops-tools') {
                    sh '''
                        az acr list -o table
                        az acr build \
                        --registry ${ACR_NAME} \
                        --image ${IMAGE_NAME}:${IMAGE_TAG} \
                        --file Dockerfile \
                        .
                    '''
                }
            }
        }
        stage('Deploy to AKS') {
            steps {
                container('devops-tools') {
                    sh '''
                        az aks get-credentials --resource-group ${AKS_RESOURCE_GROUP} --name ${AKS_CLUSTER_NAME}

                        # Update deployment with new image
                        kubectl set image deployment/${DEPLOYMENT_NAME} \
                            ${CONTAINER_NAME}=${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG} \
                            --namespace ${NAMESPACE}

                        kubectl set env deployment/${DEPLOYMENT_NAME} --namespace ${NAMESPACE} FF_CATEGORY_DROPDOWN=${FF_CATEGORY_DROPDOWN}

                        # Check rollout status
                        kubectl rollout status deployment/${DEPLOYMENT_NAME} --namespace ${NAMESPACE}

                        # Get service information
                        kubectl get service --namespace ${NAMESPACE}
                    '''
                }
            }
        }
        stage('Post-Deployment Test') {
            steps {
                container('devops-tools') {
                    sh '''
                        set -e

                        echo "Running post-deployment tests..."

                        APP_IP=$(kubectl get svc ${SERVICE_NAME} -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
                        echo "Service external IP: ${APP_IP}"

                        curl -fsS http://${APP_IP}/health
                        echo "Post-deployment tests passed successfully - /health is reachable."
                    '''
                }
            }
        }
    }
}

