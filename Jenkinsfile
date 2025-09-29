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
                    ls -la
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
                    
                    // Send WhatsApp message via Twilio
                    withCredentials([
                        string(credentialsId: 'twilio-sid', variable: 'TWILIO_SID'),
                        string(credentialsId: 'twilio-auth', variable: 'TWILIO_AUTH')
                    ]) {
                        sh """
                            curl -X POST "https://api.twilio.com/2010-04-01/Accounts/${TWILIO_SID}/Messages.json" \\
                            --data-urlencode "From=${TWILIO_FROM}" \\
                            --data-urlencode "To=${MY_WHATSAPP}" \\
                            --data-urlencode "Body=🚦 BUILD Approval Needed! SonarQube completed. Reply YES to continue automatically. Build: ${env.JOB_NAME} #${env.BUILD_NUMBER}" \\
                            -u "${TWILIO_SID}:${TWILIO_AUTH}"
                        """
                    }
                    
                    echo "✅ WhatsApp message sent!"
                    echo "⏳ Waiting for WhatsApp approval..."
                    echo "💡 Reply 'YES' on WhatsApp to continue automatically"
                    
                    // Input step that can be triggered via webhook
                    def approval = input(
                        id: 'WhatsAppApproval',
                        message: '📱 Waiting for WhatsApp approval. Reply YES on WhatsApp to continue automatically.', 
                        submitterParameter: 'approver',
                        parameters: [
                            booleanParam(
                                name: 'APPROVE',
                                defaultValue: false,
                                description: 'Automatically set to true when you reply YES on WhatsApp'
                            )
                        ]
                    )
                    
                    if (approval) {
                        echo "🎉 WhatsApp approval received from ${approval}!"
                        echo "🚀 Continuing pipeline automatically..."
                    }
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                script {
                    echo "🏗️ Building Docker images..."
                    sh '''
                        echo "Building Vote image..."
                        docker build --progress=plain -t ${IMAGE_VOTE}:${BUILD_NUMBER} ./vote
                        
                        echo "Building Result image..."
                        docker build --progress=plain -t ${IMAGE_RESULT}:${BUILD_NUMBER} ./result
                        
                        echo "Building Worker image..."
                        docker build --progress=plain -t ${IMAGE_WORKER}:${BUILD_NUMBER} ./worker
                        
                        echo "✅ All images built successfully!"
                        docker images | grep voting-app
                    '''
                }
            }
        }

        stage('Trivy Security Scan') {
            steps {
                script {
                    echo "🔒 Running Trivy Security Scan..."
                    sh '''
                        echo "Scanning Vote image..."
                        trivy image --format table -o trivy-vote.txt ${IMAGE_VOTE}:${BUILD_NUMBER} || true
                        
                        echo "Scanning Result image..."
                        trivy image --format table -o trivy-result.txt ${IMAGE_RESULT}:${BUILD_NUMBER} || true
                        
                        echo "Scanning Worker image..."
                        trivy image --format table -o trivy-worker.txt ${IMAGE_WORKER}:${BUILD_NUMBER} || true
                        
                        echo "✅ Security scans completed!"
                    '''
                    archiveArtifacts artifacts: 'trivy-*.txt', fingerprint: true
                }
            }
        }

        stage('Push Docker Images') {
            steps {
                script {
                    echo "📤 Pushing Docker images to DockerHub..."
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh '''
                            echo "Logging into DockerHub..."
                            echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin
                            
                            echo "Tagging and pushing Vote image..."
                            docker tag ${IMAGE_VOTE}:${BUILD_NUMBER} ${DOCKERHUB_NAMESPACE}/voting-app-vote:${BUILD_NUMBER}
                            docker push ${DOCKERHUB_NAMESPACE}/voting-app-vote:${BUILD_NUMBER}
                            
                            echo "Tagging and pushing Result image..."
                            docker tag ${IMAGE_RESULT}:${BUILD_NUMBER} ${DOCKERHUB_NAMESPACE}/voting-app-result:${BUILD_NUMBER}
                            docker push ${DOCKERHUB_NAMESPACE}/voting-app-result:${BUILD_NUMBER}
                            
                            echo "Tagging and pushing Worker image..."
                            docker tag ${IMAGE_WORKER}:${BUILD_NUMBER} ${DOCKERHUB_NAMESPACE}/voting-app-worker:${BUILD_NUMBER}
                            docker push ${DOCKERHUB_NAMESPACE}/voting-app-worker:${BUILD_NUMBER}
                            
                            echo "✅ All images pushed to DockerHub!"
                        '''
                    }
                }
            }
        }

        stage('Deploy Application') {
            steps {
                script {
                    echo "🚀 Deploying Application..."
                    sh '''
                        echo "Stopping existing containers..."
                        docker-compose down || true
                        
                        echo "Starting new deployment..."
                        IMAGE_VOTE=${DOCKERHUB_NAMESPACE}/voting-app-vote:${BUILD_NUMBER} \
                        IMAGE_RESULT=${DOCKERHUB_NAMESPACE}/voting-app-result:${BUILD_NUMBER} \
                        IMAGE_WORKER=${DOCKERHUB_NAMESPACE}/voting-app-worker:${BUILD_NUMBER} \
                        docker-compose up -d
                        
                        echo "✅ Application deployed successfully!"
                        docker ps | grep voting
                    '''
                }
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning workspace..."
            cleanWs()
            
            echo "📧 Sending build notification..."
            mail(
                to: "ansfarazkp@gmail.com",
                subject: "Build ${currentBuild.currentResult} - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                Build ${currentBuild.currentResult}!
                
                Job: ${env.JOB_NAME}
                Build: #${env.BUILD_NUMBER}
                URL: ${env.BUILD_URL}
                Status: ${currentBuild.currentResult}
                
                -- Jenkins CI/CD
                """
            )
            
            echo "✅ Pipeline completed!"
        }
        
        success {
            echo "🎉 BUILD SUCCESSFUL!"
            script {
                // Send success WhatsApp notification
                withCredentials([
                    string(credentialsId: 'twilio-sid', variable: 'TWILIO_SID'),
                    string(credentialsId: 'twilio-auth', variable: 'TWILIO_AUTH')
                ]) {
                    sh """
                        curl -X POST "https://api.twilio.com/2010-04-01/Accounts/${TWILIO_SID}/Messages.json" \\
                        --data-urlencode "From=${TWILIO_FROM}" \\
                        --data-urlencode "To=${MY_WHATSAPP}" \\
                        --data-urlencode "Body=✅ BUILD SUCCESS! Voting App deployed successfully. Build: ${env.JOB_NAME} #${env.BUILD_NUMBER}" \\
                        -u "${TWILIO_SID}:${TWILIO_AUTH}" || true
                    """
                }
            }
        }
        
        failure {
            echo "❌ BUILD FAILED!"
            script {
                // Send failure WhatsApp notification
                withCredentials([
                    string(credentialsId: 'twilio-sid', variable: 'TWILIO_SID'),
                    string(credentialsId: 'twilio-auth', variable: 'TWILIO_AUTH')
                ]) {
                    sh """
                        curl -X POST "https://api.twilio.com/2010-04-01/Accounts/${TWILIO_SID}/Messages.json" \\
                        --data-urlencode "From=${TWILIO_FROM}" \\
                        --data-urlencode "To=${MY_WHATSAPP}" \\
                        --data-urlencode "Body=❌ BUILD FAILED! Check Jenkins: ${env.BUILD_URL}" \\
                        -u "${TWILIO_SID}:${TWILIO_AUTH}" || true
                    """
                }
            }
        }
    }
}
