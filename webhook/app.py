from flask import Flask, request
import os
import time

app = Flask(__name__)

@app.route("/webhook", methods=['POST'])
def whatsapp_reply():
    incoming_msg = request.form.get('Body', '').strip().lower()
    
    print(f"📱 Received message: {incoming_msg}")
    
    if "yes" in incoming_msg:
        print("✅ YES received - Creating approval signal...")
        
        try:
            # Create a file to signal approval
            os.system("touch /tmp/jenkins_approved && echo 'Creating approval signal...'")
            print("✅ Approval signal created!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        return '''<Response>
            <Message>✅ Build approved! Jenkins will continue immediately...</Message>
        </Response>'''
    
    elif "no" in incoming_msg:
        print("❌ NO received - Build rejected")
        return '''<Response>
            <Message>❌ Build cancelled!</Message>
        </Response>'''
    
    return '''<Response>
        <Message>Please reply YES to approve or NO to cancel</Message>
    </Response>'''

if __name__ == "__main__":
    print("🚀 Starting WhatsApp webhook server...")
    app.run(host="0.0.0.0", port=5000, debug=True)
