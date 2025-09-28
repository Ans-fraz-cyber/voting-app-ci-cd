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
        DOCKERHUB_NAMESPACE = '31793179'
    }

    stages {
        stage('Code Clone') {
            steps {
                echo "🔄 Cloning private repository..."
                git(
                    url: 'https://github.com/Ans-fraz-cyber/voting-app-ci-cd.git',
                    branch: 'main',
                    credentialsId: 'github-token'
                )
                
                // Clean workspace from previous builds
                cleanWs()
            }
        }

        stage('SonarQube Code Analysis') {
            steps {
                echo "🔍 Running SonarQube Code Analysis..."
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

        stage('Security Gates - Quality Gate Check') {
            steps {
                echo "🛡️ Checking Security Gates - SonarQube Quality Gate..."
                script {
                    // Increased timeout for quality gate
                    timeout(time: 15, unit: 'MINUTES') {
                        waitForQualityGate abortPipeline: true
                    }
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                echo "🐳 Building Docker images..."
                sh '''
                    echo "Building Vote service..."
                    docker build -t voting-app-vote:latest ./vote
                    
                    echo "Building Result service..."
                    docker build -t voting-app-result:latest ./result
                    
                    echo "Building Worker service..."
                    docker build -t voting-app-worker:latest ./worker
                    
                    echo "✅ All images built successfully"
                '''
            }
        }

        stage('Trivy Security Scan') {
            steps {
                echo "🔒 Running Trivy Security Scan..."
                script {
                    // Clean previous reports
                    sh 'rm -rf trivy-reports || true'
                    sh 'mkdir -p trivy-reports'
                    
                    def images = [
                        'vote': 'voting-app-vote:latest',
                        'result': 'voting-app-result:latest', 
                        'worker': 'voting-app-worker:latest'
                    ]
                    
                    images.each { service, image ->
                        echo "📊 Scanning ${service} image..."
                        
                        // Generate HTML Report
                        sh """
                            trivy image \
                                --exit-code 0 \
                                --severity HIGH,CRITICAL \
                                --format html \
                                --output trivy-reports/${service}-report.html \
                                ${image}
                        """
                        
                        // Console output for logs
                        sh """
                            echo "=== ${service.toUpperCase()} SECURITY SCAN RESULTS ==="
                            trivy image --exit-code 0 --severity HIGH,CRITICAL ${image}
                        """
                    }
                    
                    // Create consolidated report index
                    sh '''
                        echo "<html><head><title>Trivy Security Reports</title></head>" > trivy-reports/index.html
                        echo "<body><h1>🔒 Trivy Security Scan Reports</h1>" >> trivy-reports/index.html
                        echo "<ul>" >> trivy-reports/index.html
                        echo "<li><a href='vote-report.html'>Vote Service Report</a></li>" >> trivy-reports/index.html
                        echo "<li><a href='result-report.html'>Result Service Report</a></li>" >> trivy-reports/index.html
                        echo "<li><a href='worker-report.html'>Worker Service Report</a></li>" >> trivy-reports/index.html
                        echo "</ul><p>Generated on: $(date)</p></body></html>" >> trivy-reports/index.html
                        
                        echo "📁 Generated Reports:"
                        ls -la trivy-reports/
                    '''
                }
            }
            
            post {
                always {
                    // Archive all reports
                    archiveArtifacts artifacts: 'trivy-reports/**', fingerprint: true
                    
                    // Publish main index
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'trivy-reports',
                        reportFiles: 'index.html',
                        reportName: '🔒 Trivy Security Reports'
                    ])
                }
            }
        }

        stage('Push to DockerHub') {
            steps {
                script {
                    echo "📤 Pushing images to DockerHub..."
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-credentials') {
                        def images = ['vote', 'result', 'worker']
                        
                        images.each { service ->
                            sh """
                                # Tag with build number
                                docker tag voting-app-${service}:latest ${env.DOCKERHUB_NAMESPACE}/voting-app-${service}:${env.BUILD_NUMBER}
                                
                                # Tag as latest
                                docker tag voting-app-${service}:latest ${env.DOCKERHUB_NAMESPACE}/voting-app-${service}:latest
                                
                                # Push both tags
                                docker push ${env.DOCKERHUB_NAMESPACE}/voting-app-${service}:${env.BUILD_NUMBER}
                                docker push ${env.DOCKERHUB_NAMESPACE}/voting-app-${service}:latest
                                
                                echo "✅ ${service} image pushed successfully"
                            """
                        }
                    }
                }
            }
        }

        stage('Deploy Application') {
            steps {
                echo "🚀 Deploying voting application..."
                sh '''
                    # Stop and remove existing containers
                    docker-compose down || true
                    
                    # Deploy fresh stack
                    docker-compose up -d --force-recreate
                    
                    # Health check
                    sleep 30
                    echo "📊 Deployment Status:"
                    docker-compose ps
                    
                    echo "🌐 Application URLs:"
                    echo "Vote: http://localhost:5000"
                    echo "Result: http://localhost:5001"
                '''
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning up workspace..."
            cleanWs()
            
            // Simple email notification without emailext (to avoid connection issues)
            mail(
                to: "ansfarazkp@gmail.com",
                subject: "Build ${currentBuild.currentResult} - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                Pipeline Execution Complete!
                
                Project: ${env.JOB_NAME}
                Build: #${env.BUILD_NUMBER}
                Status: ${currentBuild.currentResult}
                
                Build URL: ${env.BUILD_URL}
                
                Security Reports: ${env.BUILD_URL}trivy-reports/
                """
            )
        }
        
        success {
            echo "🎉 Pipeline executed successfully!"
        }
        
        failure {
            echo "❌ Pipeline failed - check logs for details"
        }
    }
}
