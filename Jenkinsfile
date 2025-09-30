pipeline {
    agent any
    environment {
        GIT_URL = "https://github.com/Ans-fraz-cyber/voting-app-ci-cd.git"
        GIT_BRANCH = "main"
        IMAGE_VOTE = "ansfraz/voting-app-vote"
        IMAGE_RESULT = "ansfraz/voting-app-result"
        IMAGE_WORKER = "ansfraz/voting-app-worker"
        DOCKER_BUILDKIT = "1" 
        SONAR_URL = "http://localhost:9000/dashboard?id=voting-app"
        MAIL_FOR_APPROVAL = "ansfaraz.cyber@gmail.com"
        MAIL_FOR_FAIL_OR_SUCCESSFULL = "ansfaraz.cyber@gmail.com"
    }
    
    stages {
        // STAGE 1: Checkout
        stage('Checkout') {  
            steps {
                git branch: "${GIT_BRANCH}", url: "${GIT_URL}", credentialsId: 'github-token'
            }
        }

        // STAGE 2: SonarQube Quality Analysis
        stage('SonarQube Quality Analysis') {
            steps {
                script {
                    def SONAR_HOME = tool "Sonar"
                    withSonarQubeEnv("Sonar") {
                        sh "$SONAR_HOME/bin/sonar-scanner -Dsonar.projectName=voting-app -Dsonar.projectKey=voting-app -Dsonar.exclusions=**/trivy-*.html,**/*.html"
                    }
                }
            }
        }

        // STAGE 3: Sonar Quality Gate Scan
        stage('Sonar Quality Gate Scan') {
            steps {
                timeout(time: 10, unit: "MINUTES") {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        // STAGE 4: Docker Build
        stage('Docker Build') {
            steps {
                script {
                    sh """
                        docker build -t ${IMAGE_VOTE}:${BUILD_NUMBER} ./vote
                        docker build -t ${IMAGE_RESULT}:${BUILD_NUMBER} ./result
                        docker build -t ${IMAGE_WORKER}:${BUILD_NUMBER} ./worker
                    """
                }
            }
        }

        // STAGE 5: Scan and Push Images (Parallel)
        stage('Scan and Push Images') {
            parallel {
                // SUB-STAGE 5.1: Trivy Image Scan
                stage('Trivy Image Scan') {
                    steps {
                        script {
                            sh """
                                trivy image --format template --template @trivy-template.html -o trivy-vote-report.html ${IMAGE_VOTE}:${BUILD_NUMBER} || true
                                trivy image --format template --template @trivy-template.html -o trivy-result-report.html ${IMAGE_RESULT}:${BUILD_NUMBER} || true
                                trivy image --format template --template @trivy-template.html -o trivy-worker-report.html ${IMAGE_WORKER}:${BUILD_NUMBER} || true
                            """
                            archiveArtifacts artifacts: 'trivy-*-report.html', fingerprint: true
                        }
                    }
                }

                // SUB-STAGE 5.2: Docker Push
                stage('Docker Push') {
                    steps {
                        script {
                            withDockerRegistry(credentialsId: 'dockerhub-credentials') {
                                sh """
                                    docker push ${IMAGE_VOTE}:${BUILD_NUMBER}
                                    docker push ${IMAGE_RESULT}:${BUILD_NUMBER}
                                    docker push ${IMAGE_WORKER}:${BUILD_NUMBER}
                                """
                            }
                        }
                    }
                }
            }
        }

        // STAGE 6: Approval Required
        stage('Approval Required') {
            steps {
                script {
                    mail(
                        to: "${MAIL_FOR_APPROVAL}",
                        subject: "Approval Required for Deployment - Build #${BUILD_NUMBER}",
                        body: "SonarQube quality checks passed! Pipeline is waiting for your approval. Please go to Jenkins and click Deploy to continue."
                    )
                    input message: 'SonarQube Quality Gate PASSED! Approve deployment to production?', ok: 'Deploy'
                }
            }
        }

        // STAGE 7: Deploy using Docker compose
        stage('Deploy using Docker compose') {
            steps {
                sh "docker compose -f docker-compose.yml up -d"
            }
        }
    }
   
    post {
        success {
            script {
                echo "✅ Deployment successful!"
                mail(
                    to: "${MAIL_FOR_FAIL_OR_SUCCESSFULL}",
                    subject: "🚀 DEPLOYMENT SUCCESSFUL - Build #${BUILD_NUMBER}",
                    body: """ 
Hello Team,

🎉 Pipeline has successfully completed!

Build Number: ${BUILD_NUMBER}

🔍 Security & Quality Reports:
- SonarQube: ${SONAR_URL}
- Trivy Vote Report: ${env.BUILD_URL}artifact/trivy-vote-report.html
- Trivy Result Report: ${env.BUILD_URL}artifact/trivy-result-report.html
- Trivy Worker Report: ${env.BUILD_URL}artifact/trivy-worker-report.html

🌐 Application Links:
- Vote App: http://localhost:5000
- Result App: http://localhost:5001

Best regards,
Jenkins
"""
                )
            }
        }

        failure {
            script {
                echo "❌ Deployment failed!"
                mail(
                    to: "${MAIL_FOR_FAIL_OR_SUCCESSFULL}",
                    subject: "🚨 DEPLOYMENT FAILED - Build #${BUILD_NUMBER}",
                    body: """ 
Hello Team,

❌ Pipeline has failed!

Build Number: ${BUILD_NUMBER}

Please check the Jenkins console output for errors.

Best regards,
Jenkins
"""
                )
            }
        }
    }
}
