#!/bin/bash
echo "=== SIMPLE SECURITY MONITOR ==="
echo "Monitoring /var/log and application logs for security events..."

# Monitor system logs
tail -f /var/log/syslog /var/log/auth.log 2>/dev/null | \
  grep -i -E "failed|error|warning|alert|unauthorized|intrusion" &

# Monitor Docker containers
docker logs -f voting-app-vote-1 2>/dev/null | \
  grep -i -E "error|warning|alert|sql|injection|xss|attack" &

# Monitor access logs
echo "Security monitoring started. Press Ctrl+C to stop."
wait
