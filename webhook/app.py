from flask import Flask, request
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route("/webhook", methods=['POST'])
def whatsapp_reply():
    try:
        incoming_msg = request.form.get('Body', '').strip().lower()
        from_number = request.form.get('From', '')
        
        print(f"📱 Received message from {from_number}: {incoming_msg}")
        
        if "yes" in incoming_msg:
            print("✅ YES received - Creating approval file...")
            
            # Create the approval file
            try:
                with open('/tmp/jenkins_approved', 'w') as f:
                    f.write('approved')
                print("✅ Approval file created successfully!")
                os.system('ls -la /tmp/jenkins_approved')  # Debug: check file
            except Exception as e:
                print(f"❌ Error creating file: {e}")
            
            return '''<Response>
                <Message>✅ Build approved! Jenkins will continue immediately.</Message>
            </Response>'''
            
        elif "no" in incoming_msg:
            print("❌ NO received - Build rejected")
            return '''<Response>
                <Message>❌ Build cancelled!</Message>
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
