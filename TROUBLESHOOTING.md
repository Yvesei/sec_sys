# Troubleshooting and Setup Guide

## What We Fixed

The project now properly generates and logs HTTP access requests in Common Log Format (CLF) that can be parsed by Logstash and viewed in Kibana.

### Changes Made:

1. **HTTP Log Generator (`scripts/http_log_generator.py`)**
   - New utility module that generates properly formatted HTTP access logs
   - Logs in Common Log Format: `IP - USER [TIMESTAMP] "METHOD PATH HTTP/VERSION" CODE BYTES "REFERRER" "USER_AGENT"`
   - Works both in Docker containers and on the host machine

2. **Normal Scenarios Script (`scripts/normal_scenarios.py`)**
   - Updated to log every HTTP request made to Jenkins
   - Each legitimate request generates a log entry that Logstash can parse
   - Includes: login, dashboard view, job listing, job viewing, build triggering, etc.

3. **Attack Scenarios Script (`scripts/attack_scenarios.py`)**
   - Updated to log every attack attempt with proper HTTP codes
   - Generates logs for: brute force, path traversal, script console, API enumeration, DoS, unauthorized access
   - Each attack generates realistic HTTP responses (401, 403, 400) that Logstash tags appropriately

4. **Logstash Pipeline (`docker/logstash/pipeline/jenkins.conf`)**
   - Added debug stdout output to see logs being processed
   - Properly parses Common Log Format entries
   - Extracts and tags important security-relevant fields

5. **Jenkins Configuration (`docker/jenkins/init.groovy.d/01-configure-jenkins.groovy`)**
   - Enhanced to set up Jetty HTTP access logging
   - Configured multiple log handlers for comprehensive logging

6. **Quick Test Generator (`scripts/generate_test_logs_quick.py`)**
   - New script to quickly generate 44 sample logs (10 normal + 34 attacks)
   - Perfect for testing Kibana setup without running full demo
   - Generates realistic attack patterns

---

## Complete Setup Steps

### Step 1: Generate Test Logs

Generate sample test logs that demonstrate normal and attack traffic:

```bash
python3 scripts/generate_test_logs_quick.py
```

This creates 44 sample HTTP access logs in Common Log Format at `~/.jenkins-security-logs/http_access.log`

### Step 2: Start Docker Services

```bash
cd docker
docker-compose up -d
```

Wait 2-3 minutes for services to start. Status check:

```bash
docker-compose ps
```

You should see all 5 containers running: jenkins, elasticsearch, logstash, kibana, filebeat.

### Step 3: Copy Test Logs to Jenkins

Once Jenkins container is running, copy the test logs so Filebeat can find them:

```bash
docker cp ~/.jenkins-security-logs/http_access.log jenkins:/var/jenkins_home/logs/
```

Filebeat should immediately pick up these logs and forward them to Logstash.

### Step 4: Verify Logs in Kibana

Open Kibana: **http://localhost:5601**

1. Go to **Management → Index Patterns**
2. Click **Create Index Pattern**
3. Index pattern name: `jenkins-logs-*`
4. Timestamp field: `@timestamp`
5. Click **Create Index Pattern**
6. Go to **Discover**
7. Select `jenkins-logs-*` from the dropdown
8. You should now see 44 log entries!

### Step 5: Verify Log Fields

In Kibana Discover, you should see fields like:
- `client_ip`: Client IP address (127.0.0.1 for normal, 192.168.1.x for attacks)
- `http_method`: HTTP method (GET, POST)
- `request_path`: Request URI path
- `response_code`: HTTP status code (200, 401, 403, etc.)
- `bytes`: Response size
- `tags`: Security tags (http_error, authentication_failure, path_traversal_attempt, etc.)
- `user_agent`: Browser/client information
- `referrer`: HTTP Referrer header

### Step 6: Run Full Demo (Optional)

Once you've verified logs work with test data, run the full demo:

```bash
./run.sh
# Select option 5: Run full demo
```

This will:
1. Generate realistic normal traffic (login, job viewing, builds)
2. Generate security attacks (brute force, path traversal, DoS)
3. All requests are logged in HTTP access logs
4. View results in Kibana

---

## Log Format Explanation

### Common Log Format (CLF)

```
IP - USERNAME [TIMESTAMP] "METHOD PATH HTTP/VERSION" CODE BYTES "REFERRER" "USER_AGENT"
```

Example:

```
127.0.0.1 - admin [11/Feb/2026:13:12:38 +0000] "POST /job/sample-build-job/build HTTP/1.1" 201 100 "http://localhost:8080/" "Mozilla/5.0"
```

### Logstash Parsing

Logstash extracts these fields automatically:
- `client_ip`: 127.0.0.1
- `auth`: admin (user who made the request)
- `timestamp`: 11/Feb/2026:13:12:38 +0000
- `http_method`: POST
- `request_path`: /job/sample-build-job/build
- `http_version`: 1.1
- `response_code`: 201
- `bytes`: 100
- `referrer`: http://localhost:8080/
- `user_agent`: Mozilla/5.0

### Smart Tagging

Logstash automatically tags logs with security-relevant information:
- `path_traversal_attempt`: If path contains `../` or `..\\`
- `script_console_access`: If path contains `/script`
- `api_access`: If path contains `/api/`
- `authentication_failure`: If response code is 401 or 403
- `http_error`: If response code >= 400

---

## Troubleshooting

### Issue: No logs in Kibana

**Solution 1: Check Docker containers are running**
```bash
docker-compose ps
# All 5 containers should show "Up"
```

**Solution 2: Check Filebeat is reading logs**
```bash
docker logs filebeat
# Should show "logs written to Elasticsearch" messages
```

