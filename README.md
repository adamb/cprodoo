# CPR Odoo - Code Puerto Rico Coworking Portal

A self-hosted Odoo-based membership management system for the CPR coworking space.

## Features

- Member management with custom fields (membership type, start date, access key)
- Hot Desk membership ($250/month, annual contract, includes $150 meeting room credits)
- Public website with membership application form
- Google OAuth login (Sign in with Google)
- OCA membership extensions for enhanced membership management
- Salto access key tracking (integration stubbed)
- Stripe payment integration (stubbed)

## Requirements

- Docker
- Docker Compose
- Git (with submodule support)

## Setup

1. Clone this repository with submodules:
git clone --recurse-submodules cd cprodoo

Copied!
2. Copy `.env.example` to `.env` and fill in your credentials

3. Build and start the containers:
docker-compose build docker-compose up -d

4. Access Odoo at http://localhost:8069

5. Create a new database when prompted

6. Enable Developer Mode (Settings → Activate developer mode)

7. Install modules:
- Go to Apps → Update Apps List
- Search for and activate: "CPR Membership", "Members", "Membership Extension", "Website", "auth_oidc"

## Backup and Restore

Backup your instance:
./scripts/backup.sh

Copied!
Restore from backup:
./scripts/restore.sh backup_YYYYMMDD_HHMMSS.tar.gz

Copied!
These scripts work on both Mac and Linux (Debian).

## Project Structure

- `addons/cpr_membership/` - Custom membership module
- `addons/vertical-association/` - OCA membership modules (submodule)
- `addons/server-auth/` - OCA authentication modules (submodule)
- `scripts/` - Backup and restore scripts
- `Dockerfile` - Custom Odoo image with additional dependencies
- `docker-compose.yml` - Docker services configuration
- `.env` - Environment variables (not in git)

## Deployment

Production instance runs at https://code.pr via Cloudflare Tunnel.


## Email Delivery (Odoo + Postfix + ImprovMX)

This project does not send email directly from Odoo to ImprovMX.

Instead, we use a Postfix sidecar container as a local MTA to avoid blocking, timeouts, and relay issues inside Odoo.

Why this setup
	•	Odoo sends emails synchronously in some code paths (login, password reset, new device alerts).
	•	If the SMTP provider is slow or disconnects, Odoo requests block or fail.
	•	ImprovMX enforces strict envelope sender rules (must match the authenticated domain).
	•	Odoo is inconsistent about envelope senders (bounce@domain, <>, etc.), especially across versions.

Using Postfix as a relay solves all of this cleanly.

Architecture

Odoo  →  Postfix (plain SMTP, port 25)  →  ImprovMX (TLS + auth)

	•	Odoo talks to Postfix over the internal Docker network
	•	Postfix handles TLS, auth, retries, and relay rules
	•	ImprovMX only ever sees approved senders (info@code.pr)

Docker Compose

A Postfix service is defined in docker-compose.yml:

postfix:
  image: boky/postfix
  restart: unless-stopped
  environment:
    - RELAYHOST=[smtp.improvmx.com]:587
    - RELAYHOST_USERNAME=${IMPROVMX_SMTP_USER}
    - RELAYHOST_PASSWORD=${IMPROVMX_SMTP_PASS}
    - SMTP_USE_TLS=yes
    - ALLOWED_SENDER_DOMAINS=code.pr
    - POSTFIX_myhostname=mailrelay.code.pr
    - POSTFIX_inet_protocols=ipv4
  volumes:
    - postfix_spool:/var/spool/postfix

ImprovMX credentials are stored in .env:

IMPROVMX_SMTP_USER=info@code.pr
IMPROVMX_SMTP_PASS=...

Odoo configuration

In Odoo → Settings → Technical → Emails → Outgoing Mail Servers:
	•	SMTP Server: postfix
	•	Port: 25
	•	Encryption: None
	•	Username / Password: empty

Odoo must not talk directly to ImprovMX.

In Settings → General Settings → Emails:
	•	Default From Alias: info
	•	Bounce Alias: info
	•	Catchall Alias: info

This ensures the envelope sender is always info@code.pr.

Debugging

Watch Postfix live:

docker-compose logs -f postfix

You should see:

from=<info@code.pr>
status=sent (250 2.0.0 Email queued for delivery)

If emails fail:
	•	Check Odoo’s email queue (Settings → Technical → Emails)
	•	Check Postfix logs
	•	Clear old queues if needed:

docker exec -it cprodoo_postfix_1 postsuper -d ALL

Notes
	•	This setup intentionally avoids AWS SES.
	•	Postfix is used only as a relay, not a public mail server.
	•	No ports are exposed to the host.


## License

TBD