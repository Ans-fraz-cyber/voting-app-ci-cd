pipeline {
    agent any
    
    stages {
        stage('📥 Checkout Code') {
            steps { 
                checkout scm
                sh 'echo "✅ Code checkout completed"'
            }
        }
        
        stage('🛑 Cleanup Previous Deployment') {
            steps {
                sh '''
                    echo "Stopping any existing containers..."
                    docker stop vote result worker redis db || true
                    docker rm vote result worker redis db || true
                    echo "✅ Cleanup completed"
                '''
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
        
        stage('🚀 Deploy Application') {
            steps {
                sh '''
                    echo "Deploying voting application..."
                    
                    # Start database services first
                    docker run -d --name redis redis:alpine
                    docker run -d --name db -e POSTGRES_PASSWORD=postgres postgres:15-alpine
                    sleep 15  # Wait for DB to be ready
                    
                    # Start application services
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
                    echo "Waiting for services to stabilize..."
                    sleep 20
                    
                    # Check container status
                    echo "=== Container Status ==="
                    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
                    
                    # Simple health checks
                    if docker ps | grep -q vote; then echo "✅ Vote service running"; else exit 1; fi
                    if docker ps | grep -q result; then echo "✅ Result service running"; else exit 1; fi
                    if docker ps | grep -q worker; then echo "✅ Worker service running"; else exit 1; fi
                    if docker ps | grep -q redis; then echo "✅ Redis running"; else exit 1; fi
                    if docker ps | grep -q db; then echo "✅ PostgreSQL running"; else exit 1; fi
                    
                    echo "🎉 ALL HEALTH CHECKS PASSED!"
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
            sh '''
                echo "=== Final Container Status ==="
                docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
            '''
        }
        failure {
            echo "❌ Pipeline failed - check logs above"
            sh '''
                echo "=== Debug Info ==="
                docker ps -a
                echo "Port 5000 status:"
                netstat -tulpn | grep 5000 || echo "Port 5000 free"
            '''
        }
    }
}
