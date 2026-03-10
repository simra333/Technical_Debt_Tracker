pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
    containers:
    - name: azure
      image: mcr.microsoft.com/azure-cli
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
        IMAGE_TAG = "${BUILD_NUMBER}"
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
        stage('Build & Push to ACR') {
            steps {
                container('azure') {
                    sh """
                    az login --identity

                    # Show current subscription
                    echo "Current subscription:"
                    az account show --query "{name:name, id:id}" -o table

                    # List all ACRs in subscription
                    echo "All ACRs in subscription:"
                    az acr list --query "[].{Name:name, ResourceGroup:resourceGroup}" -o table

                    # Try to show specific ACR
                    echo "Checking ACR $ACR_NAME:"
                    az acr show --name $ACR_NAME --query "{name:name, loginServer:loginServer, resourceGroup:resourceGroup}" -o table

                    az acr build --registry $ACR_NAME \
                    --image ${IMAGE_NAME}:${BUILD_NUMBER} \
                    --image ${IMAGE_NAME}:latest \
                    --file Dockerfile \
                    .
                """
                }
            }
        }
    }
}

