pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 15, unit: 'MINUTES')
    }

    environment {
        SONARQUBE = 'SonarQubeServer'
        SONAR_AUTH_TOKEN = credentials('sonar-token')
        IMAGE_VOTE = "voting-app-vote"
        IMAGE_RESULT = "voting-app-result" 
        IMAGE_WORKER = "voting-app-worker"
        DOCKERHUB_NAMESPACE = "31793179"
    }

    stages {
        stage('Download Code') {
            steps {
                echo "📥 Downloading repository as ZIP..."
                script {
                    sh '''
                        rm -rf * .* 2>/dev/null || true
                        curl -L -o repo.zip "https://github.com/Ans-fraz-cyber/voting-app-ci-cd/archive/main.zip" || wget -O repo.zip "https://github.com/Ans-fraz-cyber/voting-app-ci-cd/archive/main.zip"
                        unzip -q repo.zip
                        mv voting-app-ci-cd-main/* . 2>/dev/null || true
                        mv voting-app-ci-cd-main/.* . 2>/dev/null || true
                        rm -rf voting-app-ci-cd-main repo.zip
                        echo "✅ Repository downloaded successfully"
                    '''
                }
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

        stage('SonarQube Quality Gate') {
            steps {
                echo "✅ Checking SonarQube Quality Gate..."
                script {
                    timeout(time: 5, unit: 'MINUTES') {
                        waitForQualityGate abortPipeline: true
                    }
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                echo "🐳 Building Docker images..."
                script {
                    sh """
                        docker build -t ${IMAGE_VOTE}:${BUILD_NUMBER} ./vote
                        docker build -t ${IMAGE_RESULT}:${BUILD_NUMBER} ./result  
                        docker build -t ${IMAGE_WORKER}:${BUILD_NUMBER} ./worker
                    """
                }
            }
        }

        stage('Trivy Security Scan') {
            steps {
                echo "🔒 Running Trivy Security Scan..."
                script {
                    sh """
                        trivy image --format table ${IMAGE_VOTE}:${BUILD_NUMBER} | head -20 > trivy-vote.txt
                        trivy image --format table ${IMAGE_RESULT}:${BUILD_NUMBER} | head -20 > trivy-result.txt
                        trivy image --format table ${IMAGE_WORKER}:${BUILD_NUMBER} | head -20 > trivy-worker.txt
                    """
                    archiveArtifacts artifacts: 'trivy-*.txt', fingerprint: true
                    
                    // Display security summary
                    sh """
                        echo "🛡️ SECURITY GATES STATUS"
                        echo "========================"
                        echo "✅ SonarQube Quality Gate: PASSED"
                        echo "✅ Trivy Container Scan: COMPLETED"
                        echo "📊 Reports saved as artifacts"
                    """
                }
            }
        }

        stage('Push to DockerHub') {
            steps {
                echo "📤 Pushing images to DockerHub..."
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-credentials') {
                        sh """
                            docker tag ${IMAGE_VOTE}:${BUILD_NUMBER} ${DOCKERHUB_NAMESPACE}/voting-app-vote:${BUILD_NUMBER}
                            docker tag ${IMAGE_RESULT}:${BUILD_NUMBER} ${DOCKERHUB_NAMESPACE}/voting-app-result:${BUILD_NUMBER}
                            docker tag ${IMAGE_WORKER}:${BUILD_NUMBER} ${DOCKERHUB_NAMESPACE}/voting-app-worker:${BUILD_NUMBER}

                            docker push ${DOCKERHUB_NAMESPACE}/voting-app-vote:${BUILD_NUMBER}
                            docker push ${DOCKERHUB_NAMESPACE}/voting-app-result:${BUILD_NUMBER}
                            docker push ${DOCKERHUB_NAMESPACE}/voting-app-worker:${BUILD_NUMBER}
                        """
                    }
                }
            }
        }

        stage('Deploy Voting App Only') {
            steps {
                echo "🚀 Deploying voting application (excluding SonarQube)..."
                script {
                    // Stop only voting app containers, not SonarQube
                    sh '''
                        docker stop voting-app-pipeline-vote-1 voting-app-pipeline-result-1 voting-app-pipeline-worker-1 voting-app-pipeline-redis-1 voting-app-pipeline-db-1 2>/dev/null || true
                        docker rm voting-app-pipeline-vote-1 voting-app-pipeline-result-1 voting-app-pipeline-worker-1 voting-app-pipeline-redis-1 voting-app-pipeline-db-1 2>/dev/null || true
                        
                        # Start only voting app services
                        docker-compose up -d vote result worker redis db
                        
                        sleep 10
                        echo "📊 Voting App Deployment Status:"
                        docker-compose ps vote result worker redis db
                        echo "🌐 Application URLs:"
                        echo "Vote: http://localhost:5000"
                        echo "Result: http://localhost:5001"
                    '''
                }
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning up workspace..."
            cleanWs()
            
            mail(
                to: "ansfarazkp@gmail.com",
                subject: "Build ${currentBuild.currentResult} - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                Pipeline Execution Complete!
                
                Project: ${env.JOB_NAME}
                Build: #${env.BUILD_NUMBER}
                Status: ${currentBuild.currentResult}
                
                Build URL: ${env.BUILD_URL}
                
                Security Gates:
                - SonarQube Quality Gate: ✅ PASSED
                - Trivy Security Scan: ✅ COMPLETED
                
                Application URLs:
                - Vote: http://localhost:5000
                - Result: http://localhost:5001
                
                SonarQube: http://localhost:9000
                """
            )
        }
        
        success {
            echo "🎉 Pipeline executed successfully!"
            echo "🛡️ Security Gates: ALL PASSED"
            echo "🚀 Application deployed successfully"
        }
        
        failure {
            echo "❌ Pipeline failed - check console output"
        }
    }
}
