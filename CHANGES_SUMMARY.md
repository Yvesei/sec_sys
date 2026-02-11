# Summary of Changes - Jenkins Security Logs Fix

## Problem

- No logs visible in Kibana
- Jenkins not generating enough HTTP access logs
- Need detailed HTTP request data in logs for security analysis

## Root Cause

Jenkins doesn't generate HTTP access logs in Common Log Format (CLF) by default. Logstash expects CLF format with specific fields like IP, method, path, response code, etc.

## Solution

Created a comprehensive HTTP logging system that:
1. **Generates Common Log Format entries** for every HTTP request
2. **Integrates with Python scripts** to log all normal and attack scenarios
3. **Works both in containers and on host** for testing/debugging

---

## New Files Created

### 1. `scripts/http_log_generator.py`
- **Purpose**: Generate proper HTTP access logs in Common Log Format
- **Usage**: Imported by normal_scenarios.py and attack_scenarios.py
- **Log Format**: `IP - USER [TIMESTAMP] "METHOD PATH HTTP/VERSION" CODE BYTES "REFERRER" "USER_AGENT"`
- **Features**:
  - Works in Docker containers (`/var/jenkins_home/logs/`)
  - Works on host machine (`~/.jenkins-security-logs/`)
  - Supports normal and attack request logging
  - Automatic field enrichment

### 2. `scripts/generate_test_logs_quick.py`
- **Purpose**: Quickly generate 44 sample logs for testing
- **Usage**: `python3 scripts/generate_test_logs_quick.py`
- **Output**: 10 normal + 34 attack logs instantly
- **Benefit**: Test Kibana setup without running full demo

### 3. `TROUBLESHOOTING.md`
- **Purpose**: Comprehensive troubleshooting guide
- **Contents**: Setup steps, log format explanation, queries, debugging

---

## Modified Files

### 1. `scripts/normal_scenarios.py`
**Changed**: Added HTTP logging to all methods
```python
# Before: Just made requests
response = self.session.get(f"{JENKINS_URL}/api/json")

# After: Makes request AND logs it
response = self.session.get(f"{JENKINS_URL}/api/json")
HTTPLogGenerator.log_normal_request(
    http_method="GET",
    request_path="/api/json",
    response_code=response.status_code,
    bytes_sent=len(response.content)
)
```

**What logs are generated**:
- User login attempts → 200 OK
- Dashboard views → 200 OK
- Job listings → 200 OK
- Build triggering → 201 Created
- Each visible in Kibana with client IP 127.0.0.1

### 2. `scripts/attack_scenarios.py`
**Changed**: Added HTTP logging to all attack methods
```python
# Each attack method now logs attempts with attack-appropriate codes
HTTPLogGenerator.log_attack_request(
    http_method="GET",
    request_path="/login",
    response_code=401,  # Unauthorized
    client_ip=ATTACKER_IP,
    attack_type="brute_force"
)
```

**What logs are generated**:
- Brute force → 401 Unauthorized (5+ attempts)
- Path traversal → 400 Bad Request
- Script console → 403 Forbidden
- API enumeration → 403 Forbidden
- DoS → 201 Created (but rapid-fire)
- All visible in Kibana with attacker IP 192.168.1.x

### 3. `docker/logstash/pipeline/jenkins.conf`
**Changed**: Added stdout debug output
```ruby
output {
  elasticsearch { ... }
  stdout {
    codec => rubydebug
  }
}
```
**Benefit**: See logs in `docker logs logstash` for debugging

### 4. `docker/jenkins/init.groovy.d/01-configure-jenkins.groovy`
**Changed**: Enhanced Jetty HTTP logging configuration
**Purpose**: Enable Jenkins HTTP access logging (fallback if CLF not available)

---

## How to Use

### Quick Start (Test Mode)
```bash
# 1. Generate test logs
python3 scripts/generate_test_logs_quick.py

# 2. Start Docker
cd docker
docker-compose up -d

# 3. Copy logs to Jenkins
docker cp ~/.jenkins-security-logs/http_access.log jenkins:/var/jenkins_home/logs/

# 4. Open Kibana
# http://localhost:5601
# Create index pattern: jenkins-logs-*
# View in Discover tab
```

### Full Demo
```bash
./run.sh
# Select option 5: Run full demo
```

This runs:
1. Normal traffic (generates 100+ normal logs)
2. Attack traffic (generates 50+ attack logs)
3. All automatically logged and visible in Kibana

---

## Log Details

