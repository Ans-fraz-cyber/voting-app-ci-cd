pipeline {
    agent any
    
    stages {
        stage('Deploy Voting App') {
            steps {
                sh '''
                    echo "=== Deploying with Docker Commands ==="
                    
                    # Stop and remove existing containers
                    docker stop vote result worker redis db || true
                    docker rm vote result worker redis db || true
                    
                    # Build images
                    docker build -t voting-app-vote /host-voting-app/vote
                    docker build -t voting-app-result /host-voting-app/result  
                    docker build -t voting-app-worker /host-voting-app/worker
                    
                    # Start services
                    docker run -d --name redis redis:alpine
                    docker run -d --name db -e POSTGRES_PASSWORD=postgres postgres:15-alpine
                    sleep 5
                    docker run -d --name worker voting-app-worker
                    docker run -d --name vote -p 5000:80 voting-app-vote
                    docker run -d --name result -p 5001:80 voting-app-result
                    
                    echo "✅ DEPLOYMENT SUCCESSFUL!"
                    docker ps
                '''
            }
        }
    }
}
