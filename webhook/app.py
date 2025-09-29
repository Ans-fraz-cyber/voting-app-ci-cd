from flask import Flask, request
import requests
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Jenkins configuration
JENKINS_URL = "http://localhost:8080"
JOB_NAME = "voting-app-pipeline"
USERNAME = "Ans Faraz"
API_TOKEN = "111fc77cf1e14c6109c62442667f178d64"

@app.route("/webhook", methods=['POST'])
def whatsapp_reply():
    try:
        incoming_msg = request.form.get('Body', '').strip().lower()
        from_number = request.form.get('From', '')
        
        print(f"📱 Received message from {from_number}: {incoming_msg}")
        
        if "yes" in incoming_msg:
            print("✅ YES received - Triggering Jenkins via API...")
            
            try:
                # Get the current build that's waiting for input
                build_info_url = f"{JENKINS_URL}/job/{JOB_NAME}/lastBuild/api/json"
                response = requests.get(build_info_url, auth=(USERNAME, API_TOKEN))
                
                if response.status_code == 200:
                    build_data = response.json()
                    build_number = build_data['number']
                    print(f"🔍 Found build #{build_number}")
                    
                    # Check if build is waiting for input and get the input ID
                    if build_data.get('actions'):
                        for action in build_data['actions']:
                            if action.get('_class') == 'hudson.model.InputStepAction':
                                input_id = action.get('id')
                                print(f"🎯 Found input step with ID: {input_id}")
                                
                                # Submit the input to continue the build
                                proceed_url = f"{JENKINS_URL}/job/{JOB_NAME}/{build_number}/input/{input_id}/submit"
                                proceed_data = {
                                    'json': '{"parameter": {"name": "APPROVE", "value": "true"}}'
                                }
                                
                                proceed_response = requests.post(
                                    proceed_url, 
                                    auth=(USERNAME, API_TOKEN),
                                    data=proceed_data,
                                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                                )
                                
                                print(f"🚀 Triggered Jenkins proceed: {proceed_response.status_code}")
                                
                                if proceed_response.status_code in [200, 201]:
                                    print("✅ Successfully triggered Jenkins to continue!")
                                    return '''<Response>
                                        <Message>✅ Build approved! Jenkins is now continuing automatically.</Message>
                                    </Response>'''
                
                # If automatic triggering fails, provide instructions
                print("⚠️ Could not auto-trigger, providing manual instructions")
                manual_url = f"{JENKINS_URL}/job/{JOB_NAME}/lastBuild"
                return f'''<Response>
                    <Message>✅ Approval received! Please manually click PROCEED in Jenkins: {manual_url}</Message>
                </Response>'''
                
            except Exception as e:
                print(f"❌ Error triggering Jenkins: {e}")
                return '''<Response>
                    <Message>✅ Approval received! Please check Jenkins and click PROCEED manually.</Message>
                </Response>'''
            
        elif "no" in incoming_msg:
            print("❌ NO received - Build rejected")
            return '''<Response>
                <Message>❌ Build cancelled! Please abort the pipeline in Jenkins.</Message>
            </Response>'''
        
        return '''<Response>
            <Message>Please reply YES to approve or NO to cancel</Message>
        </Response>'''
        
    except Exception as e:
        print(f"❌ Error in webhook: {e}")
        return "Error", 500

@app.route("/health", methods=['GET'])
def health():
    return "Webhook is running!", 200

if __name__ == "__main__":
    print("🚀 Starting WhatsApp webhook server...")
    app.run(host="0.0.0.0", port=5000, debug=True)
