# Scenario Documentation

## Normal Usage Scenarios

### 1. User Login
**Frequency**: High  
**Description**: Legitimate user authentication to Jenkins  
**Pattern**: Single successful login attempt  
**Expected Response**: HTTP 200  

### 2. Dashboard Access
**Frequency**: High  
**Description**: User views the main Jenkins dashboard  
**Pattern**: GET request to `/`  
**Expected Response**: HTTP 200  

### 3. Job Listing
**Frequency**: Medium  
**Description**: User retrieves list of all jobs  
**Pattern**: GET request to `/api/json`  
**Expected Response**: HTTP 200  

### 4. Job Viewing
**Frequency**: Medium  
**Description**: User views details of a specific job  
**Pattern**: GET request to `/job/{job_name}/`  
**Expected Response**: HTTP 200  

### 5. Build Triggering
**Frequency**: Medium  
**Description**: User triggers a build  
**Pattern**: POST request to `/job/{job_name}/build`  
**Expected Response**: HTTP 201  

### 6. Build Log Viewing
**Frequency**: Medium  
**Description**: User views console output of a build  
**Pattern**: GET request to `/job/{job_name}/{build_number}/console`  
**Expected Response**: HTTP 200  

### 7. Build Status Check
**Frequency**: High  
**Description**: User checks build status via API  
**Pattern**: GET request to `/job/{job_name}/{build_number}/api/json`  
**Expected Response**: HTTP 200  

---

## Attack Scenarios

### 1. Brute Force Login Attack
**MITRE ATT&CK**: T1110.001 - Password Guessing  
**Severity**: HIGH  
**Description**: Multiple login attempts with different passwords  

**Indicators**:
- Multiple 401 responses from same IP
- Short time intervals between attempts
- Sequential password testing

**Detection Rule**:
```kql
log_type: "jenkins_access" AND response_code: 401
| stats count by client_ip
| where count > 5
```

---

### 2. Credential Stuffing
**MITRE ATT&CK**: T1110.004 - Credential Stuffing  
**Severity**: HIGH  
**Description**: Testing leaked username:password combinations  

**Indicators**:
- Multiple different username attempts
- Systematic testing pattern
- Mix of 401 and potentially 200 responses

**Detection Rule**:
```kql
log_type: "jenkins_access" AND response_code: 401
| stats dc(auth) by client_ip
| where dc(auth) > 3
```

---

### 3. Path Traversal Attack
**MITRE ATT&CK**: T1083 - File and Directory Discovery  
**Severity**: HIGH  
**Description**: Attempting to access files outside web root  

**Indicators**:
- URLs containing `../` or `..\` sequences
- Encoded path separators (%2F, %5C)
- Attempts to access system files (/etc/passwd, etc.)

**Detection Rule**:
```kql
log_type: "jenkins_access" AND 
request_path: (*../* OR *..\\* OR *%2e%2e*)
```

---

### 4. Script Console Exploitation
**MITRE ATT&CK**: T1059.007 - Command and Scripting Interpreter  
**Severity**: CRITICAL  
**Description**: Attempting to execute code via Groovy script console  

**Indicators**:
- Access to `/script` endpoint
- POST requests to script console
- Potential code execution attempts

**Detection Rule**:
```kql
log_type: "jenkins_access" AND request_path: "/script"
```

---

### 5. API Enumeration
**MITRE ATT&CK**: T1087 - Account Discovery  
**Severity**: MEDIUM  
**Description**: Systematic scanning of API endpoints  

**Indicators**:
- Rapid sequential API requests
- Access to multiple `/api/*` endpoints
- Mix of 200, 403, and 404 responses

**Detection Rule**:
```kql
log_type: "jenkins_access" AND request_path: /api/*
| stats count by client_ip
| where count > 10
```

---

### 6. DoS via Build Triggering
**MITRE ATT&CK**: T1499 - Endpoint Denial of Service  
**Severity**: HIGH  
**Description**: Overwhelming system with excessive build requests  

**Indicators**:
- Rapid build trigger requests
- Multiple builds from same IP
- Short intervals between requests

**Detection Rule**:
```kql
log_type: "jenkins_access" AND request_path: */build
| stats count by client_ip
| where count > 10
```

---

### 7. Unauthorized Admin Access
**MITRE ATT&CK**: T1078 - Valid Accounts  
**Severity**: HIGH  
**Description**: Attempting to access admin pages without authorization  

**Indicators**:
- Access attempts to admin endpoints
- 403 responses on sensitive pages
- Unauthenticated access attempts

**Detection Rule**:
```kql
log_type: "jenkins_access" AND 
request_path: (/configure OR /manage OR /script OR /systemInfo) AND
response_code: (401 OR 403)
```

---

## Detection Thresholds

| Rule | Threshold | Time Window |
|------|-----------|-------------|
| Brute Force | 5 attempts | 5 minutes |
| API Enumeration | 10 requests | 1 minute |
| Build DoS | 10 builds | 1 minute |
| Script Console | 1 access | Immediate |
| Path Traversal | 1 attempt | Immediate |
| Admin Access | 1 attempt | Immediate |

---

## Response Procedures

### For Brute Force Attacks:
1. Block offending IP address
2. Implement rate limiting
3. Enable account lockout policy
4. Review authentication logs

### For Path Traversal:
1. Block IP immediately
2. Review web application firewall rules
3. Audit file permissions
4. Check for unauthorized file access

### For Script Console Access:
1. Disable script console if not needed
2. Restrict access to admin users only
3. Enable audit logging
4. Review executed scripts

### For DoS Attacks:
1. Implement rate limiting
2. Block offending IP
3. Scale resources if needed
4. Review system capacity

---

## Log Analysis Tips

### Finding Suspicious Patterns
```kql
# High failure rate from single IP
log_type: "jenkins_access" AND response_code >= 400
| stats count, dc(request_path) by client_ip
| where count > 20

# Unusual access times
log_type: "jenkins_access"
| where hour(@timestamp) < 6 OR hour(@timestamp) > 22

# Multiple user agents from same IP
log_type: "jenkins_access"
| stats dc(user_agent) by client_ip
| where dc(user_agent) > 3
```

### Correlation Opportunities
- Failed login followed by successful login
- API enumeration followed by targeted attack
- Multiple attack types from same IP
- Geographic anomalies in access patterns
