# PhishForge

**A self-hosted phishing simulation platform for security awareness training and red team exercises.**

PhishForge enables security teams to conduct controlled phishing simulations in isolated environments. Test emails are captured by MailHog (no external delivery), credentials are logged for analysis, and comprehensive reports track organizational vulnerability by department.

**Legal Notice**: This tool is designed exclusively for authorized security testing and employee training. Unauthorized phishing simulations are illegal. Always obtain explicit written permission before deployment.

---

## Features

- **Campaign Management**: Create phishing campaigns with custom HTML email templates and landing pages
- **Victim Tracking**: CSV import with automatic duplicate detection, department-based segmentation
- **Analytics Dashboard**: Real-time conversion tracking, department risk scoring, credential capture logs
- **Report Generation**: Export campaign data as PDF reports or raw CSV files
- **Isolated Testing**: Fully containerized with MailHog SMTP server—no external network dependencies

---

## Tech Stack

| Component       | Technology      |
|-----------------|-----------------|
| Backend         | Python 3.12, Flask |
| Database        | SQLite          |
| Email Testing   | MailHog         |
| Containerization| Docker Compose  |
| Frontend        | Bootstrap 5 (AI-assisted) |

**Development Notes**: The backend logic, database architecture, and campaign orchestration were developed manually. Frontend templates and UI components were generated with AI assistance (Claude/GPT) and integrated into the Flask application.

---

## Architecture

```text
phishforge/
├── campaigns/          # Email delivery service
├── dashboard/          # Web interface (Flask)
├── landing/            # Phishing page service (Flask)
├── models/             # SQLite ORM & queries
├── templates/          # Jinja2 HTML templates
├── logs/               # Credential capture logs
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

**Service Architecture**:
- **Dashboard** (port 8080): Campaign CRUD, victim management, analytics
- **Landing** (port 3000): Serves campaign-specific phishing pages at `/c/<campaign_id>`
- **MailHog** (ports 1025/8025): SMTP server + web UI for email inspection
- **SQLite**: Shared database via Docker volume

---

## Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+

### Installation

```bash
git clone https://github.com/l1ght-man/phishforge.git
cd phishforge

# (Optional) Configure Flask secret key for production
export SECRET_KEY="your-secure-random-key-here"

# Start all services
docker compose up --build
```

### Access Points

| Service          | URL                     | Purpose |
|------------------|-------------------------|---------|
| Dashboard        | http://localhost:8080   | Campaign management & analytics |
| Landing Service  | http://localhost:3000   | Phishing pages at `/c/<campaign_id>` |
| MailHog          | http://localhost:8025   | Email inspection UI |

### Workflow

1. **Create Campaign**: Dashboard → Create Campaign → Define email/landing HTML
2. **Add Victims**: Upload CSV or manually add targets with department tags
3. **Send Campaign**: Click "Send Emails" to deliver to MailHog
4. **Monitor**: Check MailHog for emails, track clicks/submissions in Dashboard
5. **Export**: Generate PDF reports or download CSV data

**Note**: Captured credentials are logged to `logs/phishing_logs.txt` and stored in SQLite.

---

## Configuration

### Environment Variables

| Variable       | Default                          | Description |
|----------------|----------------------------------|-------------|
| `SECRET_KEY`   | `phishforge-dev-key-change-...`  | Flask session secret (change in production) |
| `SMTP_HOST`    | `mailhog`                        | SMTP server hostname |
| `SMTP_PORT`    | `1025`                           | SMTP server port |

### Database

SQLite database located at `/app/data/phishforge.db` inside containers. Persisted via Docker volume `db_data`.

**Tables**:
- `campaigns`: Campaign metadata (name, email/landing HTML)
- `victims`: Target list with department tags
- `hits`: Captured credentials (email, password, IP, timestamp)
- `clicks`: Landing page visits (victim tracking)

---

## Development

### Local Setup (Without Docker)

```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

export PYTHONPATH=.
python phishforge/dashboard/app.py  # Port 8080
python phishforge/landing/attack_surface.py  # Port 3000
```

### Adding Dependencies

```bash
# Update requirements.txt, then rebuild
docker compose build --no-cache
docker compose up
```

### Database Migrations

No migration tool configured. Schema changes require manual `ALTER TABLE` or recreating containers with `-v` flag:

```bash
docker compose down -v  # Destroys database
docker compose up --build
```

---

## Security Considerations

**Deployment Warnings**:
- Default Flask secret key is insecure—set `SECRET_KEY` env var
- No authentication on dashboard—do not expose publicly
- SQLite is not suitable for high-concurrency production workloads
- Logs contain plaintext passwords—secure file permissions required

**Intended Use**: Internal lab environments, isolated networks, or localhost testing only.

---

## Legal & Ethics

This software is provided for **authorized security testing and educational purposes only**. 

**Prohibited Uses**:
- Unauthorized access to computer systems (violations of CFAA, GDPR, etc.)
- Targeting individuals without explicit written consent
- Using captured credentials for unauthorized access
- Deploying without organizational approval

**User Responsibilities**:
- Obtain legal authorization before deployment
- Comply with local laws and regulations (GDPR, CCPA, etc.)
- Securely destroy captured data after testing
- Never use in production environments without proper controls

The authors and contributors assume no liability for misuse. You are solely responsible for compliance with applicable laws.

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Backend and architecture: Manual development
- Frontend templates: AI-assisted generation 
- Email testing: [MailHog](https://github.com/mailhog/MailHog) project
- PDF generation: [WeasyPrint](https://weasyprint.org/)

---

**Disclaimer**: PhishForge is a penetration testing tool. Misuse can result in criminal prosecution. Use responsibly.