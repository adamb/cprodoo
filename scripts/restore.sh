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

# Start postgres
docker-compose up -d postgres
sleep 5

# Detect container names
if docker ps --format '{{.Names}}' | grep -q "cprodoo-postgres-1"; then
    ODOO_CONTAINER="cprodoo-odoo-1"
    POSTGRES_CONTAINER="cprodoo-postgres-1"
else
    ODOO_CONTAINER="cprodoo_postgres_1"
    POSTGRES_CONTAINER="cprodoo_postgres_1"
fi

# Restore database
docker exec -i $POSTGRES_CONTAINER psql -U odoo -d postgres -c "DROP DATABASE IF EXISTS cpr;"
docker exec -i $POSTGRES_CONTAINER psql -U odoo -d postgres -c "CREATE DATABASE cpr OWNER odoo;"
docker exec -i $POSTGRES_CONTAINER psql -U odoo -d cpr < $TEMP_DIR/$BACKUP_DIR/cpr.sql

# Start all containers
docker-compose up -d
sleep 5

# Detect odoo container name again (in case it changed)
if docker ps --format '{{.Names}}' | grep -q "cprodoo-odoo-1"; then
    ODOO_CONTAINER="cprodoo-odoo-1"
else
    ODOO_CONTAINER="cprodoo_odoo_1"
fi

# Restore filestore
docker cp $TEMP_DIR/$BACKUP_DIR/filestore/. $ODOO_CONTAINER:/var/lib/odoo/filestore/

# Copy .env
cp $TEMP_DIR/$BACKUP_DIR/.env .env

# Cleanup
rm -rf $TEMP_DIR

echo "Restore complete!"
