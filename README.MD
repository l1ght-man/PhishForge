# PhishForge

PhishForge is a small self‑hosted phishing simulation lab.  
It lets you send test phishing emails, capture credentials on a fake login page, and view results in a simple dashboard – all locally using Docker and MailHog.[web:341][web:347]

> Warning: Use PhishForge **only** on systems and mailboxes you own or have explicit permission to test. Misuse can be illegal and unethical.

---

## Features

- Email campaign sender that reads targets from `victims.csv` and sends phishing emails via MailHog.
- Landing page that records submitted credentials into a log file.
- Dashboard to view recent captured entries.
- 100% local environment using Docker Compose and MailHog (no real email is sent).[web:233][web:238]

---

## Tech stack

- Python 3  
- Flask  
- Docker & Docker Compose  
- MailHog (fake SMTP server + web UI)

---

## Project structure

```text
phishforge/
├── campaigns/
│   ├── __init__.py
│   └── app.py             # email campaign script
├── dashboard/
│   ├── __init__.py
│   └── app.py             # dashboard Flask app
├── landing/
│   ├── __init__.py
│   └── attack_surface.py  # phishing page Flask app
├── models/
│   └── __init__.py
├── templates/
│   ├── home.html
│   ├── demo.html
│   └── results.html
├── logs/                  # runtime logs (ignored by git)
├── victims.csv            # example target list
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .gitignore
```
## Getting started

- **Prerequisites :**
    • Docker and Docker Compose installed.

    • Python 3 (optional, only needed if you want to run scripts directly instead of via Docker).

```bash
git clone https://github.com/l1ght-man/phishforge.git
```
```bash
cd phishforge
```

## Configure victims

- Edit victims.csv and add one email address per line (or the format your campaign script expects), for example:
```text
alice@example.test
bob@example.test
```

## Running with Docker

- Build and start the core services (MailHog, dashboard, landing):

```bash
docker compose up --build
```
- This will start:
    • Dashboard at http://localhost:8080

    • Phishing landing page at http://localhost:3000

    • MailHog UI at http://localhost:8025 (SMTP on port 1025)
- The containers share a logs/ directory on the host for phishing_logs.txt   

## Sending a campaign

- To run the email campaign once:
```bash
docker compose run --rm campaign
```

- The campaign reads victims.csv (mounted into the container).

- Emails are delivered to MailHog, visible in the web UI at http://localhost:8025.

## Development notes

    • Flask apps listen on 0.0.0.0 inside the containers so they can be exposed on host ports.

    • The landing page writes captured credentials to logs/phishing_logs.txt.

    • The dashboard reads from the same log file to display recent entries.

- If you change Python dependencies, update requirements.txt and rebuild:

```bash
docker compose build
```

## Legal & ethical use

**PhishForge is for education and security awareness only.**

• Do not use it against people or systems without explicit permission.

• Check your local laws and your organization’s policies before running real campaigns.

• Use non‑sensitive lures and focus on learning, not shaming users.

- The authors are not responsible for any misuse of this tool.

## License

**PhishForge is released under the MIT License.**

• See the LICENSE file for details.