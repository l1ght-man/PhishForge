# 🛡️ PhishForge

> **A self-hosted phishing simulation lab for security awareness training**

PhishForge lets you safely simulate phishing attacks in a controlled environment:
- Send test emails via **MailHog** (no real email sent)
- Capture credentials on a fake login page
- Analyze results in a dashboard with department-level insights
- Export reports as **PDF/CSV**

> ⚠️ **Ethical Use Only**: Use **exclusively** on systems/mailboxes you own or have explicit permission to test. Unauthorized use is illegal.

---

## ✨ Features

- **Campaign Management**: Create phishing campaigns with custom HTML emails & landing pages  
- **Victim Tracking**: Import targets via CSV, prevent duplicates, manage by department  
- **Real-Time Analytics**: View conversion rates, department risk, captured credentials  
- **Exportable Reports**: Generate PDF summaries or raw CSV data  
- **100% Local**: Runs in Docker with MailHog — no external dependencies  

---

## 📦 Tech Stack

| Component       | Technology      |
|-----------------|-----------------|
| Backend         | Python 3, Flask |
| Database        | SQLite          |
| Email Testing   | MailHog         |
| Containerization| Docker Compose  |
| Frontend        | Bootstrap 5     |

---

## 🗂️ Project Structure

```text
phishforge/
├── campaigns/          # Email campaign sender
├── dashboard/          # Analytics dashboard (Flask app)
├── landing/            # Fake login page (Flask app)
├── models/             # Database logic
├── templates/          # HTML templates (Jinja2)
├── logs/               # Runtime logs (phishing_logs.txt)
├── phishforge.db       # SQLite database
├── victims.csv         # Target list template
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)

### 1. Clone & Configure
```bash
git clone https://github.com/l1ght-man/phishforge.git
cd phishforge

# Edit targets (one email per line)
nano victims.csv
```

### 2. Launch Services
```bash
docker compose up --build
```

### 3. Access Interfaces
| Service          | URL                     |
|------------------|-------------------------|
| Dashboard        | http://localhost:8080   |
| Phishing Page    | http://localhost:3000   |
| MailHog (Emails) | http://localhost:8025   |

### 4. Send a Campaign
```bash
# Run once to send emails to victims.csv
docker compose run --rm campaign
```

> 💡 Credentials are saved to `logs/phishing_logs.txt` and visible in the dashboard.

---

## 🧪 Development Notes

- **Database**: All data stored in `phishforge.db` (SQLite)  
- **Logs**: Shared volume at `./logs/`  
- **Dependencies**: Update `requirements.txt` → rebuild with `docker compose build`  
- **Victim Management**:  
  - Add/edit/delete victims via dashboard  
  - Automatic duplicate prevention  
  - Department-based analytics  

---

## 📤 Export Options

From any campaign's **Stats** page (`/campaign/X/stats`):
- **PDF Report**: Professional summary with charts  
- **Victims CSV**: Raw target list  
- **Credentials CSV**: Captured logins  

---

## ⚖️ Legal & Ethical Use

**PhishForge is for education and security awareness ONLY.**  
- ✅ **Do**: Test with explicit consent, focus on training  
- ❌ **Don't**: Target unauthorized systems, use real credentials, or shame users  

The authors assume **no liability** for misuse. Check your local laws before use.

---

## 📜 License

MIT License – see [LICENSE](LICENSE) for details.

---

> 🔐 **Remember**: Security awareness builds resilience. Use this tool to educate, not exploit.