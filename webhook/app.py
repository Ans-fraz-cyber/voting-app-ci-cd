from flask import Flask, request
import requests
import os

app = Flask(__name__)

@app.route("/webhook", methods=['POST'])
def whatsapp_reply():
    incoming_msg = request.form.get('Body', '').strip().lower()
    
    print(f"📱 Received message: {incoming_msg}")
    
    if "yes" in incoming_msg:
        print("✅ YES received - Triggering new build immediately!")
        
        try:
            # Trigger a NEW build immediately (this will skip the wait)
            os.system("curl -s -X POST http://localhost:8080/job/voting-app-pipeline/buildWithParameters?APPROVED=true --user 'Ans Faraz:111fc77cf1e14c6109c62442667f178d64' &")
            print("🚀 Triggered new build with approval!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        return '''<Response>
            <Message>✅ Build approved! Starting new build immediately...</Message>
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
