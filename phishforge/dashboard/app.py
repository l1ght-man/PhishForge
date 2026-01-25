from flask import Flask
from flask import request          
from datetime import datetime
from flask import render_template
template_folder = '/app/templates'
app = Flask(__name__ , template_folder=template_folder)

@app.route('/')

def home ():
        return render_template('home.html')
@app.route('/demo' , methods = ['GET' , 'POST'])
def demo():
    if request.method == 'POST':
 
           username = request.form['username']
           password = request.form['password']
           timestap = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
           issues = analyse_phishing(username, password)
           risk = 'HIGH RISK' if issues else 'LOW RISK'
           log_entry = f" {timestap} | User: {username} | password: {password} | {risk} \n"
           with open("logs/phishing_logs.txt" , 'a') as f:
                  f.write(log_entry)
                  
           return render_template('results.html', issues=issues , risk= risk , log_entry=log_entry)
    return render_template('demo.html')

def analyse_phishing(username , password):
        issues =[]
        if len(password) < 6 and password in ['admin' , '12345' , 'admin']:
            issues.append("❌ Weak password (common phishing bait")
        if len(username) <5 and username.lower() in ['admin', 'administrator', 'root']:
            issues.append("❌ Suspicious username")
        if any(char.isdigit() for char in password) and len(password) < 3:
            issues.append("❌ Sequential/repeated chars")
        return issues
@app.route('/dashboard')
def dashboard():
        try:
              with open('logs/phishing_logs.txt', 'r') as f:
                    logs = f.readlines()[-10:]
        except:
              logs = ['no logs yet!']
        log_html = ''.join(f'<p>{log}</p>' for log in logs)
        return f"""
    <h1>🛡️ Phishing Detection Dashboard</h1>
    <p>Recent detections:</p>
    {log_html}
    <p><a href="/demo">→ Test new login</a> | <a href="/">← Home</a></p>
    """
                  
if __name__ == '__main__':
        app.run(debug=True, host='0.0.0.0' , port=8080)
