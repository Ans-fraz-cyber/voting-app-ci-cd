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

        stage('SonarQube Quality Gate') {
            steps {
                echo "✅ Checking SonarQube Quality Gate..."
                script {
                    // Smart timeout - wait max 5 minutes for quality gate
                    timeout(time: 5, unit: 'MINUTES') {
                        try {
                            waitForQualityGate abortPipeline: true
                            echo "✅ Quality Gate: PASSED"
                        } catch (Exception e) {
                            echo "❌ Quality Gate: FAILED or TIMEOUT"
                            error "SonarQube Quality Gate failed or timed out"
                        }
                    }
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                echo "🐳 Building Docker images..."
                script {
                    def services = ['vote', 'result', 'worker']
                    
                    services.each { service ->
                        echo "Building ${service} service..."
                        try {
                            sh "docker build -t voting-app-${service}:latest ./${service}"
                            echo "✅ ${service} built successfully"
                        } catch (Exception e) {
                            echo "❌ Failed to build ${service}: ${e.getMessage()}"
                            error "Docker build failed for ${service}"
                        }
                    }
                }
            }
        }

        stage('Container Security Scan - Trivy') {
            steps {
                echo "🔒 Running Container Security Scan - Trivy..."
                script {
                    sh 'rm -rf security-reports || true'
                    sh 'mkdir -p security-reports'
                    
                    def images = [
                        'vote': 'voting-app-vote:latest',
                        'result': 'voting-app-result:latest', 
                        'worker': 'voting-app-worker:latest'
                    ]
                    
                    images.each { service, image ->
                        echo "📊 Security Scanning: ${service}"
                        
                        // Generate HTML Report
                        sh """
                            trivy image \
                                --exit-code 0 \
                                --severity HIGH,CRITICAL \
                                --format html \
                                --output security-reports/${service}-security-report.html \
                                ${image}
                        """
                        
                        // Console output
                        sh """
                            echo "=== ${service.toUpperCase()} SECURITY SCAN ==="
                            trivy image --exit-code 0 --severity HIGH,CRITICAL ${image} | head -10
                        """
                    }
                    
                    // Create security dashboard
                    sh '''
                        echo "<html><head><title>Security Gates Report</title></head>" > security-reports/security-dashboard.html
                        echo "<body><h1>🛡️ Security Gates Dashboard</h1>" >> security-reports/security-dashboard.html
                        echo "<h2>✅ All Security Scans Completed</h2>" >> security-reports/security-dashboard.html
                        echo "<h3>📊 Security Reports:</h3>" >> security-reports/security-dashboard.html
                        echo "<ul>" >> security-reports/security-dashboard.html
                        echo "<li><a href='vote-security-report.html'>Vote Service Security Report</a></li>" >> security-reports/security-dashboard.html
                        echo "<li><a href='result-security-report.html'>Result Service Security Report</a></li>" >> security-reports/security-dashboard.html
                        echo "<li><a href='worker-security-report.html'>Worker Service Security Report</a></li>" >> security-reports/security-dashboard.html
                        echo "</ul>" >> security-reports/security-dashboard.html
                        echo "<p><strong>SonarQube Quality Gate:</strong> ✅ PASSED</p>" >> security-reports/security-dashboard.html
                        echo "<p><strong>SonarQube Analysis:</strong> <a href='http://localhost:9000/dashboard?id=voting-app'>View Detailed Report</a></p>" >> security-reports/security-dashboard.html
                        echo "<p><em>Generated on: $(date)</em></p></body></html>" >> security-reports/security-dashboard.html
                    '''
                }
            }
            
            post {
                always {
                    archiveArtifacts artifacts: 'security-reports/**', fingerprint: true
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'security-reports',
                        reportFiles: 'security-dashboard.html',
                        reportName: '🛡️ Security Gates Dashboard'
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
                                docker tag voting-app-${service}:latest ${env.DOCKERHUB_NAMESPACE}/voting-app-${service}:${env.BUILD_NUMBER}
                                docker tag voting-app-${service}:latest ${env.DOCKERHUB_NAMESPACE}/voting-app-${service}:latest
                                
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
                    docker-compose down || true
                    docker-compose up -d --force-recreate
                    sleep 20
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
            
            mail(
                to: "ansfarazkp@gmail.com",
                subject: "Build ${currentBuild.currentResult} - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                Pipeline Execution Complete!
                
                Project: ${env.JOB_NAME}
                Build: #${env.BUILD_NUMBER}
                Status: ${currentBuild.currentResult}
                
                Build URL: ${env.BUILD_URL}
                Security Dashboard: ${env.BUILD_URL}security-gates-dashboard/
                SonarQube: http://localhost:9000/dashboard?id=voting-app
                
                View security reports in Jenkins for detailed analysis.
                """
            )
        }
        
        success {
            echo "🎉 Pipeline executed successfully!"
            echo "✅ SonarQube Quality Gate: PASSED"
            echo "🛡️ Container Security Scans: COMPLETED"
        }
    }
}
