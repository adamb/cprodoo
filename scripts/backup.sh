#!/bin/bash
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup database
docker exec cprodoo_postgres_1 pg_dump -U odoo cpr > $BACKUP_DIR/cpr.sql

# Backup filestore
docker cp cprodoo_odoo_1:/var/lib/odoo/filestore $BACKUP_DIR/

# Copy .env
cp .env $BACKUP_DIR/

# Create tarball
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

echo "Backup created: $BACKUP_DIR.tar.gz"
