pipeline {
    agent any
    
    environment {
        PROJECT_NAME = 'voting-app'
    }
    
    parameters {
        choice(
            name: 'DEPLOY_ENV',
            choices: ['dev', 'staging'],
            description: 'Select deployment environment'
        )
        booleanParam(
            name: 'RUN_TESTS',
            defaultValue: true,
            description: 'Run integration tests'
        )
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
                sh '''
                    echo "=== Voting App Project Structure ==="
                    ls -la
                    echo "=== Docker Compose File ==="
                    cat docker-compose.yml
                '''
            }
        }
        
        stage('Build Services') {
            parallel {
                stage('Build Vote Service') {
                    steps {
                        dir('vote') {
                            sh 'docker build -t voting-app-vote:${BUILD_NUMBER} .'
                        }
                    }
                }
                stage('Build Result Service') {
                    steps {
                        dir('result') {
                            sh 'docker build -t voting-app-result:${BUILD_NUMBER} .'
                        }
                    }
                }
                stage('Build Worker Service') {
                    steps {
                        dir('worker') {
                            sh 'docker build -t voting-app-worker:${BUILD_NUMBER} .'
                        }
                    }
                }
            }
        }
        
        stage('Test Services') {
            when {
                expression { params.RUN_TESTS == true }
            }
            steps {
                script {
                    echo "Testing built images..."
                    
                    // Test vote service
                    sh 'docker run --rm -d --name test-vote -p 5000:80 voting-app-vote:${BUILD_NUMBER} || true'
                    sh 'sleep 10 && docker logs test-vote || true'
                    sh 'docker stop test-vote || true'
                    
                    // Test result service  
                    sh 'docker run --rm -d --name test-result -p 5001:80 voting-app-result:${BUILD_NUMBER} || true'
                    sh 'sleep 10 && docker logs test-result || true'
                    sh 'docker stop test-result || true'
                    
                    // Run integration tests if available
                    sh 'if [ -f "test-integration.sh" ]; then chmod +x test-integration.sh && ./test-integration.sh; fi'
                }
            }
        }
        
        stage('Deploy Application') {
            steps {
                script {
                    echo "Deploying Voting App to ${params.DEPLOY_ENV} environment"
                    
                    // Stop existing deployment
                    sh 'docker-compose down || true'
                    
                    // Tag new images as latest for docker-compose
                    sh '''
                        docker tag voting-app-vote:${BUILD_NUMBER} voting-app-vote:latest
                        docker tag voting-app-result:${BUILD_NUMBER} voting-app-result:latest  
                        docker tag voting-app-worker:${BUILD_NUMBER} voting-app-worker:latest
                    '''
                    
                    // Deploy using docker-compose
                    sh 'docker-compose up -d'
                    
                    // Wait for services to start
                    sh 'sleep 30'
                    
                    // Check running containers
                    sh 'docker ps'
                    sh 'docker-compose ps'
                    
                    // Test if services are responding
                    sh 'curl -f http://localhost:5000 || echo "Vote service check failed"'
                    sh 'curl -f http://localhost:5001 || echo "Result service check failed"'
                }
            }
        }
    }
    
    post {
        always {
            echo "=== Pipeline completed ==="
            sh 'docker images | grep voting-app || true'
            sh 'docker ps -a | grep voting-app || true'
        }
        success {
            echo "✅ Voting App deployed successfully!"
            sh '''
                echo "Vote app: http://localhost:5000"
                echo "Result app: http://localhost:5001"
            '''
        }
        failure {
            echo "❌ Pipeline failed!"
        }
        cleanup {
            // Clean up test containers
            sh 'docker stop test-vote test-result || true'
            sh 'docker rm test-vote test-result || true'
        }
    }
}
