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
        MY_EMAIL = "ansfaraz.cyber@gmail.com"
        APPROVAL_FILE = "/tmp/build_${BUILD_NUMBER}_approved"
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

        stage('Send Email for Approval') {
            steps {
                script {
                    echo "📧 Sending approval email..."
                    
                    // Clean previous approval file
                    sh "rm -f ${APPROVAL_FILE} || true"
                    
                    // Send email with approval instructions
                    mail(
                        to: "${MY_EMAIL}",
                        subject: "APPROVAL REQUIRED: Build ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                        body: """
                        BUILD APPROVAL NEEDED!
                        
                        Project: ${env.JOB_NAME}
                        Build Number: #${env.BUILD_NUMBER}
                        Build URL: ${env.BUILD_URL}
                        
                        ✅ TO APPROVE this build:
                        Run this command on your server:
                        
                        echo "APPROVED" > ${APPROVAL_FILE}
                        
                        ❌ TO REJECT this build:
                        Run this command on your server:
                        
                        echo "REJECTED" > ${APPROVAL_FILE}
                        
                        OR visit: http://localhost:5000/approve?build=${env.BUILD_NUMBER}
                        
                        ⏰ This build will wait for 30 minutes for approval.
                        """
                    )
                    
                    echo "✅ Approval email sent to: ${MY_EMAIL}"
                    echo "📋 Check your email for approval instructions"
                }
            }
        }

        stage('Wait for Manual Approval') {
            steps {
                script {
                    echo "⏳ Waiting for manual approval..."
                    echo "📧 Check your email: ${MY_EMAIL}"
                    echo "💡 Follow the instructions in the email to approve"
                    
                    // Wait for approval file to be created manually
                    timeout(time: 30, unit: 'MINUTES') {
                        waitUntil {
                            sleep 10  // Check every 10 seconds
                            
                            if (fileExists(APPROVAL_FILE)) {
                                def status = sh(script: "cat ${APPROVAL_FILE}", returnStdout: true).trim()
                                if (status == "APPROVED") {
                                    echo "🎉 Build approved! Continuing pipeline..."
                                    return true
                                } else if (status == "REJECTED") {
                                    error "❌ Build rejected!"
                                }
                            }
                            
                            echo "⏰ Still waiting for approval... Check your email for instructions"
                            return false
                        }
                    }
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                script {
                    echo "🏗️ Building Docker images..."
                    sh '''
                        docker build --progress=plain -t ${IMAGE_VOTE}:${BUILD_NUMBER} ./vote
                        docker build --progress=plain -t ${IMAGE_RESULT}:${BUILD_NUMBER} ./result
                        docker build --progress=plain -t ${IMAGE_WORKER}:${BUILD_NUMBER} ./worker
                        echo "✅ All images built successfully!"
                    '''
                }
            }
        }

        stage('Trivy Security Scan') {
            steps {
                script {
                    echo "🔒 Running Trivy Security Scan..."
                    sh '''
                        trivy image --format table -o trivy-vote.txt ${IMAGE_VOTE}:${BUILD_NUMBER} || true
                        trivy image --format table -o trivy-result.txt ${IMAGE_RESULT}:${BUILD_NUMBER} || true
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
                            echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin
                            
                            docker tag ${IMAGE_VOTE}:${BUILD_NUMBER} ${DOCKERHUB_NAMESPACE}/voting-app-vote:${BUILD_NUMBER}
                            docker tag ${IMAGE_RESULT}:${BUILD_NUMBER} ${DOCKERHUB_NAMESPACE}/voting-app-result:${BUILD_NUMBER}
                            docker tag ${IMAGE_WORKER}:${BUILD_NUMBER} ${DOCKERHUB_NAMESPACE}/voting-app-worker:${BUILD_NUMBER}

                            docker push ${DOCKERHUB_NAMESPACE}/voting-app-vote:${BUILD_NUMBER}
                            docker push ${DOCKERHUB_NAMESPACE}/voting-app-result:${BUILD_NUMBER}
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
                        docker-compose down || true
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
            // Clean up approval file
            sh "rm -f ${APPROVAL_FILE} || true"
            cleanWs()
            
            echo "📧 Sending build result email..."
            mail(
                to: "${MY_EMAIL}",
                subject: "Build ${currentBuild.currentResult} - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Build ${currentBuild.currentResult}! URL: ${env.BUILD_URL}"
            )
        }
    }
}
