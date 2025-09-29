pipeline {
    agent any

    parameters {
        booleanParam(name: 'APPROVED', defaultValue: false, description: 'Approved via WhatsApp')
    }

    options {
        skipDefaultCheckout(true)
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
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
        MY_WHATSAPP = "whatsapp:+923066818972"
        WEBHOOK_URL = "https://65d1b1133b29.ngrok-free.app"
    }

    stages {
        stage('Download Code') {
            when {
                expression { params.APPROVED == false }
            }
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
            when {
                expression { params.APPROVED == false }
            }
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

        stage('Send WhatsApp Approval Request') {
            when {
                expression { params.APPROVED == false }
            }
            steps {
                script {
                    echo "📲 Sending WhatsApp approval request..."
                    
                    withCredentials([
                        string(credentialsId: 'twilio-sid', variable: 'TWILIO_SID'),
                        string(credentialsId: 'twilio-auth', variable: 'TWILIO_AUTH')
                    ]) {
                        sh """
                        curl -X POST "https://api.twilio.com/2010-04-01/Accounts/${TWILIO_SID}/Messages.json" \\
                        --data-urlencode "From=${TWILIO_FROM}" \\
                        --data-urlencode "To=${MY_WHATSAPP}" \\
                        --data-urlencode "Body=🚦 BUILD Approval Needed! SonarQube completed. Reply YES to start building IMMEDIATELY. Build: ${env.JOB_NAME} #${env.BUILD_NUMBER}" \\
                        -u "${TWILIO_SID}:${TWILIO_AUTH}"
                        """
                    }
                    
                    echo "✅ WhatsApp message sent!"
                    echo "⏳ Waiting for your 'YES' reply..."
                    echo "📱 The build will start IMMEDIATELY when you reply 'YES'"
                    
                    // Wait for approval (this build will stop here, new build will start)
                    sleep time: 300, unit: 'SECONDS'
                    error("❌ No approval received within 5 minutes")
                }
            }
        }

        stage('Build Docker Images') {
            when {
                expression { params.APPROVED == true }
            }
            steps {
                script {
                    echo "🏗️ Building Docker images (Approved via WhatsApp)..."
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
            when {
                expression { params.APPROVED == true }
            }
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
            when {
                expression { params.APPROVED == true }
            }
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
            when {
                expression { params.APPROVED == true }
            }
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
            script { cleanWs() }
            mail(
                to: "ansfarazkp@gmail.com",
                subject: "Build ${currentBuild.currentResult} - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Build ${currentBuild.currentResult}! URL: ${env.BUILD_URL}"
            )
        }
    }
}
