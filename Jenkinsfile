pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
    containers:
    - name: docker
        image: docker:latest
        command:
        - cat
        tty: true
        volumeMounts:
        - mountPath: /var/run/docker.sock
          name: docker-sock
    volumes:
    - name: docker-sock
        hostPath:
          path: /var/run/docker.sock
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
        stage('Build Docker Image') {
            steps {
                sh """
                    docker build -t ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG} .
                """
            }
        }
    }
}

