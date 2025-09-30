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
        stage('Checkout') {  
            steps {
                script {
                    echo '📥 Downloading voting-app repository...'
                    sh '''
                        # Configure git to avoid HTTP/2 issues
                        git config --global http.version HTTP/1.1
                        git config --global http.postBuffer 1048576000
                        git config --global core.compression 0
                    '''
                    git branch: "${GIT_BRANCH}", url: "${GIT_URL}"
                }
            }
        }

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

        stage('Sonar Quality Gate Scan') {
            steps {
                timeout(time:10, unit:"MINUTES"){
                    waitForQualityGate abortPipeline: true
                }
            }
        }

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

        stage('Scan and Push images') {
            parallel {
                stage('Trivy Image Scan') {
                    steps {
                        script {
                            // Trivy images scan
                            sh """
                                trivy image --format template --template @trivy-template.html -o trivy-vote-report.html ${IMAGE_VOTE}:${BUILD_NUMBER} || true
                                trivy image --format template --template @trivy-template.html -o trivy-result-report.html ${IMAGE_RESULT}:${BUILD_NUMBER} || true
                                trivy image --format template --template @trivy-template.html -o trivy-worker-report.html ${IMAGE_WORKER}:${BUILD_NUMBER} || true
                            """
                            // Archive HTML reports
                            archiveArtifacts artifacts: 'trivy-*-report.html', fingerprint: true
                        }
                    }
                }

                stage('Docker Push') {
                    steps {
                        script {
                            withDockerRegistry(credentialsId: 'your-docker-credentials') {
                                sh """
                                    docker tag ${IMAGE_VOTE}:${BUILD_NUMBER} ${IMAGE_VOTE}:${BUILD_NUMBER}
                                    docker tag ${IMAGE_RESULT}:${BUILD_NUMBER} ${IMAGE_RESULT}:${BUILD_NUMBER}
                                    docker tag ${IMAGE_WORKER}:${BUILD_NUMBER} ${IMAGE_WORKER}:${BUILD_NUMBER}

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

        stage('Approval Required') {
            steps {
                script {
                    mail(
                        to: "${MAIL_FOR_APPROVAL}",
                        subject: "Approval Required for Deployment",
                        body: "Pipeline is waiting for your approval. Please go to Jenkins and click Deploy to continue."
                    )
                    input message: 'Do you approve deployment to production?', ok: 'Deploy'
                }
            }
        }

        stage('Deploy using Docker compose') {
            steps {
                sh "IMAGE_VOTE_TAG=${BUILD_NUMBER} IMAGE_RESULT_TAG=${BUILD_NUMBER} IMAGE_WORKER_TAG=${BUILD_NUMBER} docker compose -f docker-compose.yml up -d"
            }
        }
    }
   
    post {
        success {
            script {
                echo "✅ Deployment successful!"
                mail(
                    to: "${MAIL_FOR_FAIL_OR_SUCCESSFULL}",
                    subject: "Build #${BUILD_NUMBER} Successful - ${env.JOB_NAME}",
                    body: """ 
Hello Team,

Pipeline has successfully completed!

Build Number: ${BUILD_NUMBER}

Security & Quality Reports:
- SonarQube: ${SONAR_URL}
- Trivy Vote Report: ${env.BUILD_URL}artifact/trivy-vote-report.html
- Trivy Result Report: ${env.BUILD_URL}artifact/trivy-result-report.html
- Trivy Worker Report: ${env.BUILD_URL}artifact/trivy-worker-report.html

Application Links:
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
                    subject: "Build #${BUILD_NUMBER} Failed - ${env.JOB_NAME}",
                    body: """ 
Hello Team,

Pipeline has failed.

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
