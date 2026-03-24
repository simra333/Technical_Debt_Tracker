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
                git branch: 'feature/monitoring', url: 'https://github.com/simra333/Technical_Debt_Tracker.git'
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

        //    stage('az login with Managed Identity') {
        //     steps {
        //         container('azure-cli') {
        //             sh '''
        //                 az login --identity

        //                 az aks show -g tdtracker-rg -n tdtracker-aks --query identity
        
        //                 echo "=== SIGNED-IN USER ==="
        //                 az ad signed-in-user show
        
        //                 echo "=== AKS IDENTITY (Cluster Identity) ==="
        //                 az aks show -g tdtracker-rg -n tdtracker-aks --query identity
        
        //                 echo "=== AKS IDENTITY PROFILE (Kubelet / Nodepool MI) ==="
        //                 az aks show -g tdtracker-rg -n tdtracker-aks --query identityProfile
        //             '''
        //         }
        //     }
        // }
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
                            echo "No secrets detected."
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
        stage('Deploy to AKS') {
            steps {
                container('azure-cli') {
                    sh '''
                        az login --identity
                        az aks install-cli
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

