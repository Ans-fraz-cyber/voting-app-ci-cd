pipeline {
    agent any

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

        stage('Wait for WhatsApp Approval') {
            steps {
                script {
                    echo "📲 Sending WhatsApp approval request..."
                    
                    // Clean previous approval files
                    sh '''
                        rm -f approved.txt || true
                        rm -f /tmp/jenkins_approved || true
                        echo "✅ Cleaned previous approval files"
                    '''
                    
                    // Send WhatsApp message
                    withCredentials([
                        string(credentialsId: 'twilio-sid', variable: 'TWILIO_SID'),
                        string(credentialsId: 'twilio-auth', variable: 'TWILIO_AUTH')
                    ]) {
                        sh """
                        curl -X POST "https://api.twilio.com/2010-04-01/Accounts/${TWILIO_SID}/Messages.json" \\
                        --data-urlencode "From=${TWILIO_FROM}" \\
                        --data-urlencode "To=${MY_WHATSAPP}" \\
                        --data-urlencode "Body=🚦 BUILD Approval Needed! SonarQube completed. Reply YES to start building. Build: ${env.JOB_NAME} #${env.BUILD_NUMBER}" \\
                        -u "${TWILIO_SID}:${TWILIO_AUTH}"
                        """
                    }
                    
                    echo "✅ WhatsApp message sent!"
                    echo "⏳ Waiting for your 'YES' reply on WhatsApp..."
                    echo "📱 The build will ONLY continue when you reply 'YES'"
                    
                    // Wait for approval - check every 5 seconds
                    def approved = false
                    def waitCount = 0
                    def maxWait = 120 // 10 minutes (120 * 5 seconds)
                    
                    while (waitCount < maxWait && !approved) {
                        sleep(5000) // Wait 5 seconds
                        waitCount++
                        
                        // Check multiple possible file locations
                        approved = fileExists('approved.txt') || fileExists('/tmp/jenkins_approved')
                        
                        if (approved) {
                            echo "🎉 ✅ Approval received via WhatsApp! Continuing build..."
                            sh "cat approved.txt || true" // Debug: show file content
                            break
                        }
                        
                        // Log every 30 seconds
                        if (waitCount % 6 == 0) {
                            def minutes = (waitCount * 5) / 60
                            echo "⏰ Still waiting for WhatsApp approval... (${waitCount * 5} seconds elapsed)"
                        }
                    }
                    
                    if (!approved) {
                        error("❌ No approval received within 10 minutes. Pipeline stopped.")
                    }
                }
            }
        }

        // REST OF YOUR STAGES REMAIN THE SAME
        stage('Build Docker Images') {
            steps {
                script {
                    echo "🏗️ Building Docker images..."
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
                    echo "🔒 Running Trivy Security Scan..."
                    sh '''
                        trivy image --format table -o trivy-vote.txt ${IMAGE_VOTE}:${BUILD_NUMBER}
                        trivy image --format table -o trivy-result.txt ${IMAGE_RESULT}:${BUILD_NUMBER}
                        trivy image --format table -o trivy-worker.txt ${IMAGE_WORKER}:${BUILD_NUMBER}
                        
                        trivy image --format json -o trivy-vote.json ${IMAGE_VOTE}:${BUILD_NUMBER}
                        trivy image --format json -o trivy-result.json ${IMAGE_RESULT}:${BUILD_NUMBER}
                        trivy image --format json -o trivy-worker.json ${IMAGE_WORKER}:${BUILD_NUMBER}
                    '''
                    archiveArtifacts artifacts: 'trivy-*.txt,trivy-*.json', fingerprint: true
                }
            }
        }

        stage('Push Docker Images') {
            steps {
                script {
                    echo "📤 Pushing Docker images to DockerHub..."
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
                    echo "🚀 Deploying Application..."
                    sh '''
                        docker-compose down || true
                        IMAGE_VOTE=${DOCKERHUB_NAMESPACE}/voting-app-vote:${BUILD_NUMBER} \
                        IMAGE_RESULT=${DOCKERHUB_NAMESPACE}/voting-app-result:${BUILD_NUMBER} \
                        IMAGE_WORKER=${DOCKERHUB_NAMESPACE}/voting-app-worker:${BUILD_NUMBER} \
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
                sh "rm -f approved.txt || true"
            }
            mail(
                to: "ansfarazkp@gmail.com",
                subject: "Build ${currentBuild.currentResult} - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Build ${currentBuild.currentResult}! URL: ${env.BUILD_URL}"
            )
        }
    }
}
