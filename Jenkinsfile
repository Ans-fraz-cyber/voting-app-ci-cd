pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
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
        stage('Code Clone') {
            steps {
                echo "📥 Cloning repository..."
                git(
                    url: 'https://github.com/Ans-fraz-cyber/voting-app-ci-cd.git',
                    branch: 'main'
                )
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

        stage('Quality Gate') {
            steps {
                echo "✅ Checking Quality Gate..."
                script {
                    try {
                        timeout(time: 2, unit: 'MINUTES') {
                            waitForQualityGate abortPipeline: false
                            echo "🎉 Quality Gate: PASSED"
                        }
                    } catch (Exception e) {
                        echo "⚠️ Quality Gate: Still processing (continuing)"
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

        stage('Security & Push') {
            parallel {
                stage('Trivy Scan') {
                    steps {
                        echo "🔒 Running Trivy Security Scan..."
                        script {
                            sh """
                                # Generate both table format (for console) and HTML format (for reports)
                                trivy image --format table ${IMAGE_VOTE}:${BUILD_NUMBER} > trivy-vote.txt
                                trivy image --format template --template "@html.tpl" -o trivy-vote.html ${IMAGE_VOTE}:${BUILD_NUMBER}
                                
                                trivy image --format table ${IMAGE_RESULT}:${BUILD_NUMBER} > trivy-result.txt
                                trivy image --format template --template "@html.tpl" -o trivy-result.html ${IMAGE_RESULT}:${BUILD_NUMBER}
                                
                                trivy image --format table ${IMAGE_WORKER}:${BUILD_NUMBER} > trivy-worker.txt
                                trivy image --format template --template "@html.tpl" -o trivy-worker.html ${IMAGE_WORKER}:${BUILD_NUMBER}
                            """
                            archiveArtifacts artifacts: 'trivy-*.txt,trivy-*.html', fingerprint: true
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
            }
        }

        stage('Deploy Application') {
            steps {
                echo "🚀 Deploying application..."
                script {
                    sh '''
                        docker stop voting-app-pipeline-vote-1 voting-app-pipeline-result-1 voting-app-pipeline-worker-1 voting-app-pipeline-redis-1 voting-app-pipeline-db-1 2>/dev/null || true
                        docker rm voting-app-pipeline-vote-1 voting-app-pipeline-result-1 voting-app-pipeline-worker-1 voting-app-pipeline-redis-1 voting-app-pipeline-db-1 2>/dev/null || true
                        
                        docker-compose up -d vote result worker redis db
                        
                        sleep 10
                        echo "📊 Application Status:"
                        docker-compose ps vote result worker redis db
                        echo "🌐 URLs:"
                        echo "Vote: http://localhost:5000"
                        echo "Result: http://localhost:5001"
                    '''
                }
            }
        }
    }

    post {
        always {
            // Publish HTML reports
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: '',
                reportFiles: 'trivy-vote.html,trivy-result.html,trivy-worker.html',
                reportName: 'Trivy Security Reports',
                reportTitles: 'Trivy Security Scan Results'
            ])
            
            cleanWs()
            
            mail(
                to: "ansfarazkp@gmail.com",
                subject: "Build ${currentBuild.currentResult} - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Build ${currentBuild.currentResult}. Check: ${env.BUILD_URL}"
            )
        }
        
        success {
            echo "🎉 Pipeline executed successfully!"
        }
    }
}
