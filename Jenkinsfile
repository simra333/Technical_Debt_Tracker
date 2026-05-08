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
      image: tdtrackeracr.azurecr.io/tdt-python-ci:1.1
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
    choice(name: 'FF_CATEGORY_DROPDOWN', 
    choices: ['true', 'false'], 
    description: 'Feature flag: show Category dropdown in UI')
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
                checkout scm
            }
        }
        stage('Run Unit Tests') {
            steps {
                container ('python') {
                    withCredentials([string(credentialsId: 'flask-secret-key', variable: 'SECRET_KEY')]) {
                        sh '''
                            pytest tests/ \
                                --junitxml=test-results.xml \
                                --cov=app \
                                --cov-report=xml \
                                --cov-fail-under=80
                        '''
                    }
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'test-results.xml', allowEmptyArchive: true
                    archiveArtifacts artifacts: 'coverage.xml', allowEmptyArchive: true
                }
            }
        }
        stage('Static Application Security Testing - Bandit') {
            steps {
                container('python') {
                    sh '''
                        set -e
                        echo "Running Bandit SAST scan..."

                        bandit -r ${APP_DIR} -f json -o bandit-report.json

                        # Fail build if HIGH or MEDIUM issues exist
                        bandit -r ${APP_DIR} -lll
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'bandit-report.json', allowEmptyArchive: true
                }
            }
        }
        stage('Dependency Vulnerability Scan') {
            steps {
                container('python') {
                    sh '''
                        set -e
                        echo "Running dependency vulnerability scan..."

                        pip-audit -r requirements.txt --strict -f json -o pip-audit-report.json

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
                        --file docker/Dockerfile \
                        .
                    '''
                }
            }
        }
        stage('Deploy to AKS') {
            steps {
                container('devops-tools') {
                    sh '''
                        # Authenticate with AKS cluster
                        az aks get-credentials \
                            --resource-group ${AKS_RESOURCE_GROUP} \
                            --name ${AKS_CLUSTER_NAME}

                        # Update deployment with new image
                        kubectl set image deployment/${DEPLOYMENT_NAME} \
                            ${CONTAINER_NAME}=${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG} \
                            --namespace ${NAMESPACE}

                        # Update feature flag environment variable
                        kubectl set env deployment/${DEPLOYMENT_NAME} \
                        --namespace ${NAMESPACE} \
                        FF_CATEGORY_DROPDOWN=${FF_CATEGORY_DROPDOWN}

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

