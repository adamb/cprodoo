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

## License

TBD