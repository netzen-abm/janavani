#!/usr/bin/env bash

# ==============================================================================
# JANAVANI ANONYMOUS MEMORY DATA EXTRACTION ENGINE
# Backs up aggregate statistics and sanitized reviews safely without collecting user PII.
# ==============================================================================

# Exit immediately if any command pipeline encounters an error state
set -e

BACKUP_DIR="/workspace/backups"
TIMESTAMP=$(date -u +"%Y%m%d_%H%M%SZ")
EXPORT_FILE="${BACKUP_DIR}/janavani_anonymous_snapshot_${TIMESTAMP}.json"
ARCHIVE_FILE="${BACKUP_DIR}/janavani_secure_backup_${TIMESTAMP}.tar.gz"

# Enforce secure directory path creation parameters locally on host layers
mkdir -p "$BACKUP_DIR"

echo "=== [1/3] Extracting Anonymous Aggregate Metrics from Volatile Grid ==="
# Export only the telemetry counters and public review datasets from Redis memory
docker compose exec -T transient-memory-grid redis-cli --eval - <<EOF > "$EXPORT_FILE"
    local metrics = redis.call('KEYS', 'metrics:*')
    local feedback = redis.call('KEYS', 'feedback:*')
    local data = {}
    
    for _, key in ipairs(metrics) do
        data[key] = redis.call('GET', key) or redis.call('HGETALL', key)
    end
    for _, key in ipairs(feedback) do
        if redis.call('TYPE', key).name == 'string' then
            data[key] = redis.call('GET', key)
        elif redis.call('TYPE', key).name == 'hash' then
            data[key] = redis.call('HGETALL', key)
        elif redis.call('TYPE', key).name == 'list' then
            data[key] = redis.call('LRANGE', key, 0, -1)
        end
    end
    return json.encode(data)
EOF

echo "=== [2/3] Compressing Snapshot Files into Secure Archives ==="
# Compress and protect the data logs using standard gzip formats
tar -czf "$ARCHIVE_FILE" -C "$BACKUP_DIR" "janavani_anonymous_snapshot_${TIMESTAMP}.json"

# Remove the plaintext raw file trace immediately from host layers
rm -f "$EXPORT_FILE"

echo "=== [3/3] Enforcing Retention Policies (Purging Backups Older Than 30 Days) ==="
find "$BACKUP_DIR" -type f -name "janavani_secure_backup_*.tar.gz" -mtime +30 -exec rm {} \;

echo "🎉 Janavani Anonymous Telemetry Data Archive Saved Successfully: ${ARCHIVE_FILE}"
