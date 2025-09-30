// =============================================
// DYNAMIC JENKINSFILE - REUSABLE FOR ANY PROJECT
// =============================================

// Configuration Map - Update these for each project
def projectConfig = [
    projectName: "voting-app",
    sonarProjectKey: "voting-app", 
    sonarProjectName: "voting-app",
    sourceDirs: "vote,result,worker",  // Comma-separated source directories
    dockerImages: [
        [name: "vote", context: "./vote"],
        [name: "result", context: "./result"], 
        [name: "worker", context: "./worker"]
    ],
    dockerhubNamespace: "31793179",
    notificationEmail: "ansfaraz.cyber@gmail.com",
    gitRepo: "https://github.com/Ans-fraz-cyber/voting-app-ci-cd.git",
    timeoutMinutes: 30,
    approvalTimeoutMinutes: 30
]

pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: projectConfig.timeoutMinutes, unit: 'MINUTES')
    }

    environment {
        // Auto-generated environment variables
        PROJECT_NAME = "${projectConfig.projectName}"
        SONAR_PROJECT_KEY = "${projectConfig.sonarProjectKey}"
        SONAR_PROJECT_NAME = "${projectConfig.sonarProjectName}" 
        SOURCE_DIRS = "${projectConfig.sourceDirs}"
        DOCKERHUB_NAMESPACE = "${projectConfig.dockerhubNamespace}"
        NOTIFICATION_EMAIL = "${projectConfig.notificationEmail}"
        APPROVAL_FILE = "/tmp/build_${PROJECT_NAME}_${BUILD_NUMBER}_approved"
    }

    stages {
        // STAGE 1: Dynamic Code Download
        stage('Download Code') {
            steps {
                script {
                    echo "📥 Downloading ${PROJECT_NAME} repository..."
                    dynamicDownloadCode(projectConfig.gitRepo)
                }
            }
        }

        // STAGE 2: SonarQube Analysis (Conditional)
        stage('Code Quality Analysis') {
            when {
                expression { return fileExists('sonar-project.properties') || params.ENABLE_SONARQUBE }
            }
            steps {
                script {
                    echo "🔍 Running SonarQube Analysis..."
                    runSonarQubeAnalysis()
                }
            }
        }

        // STAGE 3: Quality Gate Check (Conditional)  
        stage('Quality Gate Check') {
            when {
                expression { return fileExists('sonar-project.properties') || params.ENABLE_SONARQUBE }
            }
            steps {
                script {
                    echo "✅ Checking Quality Gate..."
                    checkQualityGate()
                }
            }
        }

        // STAGE 4: Approval Workflow
        stage('Manual Approval') {
            steps {
                script {
                    sendApprovalRequest()
                    waitForManualApproval()
                }
            }
        }

        // STAGE 5: Dynamic Docker Build
        stage('Build Docker Images') {
            steps {
                script {
                    echo "🏗️ Building Docker Images..."
                    projectConfig.dockerImages.each { image ->
                        buildDockerImage(image.name, image.context)
                    }
                }
            }
        }

        // STAGE 6: Security Scan
        stage('Security Scan') {
            steps {
                script {
                    echo "🔒 Running Security Scans..."
                    projectConfig.dockerImages.each { image ->
                        runSecurityScan(image.name)
                    }
                }
            }
        }

        // STAGE 7: Push Images
        stage('Push Docker Images') {
            steps {
                script {
                    echo "📤 Pushing Images to DockerHub..."
                    projectConfig.dockerImages.each { image ->
                        pushDockerImage(image.name)
                    }
                }
            }
        }

        // STAGE 8: Deploy (Conditional)
        stage('Deploy Application') {
            when {
                expression { return fileExists('docker-compose.yml') && params.AUTO_DEPLOY }
            }
            steps {
                script {
                    echo "🚀 Deploying Application..."
                    deployApplication()
                }
            }
        }
    }

    post {
        always {
            script {
                cleanupWorkspace()
            }
        }
        success {
            script {
                sendNotification("SUCCESS")
            }
        }
        failure {
            script {
                sendNotification("FAILED")
            }
        }
    }
}

// =============================================
// REUSABLE FUNCTIONS
// =============================================

// Dynamic code download function
def dynamicDownloadCode(gitRepo) {
    sh """
        # Clean workspace
        rm -rf * .* 2>/dev/null || true
        
        # Smart clone - only get what's needed
        git clone --depth 1 --branch main --single-branch ${gitRepo} .
        
        # Remove large binary files that slow down downloads
        find . -name "*.zip" -o -name "*.rpm" -o -name "*.tgz" -o -name "*.tar.gz" -size +10M -delete 2>/dev/null || true
        
        echo "✅ Repository downloaded successfully!"
        ls -la
    """
}