**Solution 3: Check Elasticsearch has indices**
```bash
curl http://localhost:9200/_cat/indices?v
# Should show jenkins-logs-* indices
```

**Solution 4: Copy test logs to Jenkins**
```bash
# Generate test logs
python3 scripts/generate_test_logs_quick.py

# Copy to Jenkins
docker cp ~/.jenkins-security-logs/http_access.log jenkins:/var/jenkins_home/logs/

# Wait 30 seconds and refresh Kibana
```

### Issue: Index pattern shows "0 fields"

**Solution:** Wait 1-2 minutes for Filebeat to ingest logs, then reload the index pattern:
1. Go to **Management → Index Patterns**
2. Click the `jenkins-logs-*` pattern
3. Click **Refresh field list** (circular arrow icon)

### Issue: Elasticsearch won't start (Linux only)

**Solution:** Increase virtual memory:
```bash
# Temporary
sudo sysctl -w vm.max_map_count=262144

# Permanent
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
```

### Issue: Jenkins logs not being generated during demo

**Reason:** The HTTP log generator creates logs during the scenario scripts. Make sure you're running:
```bash
python3 scripts/normal_scenarios.py
python3 scripts/attack_scenarios.py
```

### Issue: Logstash not processing logs

**Debug Steps:**
1. Check Logstash is running: `docker logs logstash | head -50`
2. Look for "pipeline started successfully" message
3. Check Filebeat logs: `docker logs filebeat`
4. Restart if needed: `docker-compose restart logstash`

---

## Querying Logs in Kibana

### View All Logs
In Discover, leave the search empty or use:
```
*
```

### Find Failed Login Attempts
```
response_code: 401
```

### Find Path Traversal Attacks
```
tags: path_traversal_attempt
```

### Find Script Console Access
```
tags: script_console_access
```

### Find API Enumeration
```
tags: api_access
```

### Find High-Rate Attacks (Same IP, many requests)
```
client_ip: 192.168.1.*
```

### Find Specific Attack Pattern
```
response_code: (401 OR 403) AND client_ip: 192.168.1.100
```

### Find Brute Force (Multiple 401s from same IP)
In Dashboard, add a search that groups by `client_ip` and counts `response_code: 401`:
```
response_code: 401 | stats count by client_ip
```

---

## Log Generation Scripts

### For Normal Traffic

```bash
python3 scripts/normal_scenarios.py
```

**What it does:**
- Logs in as admin
- Views dashboard
- Lists jobs
- Views job details
- Triggers builds
- Checks build status
- Each action generates an HTTP log entry

### For Attack Traffic

```bash
python3 scripts/attack_scenarios.py
```

**What it does:**
- Brute force login (5+ failed login attempts)
- Credential stuffing (multiple username attempts)
- Path traversal (../../etc/passwd attempts)
- Script console exploitation (/script endpoint)
- API enumeration (rapid API requests)
- DoS build triggering (20+ build triggers)
- Unauthorized admin access (accessing restricted pages)
- Each attempt generates an HTTP log entry with attack-appropriate response codes

### For Quick Testing

```bash
python3 scripts/generate_test_logs_quick.py
```

**What it does:**
- Generates 44 sample logs instantly
- 10 normal user requests
- 34 different attack attempts
- Perfect for testing Kibana without full demo

---

## Additional Notes

### Log File Locations

**In Docker:**
- Jenkins logs: `/var/jenkins_home/logs/http_access.log`
- Picked up by Filebeat: `jenkins_home` volume
- Sent to Logstash: Port 5044

**On Host:**
- Test logs: `~/.jenkins-security-logs/http_access.log`
- Format: Common Log Format (CLF)

### Log Retention

- Elasticsearch default: indexes by date (jenkins-logs-YYYY.MM.dd)
- Each day gets a new index
- Logs persist in Docker volumes
- To clear: `docker-compose down -v`

### Production Notes

This setup is intentionally insecure for testing:
- Filebeat → Logstash: No authentication
- Logstash → Elasticsearch: No SSL/Auth
- Kibana: No authentication
- Jenkins: CSRF disabled

For production, enable:
- SSL/TLS for all connections
- Authentication on Elasticsearch
- RBAC on Kibana
- Jenkins security hardening

---

## Expected Results

Once properly set up, in Kibana Discover you should see:

**Normal Traffic Logs:**
```
127.0.0.1 - admin [TIME] "GET / HTTP/1.1" 200 8234
127.0.0.1 - admin [TIME] "GET /api/json HTTP/1.1" 200 5234
127.0.0.1 - admin [TIME] "POST /job/sample-build-job/build HTTP/1.1" 201 100
```

**Attack Logs:**
```
192.168.1.100 - - [TIME] "GET /login HTTP/1.1" 401 1234
192.168.1.100 - - [TIME] "GET /../../../etc/passwd HTTP/1.1" 400 342
192.168.1.100 - - [TIME] "POST /script HTTP/1.1" 403 456
192.168.1.200 - attacker [TIME] "POST /job/sample-build-job/build HTTP/1.1" 201 100
```

All logs should have:
- Proper timestamps (@timestamp field)
- Extracted HTTP method/path/code
- Security tags for attacks
- Client IP and user information
- Bytes sent
- User agent and referrer

---

## Support

If you still have issues:

1. Check all containers are running: `docker-compose ps`
2. View Logstash debug output: `docker logs logstash`
3. View Filebeat output: `docker logs filebeat`
4. Verify logs exist in Jenkins: `docker exec jenkins ls -la /var/jenkins_home/logs/`
5. Generate test logs and copy manually: `python3 scripts/generate_test_logs_quick.py && docker cp ~/.jenkins-security-logs/http_access.log jenkins:/var/jenkins_home/logs/`
