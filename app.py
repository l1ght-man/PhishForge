from flask import Flask
from flask import request          
from datetime import datetime

app = Flask(__name__)

@app.route('/')

def home ():
        return "<h1>Phishing Detection Lab v1.0 - Ready!</h1><p>Server running ...</p>"
@app.route('/demo' , methods = ['GET' , 'POST'])
def demo():
    if request.method == 'POST':
 
           username = request.form['username']
           password = request.form['password']
           timestap = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
           issues = analyse_phishing(username, password)
           risk = 'HIGH RISK' if issues else 'LOW RISK'
           log_entry = f" {timestap} | User: {username} | password: {password} | {risk} \n"
           with open("phishing_logs.txt" , 'a') as f:
                  f.write(log_entry)
                  
           return f"<h3>🚨 PHISHING ATTEMPT DETECTED!</h3><p>Username: {username}</p>"
    return"""<h2>🚨 FAKE LOGIN PAGE (for analysis)</h2>
    <form method="POST">
      Username: <input name="username" type="text"><br>
      Password: <input name="password" type="password"><br>  
      <button>Login Now!</button>
    </form>"""

def analyse_phishing(username , password):
        issues =[]
        if len(password) < 6 and password in ['admin' , '12345' , 'admin']:
            issues.append("❌ Weak password (common phishing bait")
        if len(username) <5 and username.lower() in ['admin', 'administrator', 'root']:
            issues.append("❌ Suspicious username")
        if any(char.isdigit() for char in password) and len(password) < 3:
            issues.append("❌ Sequential/repeated chars")

        return issues          
if __name__ == '__main__':
        app.run(debug=True, port=8080)
