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
                echo "🔄 Cloning repository..."
                git(
                    url: 'https://github.com/Ans-fraz-cyber/voting-app-ci-cd.git',
                    branch: 'main'
                    // No credentials needed for public repo
                )
            }
        }

        stage('SonarQube Code Analysis') {
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
                timeout(time: 10, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
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
                        trivy image --format table -o trivy-vote-report.txt ${IMAGE_VOTE}:${BUILD_NUMBER}
                        trivy image --format table -o trivy-result-report.txt ${IMAGE_RESULT}:${BUILD_NUMBER}
                        trivy image --format table -o trivy-worker-report.txt ${IMAGE_WORKER}:${BUILD_NUMBER}
                    """
                    // Archive the reports
                    archiveArtifacts artifacts: 'trivy-*.txt', fingerprint: true
                    
                    // Display summary in console
                    sh """
                        echo "🔒 SECURITY SCAN SUMMARY"
                        echo "========================"
                        echo "Vote Service:"
                        cat trivy-vote-report.txt | head -10
                        echo ""
                        echo "Result Service:"
                        cat trivy-result-report.txt | head -10
                        echo ""
                        echo "Worker Service:"
                        cat trivy-worker-report.txt | head -10
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

                            docker tag ${IMAGE_VOTE}:${BUILD_NUMBER} ${DOCKERHUB_NAMESPACE}/voting-app-vote:latest
                            docker tag ${IMAGE_RESULT}:${BUILD_NUMBER} ${DOCKERHUB_NAMESPACE}/voting-app-result:latest  
                            docker tag ${IMAGE_WORKER}:${BUILD_NUMBER} ${DOCKERHUB_NAMESPACE}/voting-app-worker:latest

                            docker push ${DOCKERHUB_NAMESPACE}/voting-app-vote:${BUILD_NUMBER}
                            docker push ${DOCKERHUB_NAMESPACE}/voting-app-result:${BUILD_NUMBER}
                            docker push ${DOCKERHUB_NAMESPACE}/voting-app-worker:${BUILD_NUMBER}

                            docker push ${DOCKERHUB_NAMESPACE}/voting-app-vote:latest
                            docker push ${DOCKERHUB_NAMESPACE}/voting-app-result:latest
                            docker push ${DOCKERHUB_NAMESPACE}/voting-app-worker:latest
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
                    sleep 20
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
                
                Security Reports: Download from Jenkins artifacts
                SonarQube: http://localhost:9000/dashboard?id=voting-app
                
                Deployment:
                - Vote: http://localhost:5000
                - Result: http://localhost:5001
                """
            )
        }
        
        success {
            echo "🎉 Pipeline executed successfully!"
            echo "✅ SonarQube Quality Gate: PASSED"
            echo "🔒 Trivy Security Scans: COMPLETED"
            echo "🐳 Docker Images: PUSHED"
            echo "🚀 Application: DEPLOYED"
        }
        
        failure {
            echo "❌ Pipeline failed - check console output for details"
        }
    }
}
