#!/bin/bash
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Detect container names (hyphen vs underscore)
if docker ps --format '{{.Names}}' | grep -q "cprodoo-odoo-1"; then
    ODOO_CONTAINER="cprodoo-odoo-1"
    POSTGRES_CONTAINER="cprodoo-postgres-1"
else
    ODOO_CONTAINER="cprodoo_odoo_1"
    POSTGRES_CONTAINER="cprodoo_postgres_1"
fi

# Backup database
docker exec $POSTGRES_CONTAINER pg_dump -U odoo cpr > $BACKUP_DIR/cpr.sql

# Backup filestore
docker cp $ODOO_CONTAINER:/var/lib/odoo/filestore $BACKUP_DIR/

# Copy .env
cp .env $BACKUP_DIR/

# Create tarball
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

echo "Backup created: $BACKUP_DIR.tar.gz"
