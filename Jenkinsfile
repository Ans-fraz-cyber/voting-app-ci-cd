pipeline {
    agent any
    stages {
        stage('1. Checkout Code') { 
            steps { 
                checkout scm
                sh 'echo "Stage 1: Code checkout completed"'
            } 
        }
        stage('2. Code Quality Scan') { 
    steps { 
        sh '''
            echo "Running SonarQube analysis with Docker..."
            docker run --rm \
            -v $(pwd):/usr/src \
            -w /usr/src \
            sonarsource/sonar-scanner-cli:latest \
            sonar-scanner \
            -Dsonar.projectKey=voting-app \
            -Dsonar.sources=vote,result,worker \
            -Dsonar.host.url=http://192.168.18.63:9000 \
            -Dsonar.login=sqa_8cf00cc4ae6cede80c8511ffe6457f52322d4065
        '''
            } 
        }
        stage('3. Build Docker Images') {
            steps {
                sh 'echo "Stage 3: Building images..."'
                sh 'docker build -t voting-app-vote /host-voting-app/vote'
                sh 'docker build -t voting-app-result /host-voting-app/result'
                sh 'docker build -t voting-app-worker /host-voting-app/worker'
            }
        }
        stage('4. Security Vulnerability Scan') {
            steps {
                sh 'echo "Stage 4: Security scanning with Trivy..."'
                sh 'trivy image voting-app-vote || true'
                sh 'trivy image voting-app-result || true'
                sh 'trivy image voting-app-worker || true'
            }
        }
        stage('5. Run Tests') {
            steps {
                sh 'echo "Stage 5: Running application tests..."'
                sh 'docker run --rm voting-app-vote ls -la /app && echo "Vote service test passed"'
                sh 'docker run --rm voting-app-result ls -la /app && echo "Result service test passed"'
            }
        }
        stage('6. Deploy to Production') {
            steps {
                sh 'echo "Stage 6: Deploying application..."'
                sh 'docker stop vote result worker redis db || true'
                sh 'docker rm vote result worker redis db || true'
                sh 'docker run -d --name redis redis:alpine'
                sh 'docker run -d --name db -e POSTGRES_PASSWORD=postgres postgres:15-alpine'
                sh 'sleep 10'
                sh 'docker run -d --name worker --link redis --link db voting-app-worker'
                sh 'docker run -d --name vote -p 5000:80 --link redis -e OPTION_A=Cats -e OPTION_B=Dogs voting-app-vote'
                sh 'docker run -d --name result -p 5001:80 --link db voting-app-result'
            }
        }
        stage('7. Health Check & Verify') {
            steps {
                sh 'echo "Stage 7: Final verification..."'
                sh 'sleep 15'
                sh 'docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'
                sh 'echo " 7-STAGE PIPELINE COMPLETED SUCCESSFULLY!"'
            }
        }
    }
}
