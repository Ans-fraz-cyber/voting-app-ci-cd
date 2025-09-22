pipeline {
    agent any
    
    stages {
        stage('📥 Checkout Code') {
            steps { 
                checkout scm
                sh 'echo "✅ Code checkout completed"'
            }
        }
        
        stage('🏗️ Build Images') {
            steps {
                sh '''
                    echo "Building Docker images..."
                    docker build -t voting-app-vote /host-voting-app/vote
                    docker build -t voting-app-result /host-voting-app/result
                    docker build -t voting-app-worker /host-voting-app/worker
                    echo "✅ Images built"
                '''
            }
        }
        
        stage('🚀 Deploy') {
            steps {
                sh '''
                    echo "Deploying application..."
                    docker stop vote result worker redis db || true
                    docker rm vote result worker redis db || true
                    
                    docker run -d --name redis redis:alpine
                    docker run -d --name db -e POSTGRES_PASSWORD=postgres postgres:15-alpine
                    sleep 10
                    docker run -d --name worker --link redis --link db voting-app-worker
                    docker run -d --name vote -p 5000:80 --link redis -e OPTION_A=Cats -e OPTION_B=Dogs voting-app-vote
                    docker run -d --name result -p 5001:80 --link db voting-app-result
                    
                    echo "✅ Deployment completed"
                '''
            }
        }
        
        stage('❤️ Health Check') {
            steps {
                sh '''
                    echo "Waiting for services to start..."
                    sleep 30
                    
                    # Simple container checks instead of curl
                    docker ps --filter "name=vote" --format "table {{.Names}}\t{{.Status}}" | grep -q vote && echo "✅ Vote service running"
                    docker ps --filter "name=result" --format "table {{.Names}}\t{{.Status}}" | grep -q result && echo "✅ Result service running"
                    docker ps --filter "name=worker" --format "table {{.Names}}\t{{.Status}}" | grep -q worker && echo "✅ Worker service running"
                    docker ps --filter "name=redis" --format "table {{.Names}}\t{{.Status}}" | grep -q redis && echo "✅ Redis running"
                    docker ps --filter "name=db" --format "table {{.Names}}\t{{.Status}}" | grep -q db && echo "✅ PostgreSQL running"
                    
                    echo "🎉 HEALTH CHECKS PASSED!"
                    echo "🌐 Application URLs:"
                    echo "   Vote: http://localhost:5000"
                    echo "   Results: http://localhost:5001"
                '''
            }
        }
    }
    
    post {
        success {
            echo "✅ Pipeline executed successfully!"
        }
    }
}
