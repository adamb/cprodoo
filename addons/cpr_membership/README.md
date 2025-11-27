# CPR Odoo - Code Puerto Rico Coworking Portal

A self-hosted Odoo-based membership management system for the CPR coworking space.

## Features

- Member management with custom fields (membership type, start date, access key)
- Hot Desk membership ($250/month, annual contract)
- Salto access key tracking (integration stubbed)
- Stripe payment integration (stubbed)

## Requirements

- Docker
- Docker Compose

## Setup

1. Clone this repository
2. Copy `.env.example` to `.env` and fill in your credentials
3. Run `docker-compose up -d`
4. Access Odoo at http://localhost:8069
5. Create a new database when prompted
6. Enable Developer Mode (Settings → Activate developer mode)
7. Go to Apps → Update Apps List
8. Search for "CPR Membership" and activate it

## Project Structure

- `addons/cpro_membership/` - Custom membership module
- `docker-compose.yml` - Docker services configuration
- `.env` - Environment variables (not in git)

## License

TBD
