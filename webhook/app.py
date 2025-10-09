from flask import Flask, request, jsonify
import requests
import json
import base64
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Jenkins configuration
JENKINS_URL = "http://localhost:8080"
JOB_NAME = "voting-app-pipeline"
USERNAME = "Ans Faraz"
API_TOKEN = "111fc77cf1e14c6109c62442667f178d64"

# Create basic auth header
auth_string = f"{USERNAME}:{API_TOKEN}"
auth_bytes = auth_string.encode('ascii')
base64_auth = base64.b64encode(auth_bytes).decode('ascii')
headers = {
    'Authorization': f'Basic {base64_auth}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

@app.route("/webhook", methods=['POST'])
def whatsapp_reply():
    try:
        incoming_msg = request.form.get('Body', '').strip().lower()
        from_number = request.form.get('From', '')
        
        print(f"📱 Received message from {from_number}: {incoming_msg}")
        
        if "yes" in incoming_msg:
            print("✅ YES received - Triggering Jenkins pipeline...")
            
            # Try multiple methods to trigger Jenkins
            success = trigger_jenkins_direct()
            
            if success:
                print("🎉 Successfully triggered Jenkins pipeline!")
                send_whatsapp_simple("✅ Build approved! Jenkins pipeline is now continuing automatically...")
                return jsonify({
                    "status": "success", 
                    "message": "✅ Build approved! Pipeline continuing automatically..."
                })
            else:
                print("❌ All auto-trigger methods failed")
                send_whatsapp_simple("✅ Approval received! But could not auto-trigger. Please click PROCEED in Jenkins.")
                return jsonify({
                    "status": "manual_required",
                    "message": "Approval received but please click PROCEED in Jenkins"
                })
        
        elif "no" in incoming_msg:
            print("❌ NO received - Build rejected")
            send_whatsapp_simple("❌ Build cancelled! Please abort the pipeline in Jenkins.")
            return jsonify({
                "status": "rejected",
                "message": "Build cancelled"
            })
        
        return jsonify({
            "status": "invalid",
            "message": "Please reply YES to approve or NO to cancel"
        })
        
    except Exception as e:
        print(f"❌ Error in webhook: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500

def trigger_jenkins_direct():
    """Direct method to trigger Jenkins input step"""
    try:
        print("🔄 Getting current build information...")
        
        # Get the last build
        build_info_url = f"{JENKINS_URL}/job/{JOB_NAME}/lastBuild/api/json"
        response = requests.get(build_info_url, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Failed to get build info: {response.status_code}")
            return False
            
        build_data = response.json()
        build_number = build_data['number']
        print(f"🔍 Found build #{build_number}")
        
        # Check if build is in input state and get input ID
        input_id = find_input_id(build_data)
        if not input_id:
            print("❌ No input step found or build not waiting for input")
            return False
            
        print(f"🎯 Found input step with ID: {input_id}")
        
        # Submit the input to continue
        proceed_url = f"{JENKINS_URL}/job/{JOB_NAME}/{build_number}/input/{input_id}/submit"
        proceed_data = {
            'json': '{"parameter": {"name": "APPROVE", "value": "true"}}'
        }
        
        print(f"🚀 Submitting input to: {proceed_url}")
        proceed_response = requests.post(proceed_url, data=proceed_data, headers=headers)
        
        print(f"📡 Proceed response: {proceed_response.status_code}")
        
        if proceed_response.status_code in [200, 201, 302]:
            print("✅ Successfully submitted input! Pipeline should continue.")
            return True
        else:
            print(f"❌ Failed to submit input: {proceed_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error in direct trigger: {e}")
        return False

def find_input_id(build_data):
    """Find the input step ID from build data"""
    try:
        if build_data.get('actions'):
            for action in build_data['actions']:
                # Look for input step action
                if action.get('_class') == 'hudson.model.InputStepAction':
                    return action.get('id')
                
                # Alternative class names
                if 'InputStepAction' in str(action.get('_class', '')):
                    return action.get('id')
                    
        # If no input found, check if build is in progress
        if build_data.get('inProgress', False):
            print("⚠️ Build is in progress but no input step found")
            
        return None
    except Exception as e:
        print(f"❌ Error finding input ID: {e}")
        return None

def send_whatsapp_simple(message):
    """Simple WhatsApp sender using requests"""
    try:
        print(f"📤 Would send WhatsApp: {message}")
        # In production, this would call Twilio API
        # For now, we just log it
        return True
    except Exception as e:
        print(f"❌ Error in WhatsApp sender: {e}")
        return False

@app.route("/health", methods=['GET'])
def health():
    return jsonify({"status": "healthy", "message": "Webhook is running!"})

@app.route("/test-trigger", methods=['GET'])
def test_trigger():
    """Test endpoint to manually trigger Jenkins"""
    success = trigger_jenkins_direct()
    return jsonify({
        "status": "success" if success else "failed",
        "message": "Jenkins triggered successfully" if success else "Failed to trigger Jenkins"
    })

if __name__ == "__main__":
    print("🚀 Starting WhatsApp webhook server...")
    print("📡 Endpoints:")
    print("   POST /webhook        - WhatsApp webhook")
    print("   GET  /health         - Health check") 
    print("   GET  /test-trigger   - Test Jenkins trigger")
    app.run(host="0.0.0.0", port=5000, debug=True)