### Common Log Format
```
CLIENT_IP - USERNAME [TIMESTAMP] "HTTP_METHOD REQUEST_PATH HTTP/VERSION" STATUS_CODE BYTES_SENT "REFERRER" "USER_AGENT"
```

### Example Logs

**Normal User**:
```
127.0.0.1 - admin [11/Feb/2026:13:12:38 +0000] "GET /api/json HTTP/1.1" 200 5234 "http://localhost:8080/" "Mozilla/5.0"
127.0.0.1 - admin [11/Feb/2026:13:12:39 +0000] "POST /job/sample-build-job/build HTTP/1.1" 201 100 "-" "curl/7.68.0"
```

**Attacker**:
```
192.168.1.100 - - [11/Feb/2026:13:12:40 +0000] "GET /login HTTP/1.1" 401 1234 "-" "python-requests/2.31.0"
192.168.1.100 - - [11/Feb/2026:13:12:41 +0000] "GET /../../../etc/passwd HTTP/1.1" 400 342 "-" "curl/7.68.0"
192.168.1.100 - - [11/Feb/2026:13:12:42 +0000] "POST /script HTTP/1.1" 403 456 "-" "Mozilla/5.0"
```

### Logstash Extracts

From each log, Logstash automatically extracts:
```json
{
  "client_ip": "127.0.0.1",          // IP address
  "auth": "admin",                      // Username
  "@timestamp": "2026-02-11T...",    // Standardized timestamp
  "http_method": "GET",                // GET, POST, etc.
  "request_path": "/api/json",        // API path
  "http_version": "1.1",              // HTTP version
  "response_code": 200,               // Status code
  "bytes": 5234,                      // Response size
  "referrer": "http://localhost:8080/",  // Referrer
  "user_agent": "Mozilla/5.0",        // Client info
  "tags": ["http_success"]            // Security tags
}
```

### Security Tags

Logstash automatically adds tags:
- `http_error`: response_code >= 400
- `authentication_failure`: response_code 401 or 403
- `path_traversal_attempt`: request_path contains `../`
- `script_console_access`: request_path contains `/script`
- `api_access`: request_path contains `/api/`
- `sensitive_endpoint`: access to /configure, /manage, etc.
- Custom tags from attack_type parameter

---

## Verification Steps

### 1. Containers Running
```bash
docker-compose ps
# All 5 should show "Up"
```

### 2. Elasticsearch Indices
```bash
curl http://localhost:9200/_cat/indices?v
# Should show: jenkins-logs-YYYY.MM.dd
```

### 3. Filebeat Logs
```bash
docker logs filebeat | tail -20
# Should show "logs written to Elasticsearch" messages
```

### 4. Logstash Processing
```bash
docker logs logstash | tail -20
# Should show parsed log events being sent to Elasticsearch
```

### 5. Kibana Discovery
- Open http://localhost:5601
- Go to Discover
- Index pattern: jenkins-logs-*
- Should see log entries with all extracted fields

---

## Important Notes

1. **Log Location in Docker**: `/var/jenkins_home/logs/http_access.log`
2. **Log Location on Host**: `~/.jenkins-security-logs/http_access.log`
3. **Filebeat watches**: Jenkins home volume with Logstash forwarding
4. **Logstash parses**: Common Log Format and extracts security-relevant fields
5. **Elasticsearch indexes**: By date (YYYY.MM.dd) for easy rotation
6. **Kibana visualizes**: All extracted fields and allows querying

---

## Example Kibana Queries

```
# Find failed logins
response_code: 401

# Find path traversal attempts
tags: path_traversal_attempt

# Find script console access
tags: script_console_access

# Find all attacks from specific attacker
client_ip: 192.168.1.100

# Find high-error-rate IPs
response_code: [400 TO 599]
| stats count by client_ip

# Find DoS patterns
response_code: 201 AND request_path: */build
| stats count by client_ip

# Find API enumeration
tags: api_access
| stats dc(request_path) by client_ip
```

---

## Next Steps

1. Run `python3 scripts/generate_test_logs_quick.py` to create test logs
2. Start Docker: `cd docker && docker-compose up -d`
3. Copy logs: `docker cp ~/.jenkins-security-logs/http_access.log jenkins:/var/jenkins_home/logs/`
4. Open Kibana and create index pattern
5. View logs in Discover tab
6. Run attack/normal scenarios to generate live logs

See `TROUBLESHOOTING.md` for detailed setup and debugging instructions.
