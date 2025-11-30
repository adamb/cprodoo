#!/bin/bash
if [ -z "$1" ]; then
    echo "Usage: ./restore.sh <backup_file.tar.gz>"
    exit 1
fi

BACKUP_FILE=$1
TEMP_DIR=$(mktemp -d)

# Extract backup
tar -xzf $BACKUP_FILE -C $TEMP_DIR
BACKUP_DIR=$(ls $TEMP_DIR)

# Stop containers
docker-compose down

# Restore database
docker-compose up -d postgres
sleep 5
docker exec -i cprodoo-postgres-1 psql -U odoo -d postgres -c "DROP DATABASE IF EXISTS cpr;"
docker exec -i cprodoo-postgres-1 psql -U odoo -d postgres -c "CREATE DATABASE cpr OWNER odoo;"
docker exec -i cprodoo-postgres-1 psql -U odoo -d cpr < $TEMP_DIR/$BACKUP_DIR/cpr.sql

# Start Odoo
docker-compose up -d odoo
sleep 5

# Restore filestore
docker cp $TEMP_DIR/$BACKUP_DIR/filestore/. cprodoo-odoo-1:/var/lib/odoo/filestore/

# Copy .env
cp $TEMP_DIR/$BACKUP_DIR/.env .env

# Cleanup
rm -rf $TEMP_DIR

echo "Restore complete!"
