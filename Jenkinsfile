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
                    
                    // Clean previous approval signal
                    sh "rm -f /tmp/jenkins_approved || true"
                    
                    // Send WhatsApp message
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
                    echo "📱 The build will continue IMMEDIATELY when you reply 'YES'"
                    
                    // Wait for approval signal (check every 5 seconds)
                    def approved = false
                    for(int i = 0; i < 120; i++) { // Wait max 10 minutes
                        sleep(5)
                        approved = fileExists('/tmp/jenkins_approved')
                        if(approved) {
                            echo "✅ Approval received via WhatsApp! Continuing build..."
                            break
                        }
                        if(i % 12 == 0) {
                            def secondsPassed = (i + 1) * 5
                            echo "⏰ Still waiting for WhatsApp approval... (${secondsPassed} seconds passed)"
                        }
                    }
                    
                    if(!approved) {
                        error("❌ No approval received within 10 minutes")
                    }
                }
            }
        }

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
                    // FIXED: Use correct Trivy format options
                    sh '''
                        trivy image --format table -o trivy-vote.txt ${IMAGE_VOTE}:${BUILD_NUMBER}
                        trivy image --format table -o trivy-result.txt ${IMAGE_RESULT}:${BUILD_NUMBER}
                        trivy image --format table -o trivy-worker.txt ${IMAGE_WORKER}:${BUILD_NUMBER}
                        
                        # Generate JSON reports for artifacts
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
                // Safe cleanup - won't fail if file doesn't exist
                sh "rm -f /tmp/jenkins_approved || true"
            }
            mail(
                to: "ansfarazkp@gmail.com",
                subject: "Build ${currentBuild.currentResult} - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Build ${currentBuild.currentResult}! URL: ${env.BUILD_URL}"
            )
        }
    }
}
