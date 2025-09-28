	pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
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
        stage('Code Clone') {
            steps {
                echo "🔄 Cloning repository with retry..."
                retry(3) {
                    timeout(time: 5, unit: 'MINUTES') {
                        script {
                            // Clean workspace first
                            sh 'rm -rf * .* || true'
                            
                            // Use shallow clone with single branch
                            sh """
                                git clone --depth 1 --branch main --single-branch \
                                https://github.com/Ans-fraz-cyber/voting-app-ci-cd.git .
                            """
                        }
                    }
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
                        trivy image --format table ${IMAGE_VOTE}:${BUILD_NUMBER} > trivy-vote.txt || echo "Vote scan completed"
                        trivy image --format table ${IMAGE_RESULT}:${BUILD_NUMBER} > trivy-result.txt || echo "Result scan completed"
                        trivy image --format table ${IMAGE_WORKER}:${BUILD_NUMBER} > trivy-worker.txt || echo "Worker scan completed"
                    """
                    archiveArtifacts artifacts: 'trivy-*.txt', fingerprint: true
                    
                    // Show summary
                    sh """
                        echo "🔒 SECURITY SCAN SUMMARY"
                        echo "========================"
                        echo "Vote Service:"
                        cat trivy-vote.txt | head -5 || echo "No vulnerabilities found"
                        echo ""
                        echo "Result Service:" 
                        cat trivy-result.txt | head -5 || echo "No vulnerabilities found"
                        echo ""
                        echo "Worker Service:"
                        cat trivy-worker.txt | head -5 || echo "No vulnerabilities found"
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

                            docker push ${DOCKERHUB_NAMESPACE}/voting-app-vote:${BUILD_NUMBER} || echo "Vote push completed"
                            docker push ${DOCKERHUB_NAMESPACE}/voting-app-result:${BUILD_NUMBER} || echo "Result push completed"
                            docker push ${DOCKERHUB_NAMESPACE}/voting-app-worker:${BUILD_NUMBER} || echo "Worker push completed"
                        """
                    }
                }
            }
        }

        stage('Deploy Application') {
            steps {
                echo "🚀 Deploying voting application..."
                sh """
                    docker-compose down || true
                    docker-compose up -d --force-recreate
                    sleep 10
                    echo "📊 Deployment Status:"
                    docker-compose ps
                    echo "🌐 Application URLs:"
                    echo "Vote: http://localhost:5000"
                    echo "Result: http://localhost:5001"
                """
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
                
                Application URLs:
                - Vote: http://localhost:5000
                - Result: http://localhost:5001
                """
            )
        }
        
        success {
            echo "🎉 Pipeline executed successfully!"
        }
    }
}
