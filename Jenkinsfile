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
        // BuildKit
        DOCKER_BUILDKIT = "1"
        COMPOSE_DOCKER_CLI_BUILD = "1"
        BUILDKIT_PROGRESS = "plain"
        TWILIO_SID = credentials('twilio-sid')
        TWILIO_AUTH = credentials('twilio-auth')
        TWILIO_FROM = "whatsapp:+14155238886"   // Twilio Sandbox number
        MY_WHATSAPP = "whatsapp:+92XXXXXXXXXX"  // Replace with your WhatsApp number
        JENKINS_USER = "Ans Faraz"
        JENKINS_TOKEN = "111fc77cf1e14c6109c62442667f178d64"
        JENKINS_URL = "https://0640f2ef4501.ngrok-free.app"   // ngrok URL for Jenkins
        JOB_NAME = "voting-app-pipeline"
    }

    stages {
        stage('Download Code') {
            steps {
                echo "📥 Downloading repository as ZIP..."
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

        stage('Smart Quality Gate') {
            steps {
                script {
                    try {
                        timeout(time: 2, unit: 'MINUTES') {
                            waitForQualityGate abortPipeline: false
                        }
                    } catch (Exception e) {
                        echo "⚠️ Quality Gate still processing..."
                    }
                }
            }
        }

        // 🔔 WhatsApp Approval Stage
        stage('Approval') {
            steps {
                script {
                    // 1️⃣ Send WhatsApp message via Twilio
                    echo "📲 Sending WhatsApp approval request..."
                    sh """
                        curl -X POST https://api.twilio.com/2010-04-01/Accounts/${TWILIO_SID}/Messages.json \\
                        --data-urlencode "From=${TWILIO_FROM}" \\
                        --data-urlencode "To=${MY_WHATSAPP}" \\
                        --data-urlencode "Body=🚦 Jenkins Pipeline Approval Needed! Reply YES to approve or NO to reject." \\
                        -u "${TWILIO_SID}:${TWILIO_AUTH}"
                    """

                    // 2️⃣ Pause pipeline until Flask webhook triggers input
                    timeout(time: 10, unit: 'MINUTES') {
                        input message: 'Approve deployment? (Check WhatsApp!)', ok: 'Proceed'
                    }
                }
            }
        }

        stage('Build Docker Images with BuildKit') {
            steps {
                echo "🐳 Building Docker images..."
                sh '''
                    export DOCKER_BUILDKIT=1
                    export BUILDKIT_PROGRESS=plain

                    docker build --progress=plain -t ${IMAGE_VOTE}:${BUILD_NUMBER} ./vote
                    docker build --progress=plain -t ${IMAGE_RESULT}:${BUILD_NUMBER} ./result
                    docker build --progress=plain -t ${IMAGE_WORKER}:${BUILD_NUMBER} ./worker
                '''
            }
        }

        stage('Security Scan and Push') {
            parallel {
                stage('Trivy Security Scan') {
                    steps {
                        echo "🔒 Running Trivy scans..."
                        sh '''
                            trivy image --format html -o trivy-vote.html ${IMAGE_VOTE}:${BUILD_NUMBER}
                            trivy image --format html -o trivy-result.html ${IMAGE_RESULT}:${BUILD_NUMBER}
                            trivy image --format html -o trivy-worker.html ${IMAGE_WORKER}:${BUILD_NUMBER}
                        '''
                        archiveArtifacts artifacts: 'trivy-*.html', fingerprint: true
                    }
                }

                stage('Push to DockerHub') {
                    steps {
                        echo "📤 Pushing images..."
                        docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-credentials') {
                            sh '''
                                docker tag ${IMAGE_VOTE}:${BUILD_NUMBER} ${DOCKERHUB_NAMESPACE}/voting-app-vote:${BUILD_NUMBER}
                                docker tag ${IMAGE_RESULT}:${BUILD_NUMBER} ${DOCKERHUB_NAMESPACE}/voting-app-result:${BUILD_NUMBER}
                                docker tag ${IMAGE_WORKER}:${BUILD_NUMBER} ${DOCKERHUB_NAMESPACE}/voting-app-worker:${BUILD_NUMBER}

                                docker push ${DOCKERHUB_NAMESPACE}/voting-app-vote:${BUILD_NUMBER}
                                docker push ${DOCKERHUB_NAMESPACE}/voting-app-result:${BUILD_NUMBER}
                                docker push ${DOCKERHUB_NAMESPACE}/voting-app-worker:${BUILD_NUMBER}
                            '''
                        }
                    }
                }
            }
        }

        stage('Deploy Application') {
            steps {
                echo "🚀 Deploying application..."
                sh '''
                    docker-compose down || true
                    docker-compose up -d
                '''
            }
        }
    }

    post {
        always {
            cleanWs()
            mail(
                to: "ansfarazkp@gmail.com",
                subject: "Build ${currentBuild.currentResult} - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Build ${currentBuild.currentResult}! URL: ${env.BUILD_URL}"
            )
        }
    }
}
