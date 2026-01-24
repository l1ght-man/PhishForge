import smtplib 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv
def send_phishing_email (to_email , victim_name) :
    msg = MIMEMultipart('alternative')
    msg['Subject'] = '🚨 URGENT: Microsoft Account Verification Required'
    msg['From'] = 'security@yourcompany.com'
    msg['to'] = to_email
    html = f"""
    <html>
    <body style='font-family:Segoe UI;max-width:600px;margin:0 auto;padding:20px;'>
        <h2 style='color:#d13438;'>Security Alert: Immediate Action Required</h2>
        <p>Dear {victim_name},</p>
        <p>We detected <strong>unusual activity</strong> on your Microsoft account.</p>
        <p style='background:#fff3cd;padding:15px;border-radius:6px;border-left:4px solid #ffc107;'>
            <strong>Verify your account within 24 hours</strong> or access will be suspended.
        </p>
        <a href='http://localhost:3000' style='background:#0078d4;color:white;padding:15px 30px;text-decoration:none;border-radius:6px;font-size:16px;display:inline-block;'>Verify Account Now</a>
        <p style='color:#666;font-size:14px;margin-top:30px;'>Microsoft Account Security Team</p>
    </body>
    </html>
    """
    html_part = MIMEText(html , 'html')
    msg.attach(html_part)
    server = smtplib.SMTP('mailhog', 1025)
    server.send_message(msg)
    server.quit()                                       
    print(f"✅ Phishing email sent to {to_email}")

def compaign_attack(csv_file = 'victims.csv'):
    sent = 0
    with open(csv_file, 'r') as f :
        reader = csv.DictReader(f)
        for row in reader :
            send_phishing_email(row['email'] , row['name'])
            sent += 1
            print(f"Attacked: {row['name']} ({sent}/{len(list(csv.reader(open(csv_file))))-1})")
    print(f"✅ Campaign complete: {sent} targets hit")

if __name__ == '__main__' :
    compaign_attack()