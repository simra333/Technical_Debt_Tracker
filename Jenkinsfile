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
                    sh '''
                        python -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt

                        pip install pytest pytest-cov

                        pytest tests/ \
                            --junitxml=test-results.xml \
                            --cov=app \
                            --cov-report=xml
                    '''
                }
            }
        }
        stage('TruffleHog Scan') {
            steps{
                container('trufflehog') {
                    sh '''
                        echo "Scanning for secrets..."
                        # TruffleHog automatically scans the Jenkins workspace
                        trufflehog filesystem . --json > trufflehog-report.json || true

                        if [ -s trufflehog-report.json ]; then
                            echo "WARNING: Secrets detected!"
                            cat trufflehog-report.json
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

                        # Check rollout status
                        kubectl rollout status deployment/${DEPLOYMENT_NAME} --namespace ${NAMESPACE}

                        # Get service information
                        kubectl get service --namespace ${NAMESPACE}
                    '''
                }
            }
        }
    }
}

