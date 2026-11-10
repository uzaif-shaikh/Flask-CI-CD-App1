pipeline {
    agent any

    environment {
        IMAGE_NAME     = 'flask-todo'
        CONTAINER_NAME = 'flask-todo'
        HOST_PORT      = '80'
        APP_PORT       = '5000'
    }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 15, unit: 'MINUTES')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                // Builds the "test" stage of the Dockerfile; pytest runs inside it.
                // A failing test fails this stage and stops the pipeline.
                sh 'docker build --target test -t ${IMAGE_NAME}:test .'
            }
        }

        stage('Build Image') {
            steps {
                sh '''
                    docker build --target runtime \
                      -t ${IMAGE_NAME}:${BUILD_NUMBER} \
                      -t ${IMAGE_NAME}:latest .
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker rm -f ${CONTAINER_NAME} || true
                    docker run -d \
                      --name ${CONTAINER_NAME} \
                      --restart unless-stopped \
                      -p ${HOST_PORT}:${APP_PORT} \
                      ${IMAGE_NAME}:${BUILD_NUMBER}
                '''
            }
        }

        stage('Smoke Test') {
            steps {
                // Retry for up to ~30s while the container starts
                sh '''
                    for i in $(seq 1 10); do
                      if curl -fs http://localhost:${HOST_PORT}/health; then
                        echo "App is healthy"
                        exit 0
                      fi
                      echo "Waiting for app... ($i/10)"
                      sleep 3
                    done
                    echo "Smoke test failed"
                    docker logs ${CONTAINER_NAME}
                    exit 1
                '''
            }
        }
    }

    post {
        success {
            echo "Deployed build #${env.BUILD_NUMBER} successfully."
        }
        failure {
            echo "Build #${env.BUILD_NUMBER} failed. Check the stage logs above."
        }
        always {
            // Clean up dangling images so the small EC2 disk doesn't fill up
            sh 'docker image prune -f || true'
        }
    }
}