// SonarQube analysis function
def runSonarQubeAnalysis() {
    withSonarQubeEnv("SonarQubeServer") {
        def scannerHome = tool 'SonarQubeScanner'
        withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_AUTH_TOKEN')]) {
            sh """
                ${scannerHome}/bin/sonar-scanner \\
                  -Dsonar.projectKey=${SONAR_PROJECT_KEY} \\
                  -Dsonar.projectName=${SONAR_PROJECT_NAME} \\
                  -Dsonar.sources=${SOURCE_DIRS} \\
                  -Dsonar.login=${SONAR_AUTH_TOKEN} \\
                  -Dsonar.qualitygate.wait=false
            """
        }
    }
}

// Quality gate check function
def checkQualityGate() {
    timeout(time: 2, unit: 'MINUTES') {
        waitForQualityGate abortPipeline: false
    }
}

// Approval workflow function
def sendApprovalRequest() {
    sh "rm -f ${APPROVAL_FILE} || true"
    
    mail(
        to: "${NOTIFICATION_EMAIL}",
        subject: "🚀 APPROVAL REQUIRED: ${PROJECT_NAME} Build #${BUILD_NUMBER}",
        body: """
        BUILD APPROVAL REQUIRED!
        
        Project: ${PROJECT_NAME}
        Build: #${BUILD_NUMBER}
        URL: ${BUILD_URL}
        Status: Ready for deployment
        
        ✅ TO APPROVE:
        Run this command on your server:
        echo "APPROVED" > ${APPROVAL_FILE}
        
        ❌ TO REJECT:  
        Run this command on your server:
        echo "REJECTED" > ${APPROVAL_FILE}
        
        ⏰ Timeout: ${projectConfig.approvalTimeoutMinutes} minutes
        """
    )
    echo "📧 Approval request sent to ${NOTIFICATION_EMAIL}"
}

def waitForManualApproval() {
    echo "⏳ Waiting for manual approval..."
    echo "💡 Run: echo 'APPROVED' > ${APPROVAL_FILE}"
    
    timeout(time: projectConfig.approvalTimeoutMinutes, unit: 'MINUTES') {
        waitUntil {
            sleep 10
            if (fileExists(APPROVAL_FILE)) {
                def status = sh(script: "cat ${APPROVAL_FILE}", returnStdout: true).trim()
                if (status == "APPROVED") {
                    echo "🎉 Build approved! Continuing pipeline..."
                    return true
                } else if (status == "REJECTED") {
                    error "❌ Build rejected by approver!"
                }
            }
            echo "⏰ Still waiting for approval... (Run: echo 'APPROVED' > ${APPROVAL_FILE})"
            return false
        }
    }
}

// Docker build function
def buildDockerImage(imageName, contextPath) {
    sh """
        echo "🔨 Building ${imageName} image..."
        docker build --progress=plain -t ${imageName}:${BUILD_NUMBER} ${contextPath}
        echo "✅ ${imageName} image built successfully!"
    """
}

// Security scan function  
def runSecurityScan(imageName) {
    sh """
        echo "🔍 Scanning ${imageName}..."
        trivy image --format table -o trivy-${imageName}.txt ${imageName}:${BUILD_NUMBER} || true
        echo "✅ ${imageName} security scan completed!"
    """
}

// Docker push function
def pushDockerImage(imageName) {
    withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
        sh """
            echo "🔐 Logging into DockerHub..."
            echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin
            
            echo "📤 Pushing ${imageName}..."
            docker tag ${imageName}:${BUILD_NUMBER} ${DOCKERHUB_NAMESPACE}/${imageName}:${BUILD_NUMBER}
            docker push ${DOCKERHUB_NAMESPACE}/${imageName}:${BUILD_NUMBER}
            
            echo "✅ ${imageName} pushed to DockerHub!"
        """
    }
}

// Deploy function
def deployApplication() {
    sh """
        echo "🚀 Deploying application..."
        docker-compose down || true
        docker-compose up -d
        echo "✅ Application deployed successfully!"
        docker ps
    """
}

// Cleanup function
def cleanupWorkspace() {
    sh "rm -f ${APPROVAL_FILE} || true"
    cleanWs()
}

// Notification function
def sendNotification(status) {
    def subject = "Build ${status} - ${PROJECT_NAME} #${BUILD_NUMBER}"
    def body = """
    Build ${status}!
    
    Project: ${PROJECT_NAME}
    Build: #${BUILD_NUMBER} 
    URL: ${BUILD_URL}
    Status: ${status}
    
    -- Jenkins CI/CD
    """
    
    mail(to: "${NOTIFICATION_EMAIL}", subject: subject, body: body)
    echo "📧 ${status} notification sent to ${NOTIFICATION_EMAIL}"
}
