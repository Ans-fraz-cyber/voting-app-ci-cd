pipeline {
    agent any

    options {
        skipDefaultCheckout(true)   // 👈 disables "Declarative: Checkout SCM"
    }

    environment {
        SONARQUBE = 'SonarQubeServer'        // must match Jenkins > Configure System
        SONAR_AUTH_TOKEN = credentials('sonar-token')
    }

    stages {
        stage('Code Clone') {
            steps {
                echo "🔄 Cloning repository..."
                git url: 'https://github.com/Ans-fraz-cyber/voting-app-ci-cd.git', branch: 'main'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo "🔍 Running SonarQube Analysis..."
                withSonarQubeEnv("${SONARQUBE}") {
                    script {
                        def scannerHome = tool 'SonarQubeScanner'
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                              -Dsonar.projectKey=voting-app \
                              -Dsonar.projectName=voting-app \
                              -Dsonar.sources=. \
                              -Dsonar.login=${SONAR_AUTH_TOKEN}
                        """
                    }
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                echo "🐳 Building Docker images for vote, result, and worker..."
                sh '''
                    docker build -t voting-app-vote:latest ./vote
                    docker build -t voting-app-result:latest ./result
                    docker build -t voting-app-worker:latest ./worker
                '''
            }
        }

        stage('Trivy Scan') {
            steps {
                echo "🔎 Running Trivy vulnerability scan on all services..."
                sh '''
                    trivy image --exit-code 0 --severity HIGH,CRITICAL voting-app-vote:latest
                    trivy image --exit-code 0 --severity HIGH,CRITICAL voting-app-result:latest
                    trivy image --exit-code 0 --severity HIGH,CRITICAL voting-app-worker:latest
                '''
            }
        }

        stage('Push to DockerHub') {
            steps {
                script {
                    echo "📤 Pushing images to DockerHub..."
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-credentials') {
                        sh '''
                            # Tag images with build number
                            docker tag voting-app-vote:latest 31793179/voting-app-vote:${BUILD_NUMBER}
                            docker tag voting-app-result:latest 31793179/voting-app-result:${BUILD_NUMBER}
                            docker tag voting-app-worker:latest 31793179/voting-app-worker:${BUILD_NUMBER}

                            # Also tag them as :latest under DockerHub repo
                            docker tag voting-app-vote:latest 31793179/voting-app-vote:latest
                            docker tag voting-app-result:latest 31793179/voting-app-result:latest
                            docker tag voting-app-worker:latest 31793179/voting-app-worker:latest

                            # Push all tags
                            docker push 31793179/voting-app-vote:${BUILD_NUMBER}
                            docker push 31793179/voting-app-result:${BUILD_NUMBER}
                            docker push 31793179/voting-app-worker:${BUILD_NUMBER}

                            docker push 31793179/voting-app-vote:latest
                            docker push 31793179/voting-app-result:latest
                            docker push 31793179/voting-app-worker:latest
                        '''
                    }
                }
            }
        }

        // 🚀 NEW DEPLOYMENT STAGE - FIXED VERSION
        stage('Deploy Application') {
            steps {
                echo "🚀 Deploying voting application..."
                sh '''
                    # Stop and remove ONLY voting app containers (not SonarQube)
                    docker stop voting-app-vote-1 voting-app-result-1 voting-app-worker-1 voting-app-redis-1 voting-app-db-1 2>/dev/null || true
                    docker rm voting-app-vote-1 voting-app-result-1 voting-app-worker-1 voting-app-redis-1 voting-app-db-1 2>/dev/null || true
                    
                    # Start only voting app services (SonarQube will continue running)
                    docker compose up -d vote result worker redis db
                    
                    # Wait for services to be ready
                    sleep 30
                    
                    # Check if containers are running
                    echo "📊 Deployment status:"
                    docker ps | grep voting-app
                '''
            }
        }
    }

    post {
        always {
            mail(
                to: "ansfarazkp@gmail.com",
                subject: "Jenkins Build Status: ${currentBuild.fullDisplayName}",
                body: "The Jenkins build ${currentBuild.fullDisplayName} finished with status: ${currentBuild.currentResult}. Check details here: ${env.BUILD_URL}"
            )
        }
    }
}
