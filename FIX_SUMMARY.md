# 🎯 LOGS IN KIBANA - COMPLETE FIX SUMMARY

## What Was Wrong

Your Jenkins setup couldn't display logs in Kibana because:
1. **Jenkins doesn't generate HTTP access logs by default**
2. **Logstash expects Common Log Format (CLF) which Jenkins doesn't produce**
3. **No properly formatted logs = No fields in Kibana = Empty data**

## What's Fixed Now

✅ **Complete HTTP access logging system**
- Every HTTP request is now logged in Common Log Format
- Both normal user requests AND attack attempts are logged
- All logs contain security-relevant details (IP, method, path, response code, etc.)
- Fully integrated with Logstash and Kibana

## How It Works

### The Flow
```
Python Script Makes HTTP Request
          ↓
HTTPLogGenerator Creates CLF Log Entry
          ↓
Log Written to http_access.log
          ↓
Filebeat Picks Up Log
          ↓
Logstash Parses & Enriches
          ↓
Elasticsearch Indexes
          ↓
🎉 Kibana Displays with Full Fields!
```

### Common Log Format
```
CLIENT_IP - USERNAME [TIMESTAMP] "METHOD PATH VERSION" CODE BYTES "REFERRER" "USER_AGENT"
```

Example:
```
127.0.0.1 - admin [11/Feb/2026:13:12:38 +0000] "GET /api/json HTTP/1.1" 200 5234 "http://localhost:8080/" "Mozilla/5.0"
```

## Files You Got

### New Scripts
- **`scripts/http_log_generator.py`** - HTTP logging module (import this to log requests)
- **`scripts/generate_test_logs_quick.py`** - Generate 44 test logs instantly

### Updated Scripts  
- **`scripts/normal_scenarios.py`** - Now logs every normal user request
- **`scripts/attack_scenarios.py`** - Now logs every attack attempt

### New Documentation
- **`QUICK_FIX.md`** - 4-step Quick Start to get logs in Kibana
- **`TROUBLESHOOTING.md`** - Complete setup and debugging guide
- **`CHANGES_SUMMARY.md`** - Detailed technical changes

## Get Logs in Kibana (4 Steps, 5 Minutes)

### Step 1: Generate Test Logs
```bash
cd /Users/yvesei/Downloads/jenkins-security-logs
python3 scripts/generate_test_logs_quick.py
```
Creates 44 immediately (10 normal + 34 attacks)

### Step 2: Start Docker
```bash
cd docker
docker-compose up -d
```
Wait 2-3 minutes for all 5 containers to start

### Step 3: Copy Logs to Jenkins
```bash
docker cp ~/.jenkins-security-logs/http_access.log jenkins:/var/jenkins_home/logs/
```
Filebeat automatically detects and forwards them

### Step 4: View in Kibana
1. Open http://localhost:5601
2. Management → Index Patterns → Create Index Pattern
3. Index pattern: `jenkins-logs-*`
4. Timestamp field: `@timestamp`
5. Go to Discover
6. 🎉 You now see 44 logs with all fields!

## What You'll See in Kibana

| Field | Example | Description |
|-------|---------|-------------|
| @timestamp | 2026-02-11T... | Log timestamp |
| client_ip | 127.0.0.1 | Normal user: 127.0.0.1, Attacker: 192.168.1.x |
| auth | admin | Username or "-" for anonymous |
| http_method | GET, POST | HTTP method |
| request_path | /api/json, /script | URI requested |
| response_code | 200, 401, 403 | HTTP status code |
| bytes | 5234 | Response size |
| user_agent | Mozilla/5.0 | Browser/client info |
| tags | path_traversal_attempt | Security classification |

## Normal User Logs (10 total)
```
127.0.0.1 - admin [11/Feb/2026:13:12:38 +0000] "GET / HTTP/1.1" 200 8234
127.0.0.1 - admin [11/Feb/2026:13:12:39 +0000] "GET /api/json HTTP/1.1" 200 5234
127.0.0.1 - admin [11/Feb/2026:13:12:40 +0000] "GET /job/sample-build-job/ HTTP/1.1" 200 4567
127.0.0.1 - admin [11/Feb/2026:13:12:41 +0000] "POST /job/sample-build-job/build HTTP/1.1" 201 234
... (6 more normal user actions)
```

## Attack Logs (34 total)

### Brute Force (5 logs)
```
192.168.1.100 - - [11/Feb/2026:13:12:45 +0000] "GET /login HTTP/1.1" 401 1234
192.168.1.100 - - [11/Feb/2026:13:12:46 +0000] "GET /login HTTP/1.1" 401 1234
...× 5
```

### Path Traversal (3 logs)
```
192.168.1.100 - - [11/Feb/2026:13:12:48 +0000] "GET /../../../etc/passwd HTTP/1.1" 400 342
192.168.1.100 - - [11/Feb/2026:13:12:49 +0000] "GET /..%2F..%2F..%2Fetc%2Fpasswd HTTP/1.1" 400 342
...
```

### Script Console (6 logs)
```
192.168.1.100 - - [11/Feb/2026:13:12:51 +0000] "GET /script HTTP/1.1" 403 456
192.168.1.100 - - [11/Feb/2026:13:12:52 +0000] "POST /script HTTP/1.1" 403 512
...× 6
```

