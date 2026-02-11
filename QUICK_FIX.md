# QUICK START - Fix for No Kibana Logs Issue

## The Problem Was
- Jenkins doesn't generate HTTP access logs by default
- Logstash expects Common Log Format which Jenkins/Jetty doesn't produce
- No data → No fields in Kibana → Empty index pattern

## The Solution
- Created `HTTPLogGenerator` to produce proper HTTP logs
- Updated scripts to log every request made to Jenkins
- Both normal and attack scenarios now generate detailed logs

---

## Get Log Data in Kibana Right Now (5 minutes)

### Step 1: Generate Test Logs
```bash
cd /Users/yvesei/Downloads/jenkins-security-logs
python3 scripts/generate_test_logs_quick.py
```
✅ Creates 44 sample logs (10 normal + 34 attacks)

### Step 2: Start Docker
```bash
cd docker
docker-compose up -d
```
⏳ Wait 2-3 minutes for all services to start

### Step 3: Copy Logs to Jenkins
```bash
docker cp ~/.jenkins-security-logs/http_access.log jenkins:/var/jenkins_home/logs/
```
✅ Filebeat will automatically pick them up

### Step 4: Open Kibana
Go to **http://localhost:5601**

1. Click **Menu** → **Management**
2. Click **Kibana** → **Index Patterns**
3. Click **Create Index Pattern**
4. Type: **jenkins-logs-***
5. Timestamp field: **@timestamp**
6. Click **Create Index Pattern**
7. Click **Discover**
8. Select **jenkins-logs-*** 
9. 🎉 You should see 44 logs!

---

## What You'll See in Kibana

| Field | Example | Meaning |
|-------|---------|---------|
| `client_ip` | 127.0.0.1 | User IP (normal) or 192.168.1.x (attacker) |
| `http_method` | GET, POST | HTTP method used |
| `request_path` | /api/json, /script | URI path requested |
| `response_code` | 200, 401, 403 | HTTP status code |
| `auth` | admin, attacker | Username |
| `bytes` | 5234 | Response size |
| `tags` | path_traversal_attempt | Security tags |

---

## Common Kibana Queries

```
# Find failed logins
response_code: 401

# Find path traversal attempts  
tags: path_traversal_attempt

# Find script console access
tags: script_console_access

# Find attacker IP activities
client_ip: 192.168.1.100

# Find all HTTP errors
response_code: [400 TO 599]
```

---

## Files Changed / Created

| File | Change | Purpose |
|------|--------|---------|
| `scripts/http_log_generator.py` | NEW | Generate HTTP access logs in Common Log Format |
| `scripts/generate_test_logs_quick.py` | NEW | Quickly create 44 test logs |
| `scripts/normal_scenarios.py` | UPDATED | Now logs every request made |
| `scripts/attack_scenarios.py` | UPDATED | Now logs every attack attempt |
| `docker/logstash/pipeline/jenkins.conf` | UPDATED | Added debug output |
| `TROUBLESHOOTING.md` | NEW | Full troubleshooting guide |
| `CHANGES_SUMMARY.md` | NEW | Detailed change summary |

---

## What Happens in Full Demo

```bash
./run.sh
# Select option 5: Run full demo
```

Generates:
- ✅ 100+ normal user logs
  - Login attempts
  - Dashboard views
  - Job operations
  - Build triggers
- ✅ 50+ attack logs  
  - Brute force (5+ 401s)
  - Path traversal (400s)
  - Script console (403s)
  - API enumeration (10+ 403s)
  - DoS build spam (20+ 201s)
  - Unauthorized access (403s)
- ✅ All visible in Kibana with proper tags

---

## Troubleshooting

### No logs appearing?

1. **Check containers running:**
   ```bash
   docker-compose ps
   # All 5 should say "Up"
   ```

2. **Check logs were copied:**
   ```bash
   docker exec jenkins ls -la /var/jenkins_home/logs/
   # Should show http_access.log
   ```

3. **Check Filebeat picked them up:**
   ```bash
   docker logs filebeat | grep "processed"
   ```

4. **Check Elasticsearch has data:**
   ```bash
   curl http://localhost:9200/_cat/indices?v
   # Should show jenkins-logs-* indices
   ```

5. **Refresh Kibana index pattern:**
   - Go to Management → Index Patterns
   - Click jenkins-logs-*
   - Click refresh icon (↻)

### Still no data?

Manually regenerate and copy test logs:
```bash
python3 scripts/generate_test_logs_quick.py
docker cp ~/.jenkins-security-logs/http_access.log jenkins:/var/jenkins_home/logs/
# Wait 30 seconds
# Refresh Kibana
```

---

## Key Facts

✅ **Logs are in Common Log Format (CLF)**
```
IP - USER [TIME] "METHOD PATH HTTP/VERSION" CODE BYTES "REFERRER" "USER_AGENT"
```

✅ **Logstash automatically extracts fields**
- client_ip, auth, http_method, request_path, response_code, bytes, etc.

✅ **Security tags automatically added**
- path_traversal_attempt, script_console_access, api_access, authentication_failure, etc.

✅ **Works in both containers and on host**
- Container: `/var/jenkins_home/logs/http_access.log`
- Host: `~/.jenkins-security-logs/http_access.log`

✅ **Indexes by date for easy rotation**
- Separate index for each day: jenkins-logs-2026.02.11, etc.

---

## Log Examples

### Normal User Log
```
127.0.0.1 - admin [11/Feb/2026:13:12:38 +0000] "GET /api/json HTTP/1.1" 200 5234
```

### Brute Force Attack Log  
```
192.168.1.100 - - [11/Feb/2026:13:12:40 +0000] "GET /login HTTP/1.1" 401 1234
```

### Path Traversal Attack Log
```
192.168.1.100 - - [11/Feb/2026:13:12:41 +0000] "GET /../../../etc/passwd HTTP/1.1" 400 342
```

### Script Console Attack Log
```
192.168.1.100 - - [11/Feb/2026:13:12:42 +0000] "POST /script HTTP/1.1" 403 456
```

---

## Summary

You now have:
- ✅ Proper HTTP access logging in Common Log Format
- ✅ Automatic log generation with normal and attack scenarios
- ✅ Smart Logstash parsing with security tags
- ✅ Full data visibility in Kibana
- ✅ Quick test generator for verification
- ✅ Comprehensive troubleshooting guide

**Next step:** Follow the 4 steps above to get logs in Kibana!

For more details, see:
- `TROUBLESHOOTING.md` - Full setup and debugging guide
- `CHANGES_SUMMARY.md` - Detailed change documentation
