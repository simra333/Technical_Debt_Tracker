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
    - name: azure-cli
      image: mcr.microsoft.com/azure-cli:latest
      command:
      - cat
      tty: true
    - name: kubectl
      image: bitnami/kubectl:latest
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
        DEPLOYMENT_NAME = 'tdtracker-deployment'
        CONTAINER_NAME = 'tdtracker-container'
        AKS_CLUSTER_NAME = 'tdtracker-aks'
        AKS_RESOURCE_GROUP = 'tdtracker-rg'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/simra333/Technical_Debt_Tracker.git'
            }
        }
        // stage('Run Unit Tests') {
        //     steps {
        //         sh '''
        //             python -m venv venv
        //             . venv/bin/activate
        //             pip install -r requirements.txt
        //             python -m unittest discover -s tests
        //             sh 'echo Unit Tests completed successfully!'
        //         '''
        //     }
        // }

        stage('az login with Managed Identity') {
            steps {
                sh '''
                    az login --identity
                    az ad signed-in-user show
                    az aks show -g tdtracker-rg -n tdtracker-aks --query identity
                    az aks show -g tdtracker-rg -n tdtracker-aks --query identityProfile        
                '''
            }
        }
        stage('Build & Push to ACR') {
            steps {
                container('azure-cli') {
                    sh '''
                        az login --identity
                        az account set --subscription 7d7c4617-06a8-4d8b-8dfc-d31d8d7e18eb
                        az account show
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
    }
}