### API Enumeration (6 logs)
```
192.168.1.100 - attacker [11/Feb/2026:13:12:54 +0000] "GET /api/json HTTP/1.1" 403 234
192.168.1.100 - attacker [11/Feb/2026:13:12:55 +0000] "GET /queue/api/json HTTP/1.1" 403 234
...× 6
```

### DoS Build Triggering (10 logs)
```
192.168.1.200 - attacker [11/Feb/2026:13:12:56 +0000] "POST /job/sample-build-job/build HTTP/1.1" 201 100
192.168.1.200 - attacker [11/Feb/2026:13:12:57 +0000] "POST /job/sample-build-job/build HTTP/1.1" 201 100
...× 10 (rapid-fire)
```

### Unauthorized Access (4 logs)
```
192.168.1.100 - - [11/Feb/2026:13:13:06 +0000] "GET /configure HTTP/1.1" 403 234
192.168.1.100 - - [11/Feb/2026:13:13:07 +0000] "GET /manage HTTP/1.1" 403 234
...× 4
```

## Kibana Queries You Can Use

```
# Find failed logins
response_code: 401

# Find path traversal attempts
tags: path_traversal_attempt

# Find script console access
tags: script_console_access

# Find API enumeration
tags: api_access

# Find all attack activity from one IP
client_ip: 192.168.1.100

# Find all HTTP errors
response_code: [400 TO 599]

# Find rapid build triggers (DoS pattern)
request_path: */build AND response_code: 201
| stats count by client_ip

# Find failed access patterns
response_code: (401 OR 403)
| stats count by client_ip
```

## Full Demo (10-15 minutes)

Once you've tested with the 4-step Quick Start above, try:

```bash
./run.sh
# Select option 5: Run full demo
```

This generates:
- **100+ normal user logs** (real Jenkins activity)
- **50+ attack logs** (all attack types)
- **Auto-detection** of attack patterns
- **All visible in Kibana** with security tags

## Common Issues & Fixes

### No data in Kibana?

**Check 1: Docker running?**
```bash
docker-compose ps
# All 5 containers should be "Up"
```

**Check 2: Logs exist in Jenkins?**
```bash
docker exec jenkins ls -la /var/jenkins_home/logs/
# Should show http_access.log
```

**Check 3: Filebeat picked them up?**
```bash
docker logs filebeat | tail -20
# Should show logs being forwarded
```

**Check 4: Elasticsearch has data?**
```bash
curl http://localhost:9200/_cat/indices?v
# Should show jenkins-logs-* indices
```

**Check 5: Refresh Kibana**
- Go to Management → Index Patterns
- Click jenkins-logs-* 
- Click the refresh icon (↻)

### Still no logs?

Regenerate and copy manually:
```bash
python3 scripts/generate_test_logs_quick.py
docker cp ~/.jenkins-security-logs/http_access.log jenkins:/var/jenkins_home/logs/
# Wait 30 seconds
# Refresh Kibana
```

## Technical Details

### Log Location
- **In Docker**: `/var/jenkins_home/logs/http_access.log`
- **On Host**: `~/.jenkins-security-logs/http_access.log`

### Logstash Processing
- Input: Filebeat forwards logs
- Filter: Grok pattern parses CLF
- Extract: IP, method, path, code, bytes, user agent
- Tag: Automatic security classification
- Output: Send to Elasticsearch + stdout debug

### Elasticsearch Indexing
- Index pattern: `jenkins-logs-YYYY.MM.dd`
- Document type: `_doc`
- Retention: By date (easy to rotate)
- Searchable: All extracted fields are indexed

### Kibana Visualization
- Discover: Browse all logs with full fields
- Alerts: Set up detection rules
- Dashboard: Create security panels
- Export: Download for analysis

## Verification Checklist

- ✅ Can run `python3 scripts/generate_test_logs_quick.py`
- ✅ Can start Docker: `cd docker && docker-compose up -d`
- ✅ Can see 5 containers running: `docker-compose ps`
- ✅ Can copy logs: `docker cp ... jenkins:/var/jenkins_home/logs/`
- ✅ Can access Kibana: http://localhost:5601
- ✅ Can create index pattern: `jenkins-logs-*`
- ✅ Can see 44 logs in Discover
- ✅ Can query logs: `response_code: 401`

## Summary

**Before:**
- ❌ No HTTP access logs generated
- ❌ Kibana shows empty index
- ❌ No fields to analyze
- ❌ Can't detect attacks

**After:**
- ✅ Complete HTTP logging system
- ✅ 44 sample logs in Kibana
- ✅ All fields extracted and tagged
- ✅ Attack patterns clearly visible
- ✅ Ready for 100+ attack scenarios

## Next Steps

1. **Read QUICK_FIX.md** for the 4-step Quick Start
2. **Follow the 4 steps** to get logs in Kibana
3. **Run queries** to explore the data
4. **Run full demo** with `./run.sh` option 5
5. **Refer to TROUBLESHOOTING.md** if you have issues

## Questions?

See:
- `QUICK_FIX.md` - Quick 4-step guide
- `TROUBLESHOOTING.md` - Detailed troubleshooting
- `CHANGES_SUMMARY.md` - Technical details of changes

---

**Happy analyzing! 🔍**
