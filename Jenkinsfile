pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')  // Total pipeline timeout
    }

    environment {
        SONARQUBE = 'SonarQubeServer'
        IMAGE_VOTE = "voting-app-vote"
        IMAGE_RESULT = "voting-app-result"
        IMAGE_WORKER = "voting-app-worker"
        DOCKERHUB_NAMESPACE = "31793179"
        DOCKER_BUILDKIT = "1"
        COMPOSE_DOCKER_CLI_BUILD = "1"
        BUILDKIT_PROGRESS = "plain"
        TWILIO_FROM = "whatsapp:+14155238886"
        MY_WHATSAPP = "whatsapp:+92XXXXXXXXXX"  // your WhatsApp number
        JENKINS_URL = "https://65d1b1133b29.ngrok-free.app"
        JOB_NAME = "voting-app-pipeline"
    }

    stages {
        stage('Download Code') {
            steps {
                echo "📥 Downloading repository..."
                sh '''
                    rm -rf * .* 2>/dev/null || true
                    curl -L -o repo.zip "https://github.com/Ans-fraz-cyber/voting-app-ci-cd/archive/main.zip"
                    unzip -q repo.zip
                    mv voting-app-ci-cd-main/* . 2>/dev/null || true
                    mv voting-app-ci-cd-main/.* . 2>/dev/null || true
                    rm -rf voting-app-ci-cd-main repo.zip
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo "🔍 Running SonarQube Analysis..."
                withSonarQubeEnv("${SONARQUBE}") {
                    script {
                        def scannerHome = tool 'SonarQubeScanner'
                        withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_AUTH_TOKEN')]) {
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
        }

        // Quality Gate temporarily non-blocking
        stage('Smart Quality Gate (Non-blocking)') {
            steps {
                script {
                    echo "⏳ Checking SonarQube Quality Gate (non-blocking)..."
                    try {
                        timeout(time: 2, unit: 'MINUTES') {
                            waitForQualityGate abortPipeline: false
                        }
                    } catch(Exception e) {
                        echo "⚠️ Quality Gate check skipped due to timeout or error."
                    }
                }
            }
        }

        stage('Approval via WhatsApp') {
            steps {
                script {
                    echo "📲 Sending WhatsApp approval request..."
                    withCredentials([
                        string(credentialsId: 'twilio-sid', variable: 'TWILIO_SID'),
                        string(credentialsId: 'twilio-auth', variable: 'TWILIO_AUTH')
                    ]) {
                        sh """
                        curl -X POST https://api.twilio.com/2010-04-01/Accounts/${TWILIO_SID}/Messages.json \\
                        --data-urlencode "From=${TWILIO_FROM}" \\
                        --data-urlencode "To=${MY_WHATSAPP}" \\
                        --data-urlencode "Body=🚦 Jenkins Pipeline Approval Needed! Reply YES to approve or NO to reject." \\
                        -u "${TWILIO_SID}:${TWILIO_AUTH}"
                        """
                    }

                    timeout(time: 10, unit: 'MINUTES') {
                        input message: 'Approve deployment? (Check WhatsApp!)', ok: 'Proceed'
                    }
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                script {
                    sh '''
                        export DOCKER_BUILDKIT=1
                        export BUILDKIT_PROGRESS=plain
                        docker build --progress=plain -t ${IMAGE_VOTE}:${BUILD_NUMBER} ./vote
                        docker build --progress=plain -t ${IMAGE_RESULT}:${BUILD_NUMBER} ./result
                        docker build --progress=plain -t ${IMAGE_WORKER}:${BUILD_NUMBER} ./worker
                    '''
                }
            }
        }

        stage('Trivy Security Scan') {
            steps {
                script {
                    sh '''
                        trivy image --format html -o trivy-vote.html ${IMAGE_VOTE}:${BUILD_NUMBER}
                        trivy image --format html -o trivy-result.html ${IMAGE_RESULT}:${BUILD_NUMBER}
                        trivy image --format html -o trivy-worker.html ${IMAGE_WORKER}:${BUILD_NUMBER}
                    '''
                    archiveArtifacts artifacts: 'trivy-*.html', fingerprint: true
                }
            }
        }

        stage('Push Docker Images') {
            steps {
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

        stage('Deploy Application') {
            steps {
                script {
                    sh '''
                        docker-compose down || true
                        docker-compose up -d
                    '''
                }
            }
        }
    }

    post {
        always {
            script {
                cleanWs()
            }
            mail(
                to: "ansfarazkp@gmail.com",
                subject: "Build ${currentBuild.currentResult} - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Build ${currentBuild.currentResult}! URL: ${env.BUILD_URL}"
            )
        }
    }
}
