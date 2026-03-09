pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
    containers:
    - name: docker
      image: docker:24-dind
      securityContext:
        privileged: true
      volumeMounts:
      - name: docker-graph-storage
        mountPath: /var/lib/docker
    volumes:
    - name: docker-graph-storage
      emptyDir: {}
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
                git branch: 'infrastructure/ci-cd-pipeline', url: 'https://github.com/simra333/Technical_Debt_Tracker.git'
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
        stage('Build Docker Image') {
            steps {
                container('docker') {
                    sh """
                    timeout 15 sh -c 'until docker info; do echo .; sleep 1; done'
                    docker build -t ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG} .
                """
                }
            }
        }
        stage('Push to ACR') {
            steps {
                container('docker') {
                    sh """
                    az acr login --name ${ACR_NAME}
                    docker push ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}
                    docker push ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:latest
                """
                }
            }
        }
    }
}

