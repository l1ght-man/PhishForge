import sqlite3
import os
from typing import List, Dict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


DB_PATH = '/app/data/phishforge.db'
SMTP_HOST = os.getenv('SMTP_HOST', 'mailhog')
SMTP_PORT = int(os.getenv('SMTP_PORT', '1025'))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'noreply@example.com')

def init_db():
    """Creates tables if they don't exist"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email_subject TEXT NOT NULL,
            email_body_html TEXT NOT NULL,
            landing_page_html TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS hits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER,
            email TEXT,
            password TEXT,
            ip_address TEXT,
            user_agent TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS victims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER NOT NULL,
            email TEXT NOT NULL,
            name TEXT,
            department TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            victim_id INTEGER NOT NULL,
            campaign_id INTEGER NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (victim_id) REFERENCES victims (id),
            FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_campaigns() -> List[Dict]:
    """Get all campaigns."""
    conn = get_db_connection()
    campaigns = conn.execute('SELECT * FROM campaigns ORDER BY created_at DESC').fetchall()
    conn.close()
    return [dict(campaign) for campaign in campaigns]  # Convert Row to dict

def get_campaign(campaign_id: int) -> Dict:
    """Get single campaign by ID"""
    conn = get_db_connection()
    campaign = conn.execute('SELECT * FROM campaigns WHERE id = ?', (campaign_id,)).fetchone()
    conn.close()
    return dict(campaign) if campaign else None  # Convert Row to dict

def create_campaign(name: str, subject: str, email_html: str, landing_html: str) -> int:
    """Creates a new campaign, returns the ID"""
    conn = get_db_connection()
    c = conn.cursor()
    conn.execute('''
        INSERT INTO campaigns (name, email_subject, email_body_html, landing_page_html) 
        VALUES (?, ?, ?, ?)
    ''', (name, subject, email_html, landing_html))
    conn.commit()
    campaign_id = c.lastrowid
    c.close()
    conn.close()
    print(f"Created campaign #{campaign_id}: {name}")
    return campaign_id


def add_victim(campaign_id: int, email: str, name: str = None, department: str = None) -> int:
    """Add a single victim to the campaign, returns the victim ID"""
    conn = get_db_connection()
    c = conn.cursor()
    try:
        existing = conn.execute('''
            SELECT id FROM victims WHERE campaign_id = ? AND email = ?''', (campaign_id, email)
        ).fetchone()
        if existing:
            return None
        conn.execute('''
            INSERT INTO victims (campaign_id, email, name, department)
            VALUES (?, ?, ?, ?)
        ''', (campaign_id, email, name, department))
        conn.commit()
        victim_id = c.lastrowid
        return victim_id
    finally:
        conn.close()
def get_victims(campaign_id: int) -> List[dict]:
    """Get all the victims for a campaign"""
    conn = get_db_connection()
    victims = conn.execute('''
        SELECT * FROM victims
        WHERE campaign_id = ?
        ORDER BY created_at DESC
    ''', (campaign_id,)).fetchall()
    conn.close()
    return [dict(victim) for victim in victims]


def log_click(victim_id: int, campaign_id: int, ip_address: str, user_agent: str):
    """Log a click when someone visits the landing page"""
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO clicks (victim_id, campaign_id, ip_address, user_agent)
        VALUES (?, ?, ?, ?)
    ''', (victim_id, campaign_id, ip_address, user_agent))
    conn.commit()
    conn.close()


def get_victim_by_id(victim_id: int) -> dict:
    """Get victim by their unique ID (for clicking)"""
    conn = get_db_connection()
    victim = conn.execute('SELECT * FROM victims WHERE id = ?', (victim_id,)).fetchone()
    conn.close()
    return dict(victim) if victim else None


def delete_campaign(campaign_id: int):
    """Delete campaign + all related data"""
    
    print(f"DEBUG: delete_campaign called with: {campaign_id} (type: {type(campaign_id)})")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    cid = int(campaign_id)
    print(f"DEBUG: Converted to int: {cid}")

    c.execute('DELETE FROM hits WHERE campaign_id = ?', (cid,))
    print(f"DEBUG: Deleted {c.rowcount} hits")
    
    c.execute('DELETE FROM victims WHERE campaign_id = ?', (cid,))
    print(f"DEBUG: Deleted {c.rowcount} victims")
    
    c.execute('DELETE FROM clicks WHERE campaign_id = ?', (cid,))
    print(f"DEBUG: Deleted {c.rowcount} clicks")
    
    c.execute('DELETE FROM campaigns WHERE id = ?', (cid,))
    print(f"DEBUG: Deleted {c.rowcount} campaigns")
    
    conn.commit()
    deleted_count = c.rowcount
    conn.close()
    print(f"🗑️ Deleted campaign {campaign_id}")
    return deleted_count


def send_campaign_emails(campaign_id: int):
    """Send personalized phishing emails to all victims in campaign"""
    campaign = get_campaign(campaign_id)
    if not campaign:
        return False, "Campaign not found"
    victims = get_victims(campaign_id)
    if not victims:
        return False, "No victims found"
    
    send_count = 0
    smtp_server = "mailhog"
    smtp_port = 1025
    for victim in victims:
        tracking_url = f"http://localhost:3000/c/{campaign_id}?vid={victim['id']}"
        
        email_body = campaign['email_body_html']
        email_body = email_body.replace('{{name}}', victim['name'] or victim['email'])
        email_body = email_body.replace('{{department}}', victim['department'] or 'team')
        email_body = email_body.replace('{{landing_url}}', tracking_url)
        email_body = email_body.replace('{{email}}', victim['email'])
        msg = MIMEMultipart()
        msg['From'] = f"security@phishforge.local"
        msg['To'] = victim['email']
        msg['Subject'] = campaign['email_subject']
        msg.attach(MIMEText(email_body, 'html'))

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.send_message(msg)
            server.quit()
            send_count += 1
            print(f"📧 SENT to {victim['email']} → {tracking_url}")
        except Exception as e:
            print(f"❌ FAILED to send to {victim['email']}: {e}")
    return True, f"Sent {send_count}/{len(victims)} emails"
