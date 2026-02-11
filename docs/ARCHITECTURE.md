# Technical Architecture

## Overview

This document provides detailed technical information about the Jenkins Security Log Analysis project architecture.

## System Components

### 1. Jenkins (Application Layer)

**Image**: `jenkins/jenkins:lts`  
**Ports**: 8080 (HTTP), 50000 (Agent)  

**Configuration**:
- Runs as root to access Docker socket
- CSRF protection disabled for testing
- Setup wizard skipped via Groovy scripts
- Sample jobs pre-created

**Initialization Scripts**:
- `01-configure-jenkins.groovy`: Sets up security realm, creates admin user
- `02-create-sample-jobs.groovy`: Creates sample CI/CD jobs

**Log Files**:
- Access logs: `/var/jenkins_home/logs/access.log`
- Application logs: `/var/jenkins_home/logs/jenkins.log`
- Audit logs: `/var/jenkins_home/logs/audit.log`

### 2. Filebeat (Log Collection)

**Image**: `docker.elastic.co/beats/filebeat:8.11.0`  

**Purpose**: Lightweight log shipper that monitors Jenkins log files and forwards them to Logstash.

**Configuration** (`filebeat.yml`):
```yaml
inputs:
  - type: log
    paths: [/var/jenkins_home/logs/*.log]
    fields:
      log_type: jenkins_access
      application: jenkins

output.logstash:
  hosts: ["logstash:5044"]
```

**Features**:
- Multiline support for stack traces
- Automatic field enrichment
- Docker metadata collection
- Handles log rotation

### 3. Logstash (Log Processing)

**Image**: `docker.elastic.co/logstash/logstash:8.11.0`  
**Ports**: 5044 (Beats input), 9600 (Monitoring)  

**Pipeline Stages**:

#### Input Stage
```
beats {
  port => 5044
}
```
Receives logs from Filebeat.

#### Filter Stage

**Access Log Parsing**:
```ruby
grok {
  match => {
    "message" => '%{IPORHOST:client_ip} ... %{NUMBER:response_code}'
  }
}
```

Extracts:
- Client IP address
- Authenticated user
- HTTP method
- Request path
- Response code
- Bytes transferred

**Date Parsing**:
```ruby
date {
  match => [ "timestamp", "dd/MMM/yyyy:HH:mm:ss Z" ]
  target => "@timestamp"
}
```

**Enrichment**:
- Tags HTTP errors
- Detects attack patterns
- GeoIP lookup
- Type conversions

**Attack Detection Tags**:
- `http_error`: Response code >= 400
- `authentication_failure`: 401 or 403
- `path_traversal_attempt`: `../` in URL
- `script_console_access`: `/script` endpoint
- `api_access`: `/api/` endpoint

#### Output Stage
```ruby
elasticsearch {
  hosts => ["elasticsearch:9200"]
  index => "jenkins-logs-%{+YYYY.MM.dd}"
}
```

### 4. Elasticsearch (Storage & Search)

**Image**: `docker.elastic.co/elasticsearch/elasticsearch:8.11.0`  
**Ports**: 9200 (HTTP), 9300 (Transport)  

**Configuration**:
- Single-node cluster
- Security disabled for testing
- 512MB heap size

**Index Pattern**: `jenkins-logs-YYYY.MM.dd`

**Document Structure**:
```json
{
  "@timestamp": "2025-02-12T10:30:45.000Z",
  "log_type": "jenkins_access",
  "application": "jenkins",
  "client_ip": "192.168.1.100",
  "auth": "admin",
  "http_method": "GET",
  "request_path": "/api/json",
  "response_code": 200,
  "bytes": 1234,
  "tags": ["api_access"],
  "geoip": {
    "country_name": "France",
    "city_name": "Paris",
    "location": {"lat": 48.8566, "lon": 2.3522}
  }
}
```

**Index Settings**:
- Refresh interval: 1s (real-time)
- Number of shards: 1
- Number of replicas: 0

### 5. Kibana (Visualization)

**Image**: `docker.elastic.co/kibana/kibana:8.11.0`  
**Port**: 5601  

**Configuration**:
- Connected to Elasticsearch
- Security disabled
- Default index pattern: `jenkins-logs-*`

**Features Used**:
- Discover: Log exploration
- Visualize: Chart creation
- Dashboard: Aggregated views
- Dev Tools: Query testing

## Data Flow

```
┌─────────────┐
│   Jenkins   │  1. Generates logs
│             │     - access.log
└──────┬──────┘     - jenkins.log
       │            - audit.log
       │
       ↓
┌─────────────┐
│  Filebeat   │  2. Monitors log files
│             │     - Reads new lines
└──────┬──────┘     - Adds metadata
       │
       │ (Port 5044)
       ↓
┌─────────────┐
│  Logstash   │  3. Processes logs
│             │     - Parses with Grok
└──────┬──────┘     - Enriches data
       │            - Tags patterns
       │
       │ (Port 9200)
       ↓
┌─────────────┐
│Elasticsearch│  4. Stores & indexes
│             │     - Indexes by date
└──────┬──────┘     - Makes searchable
       │
       │ (Port 5601)
       ↓
┌─────────────┐
│   Kibana    │  5. Visualizes
│             │     - Query interface
└─────────────┘     - Dashboards
```

## Network Architecture

### Docker Network: `elk`

All services communicate on bridge network `elk`:

```
jenkins         → 172.18.0.2
elasticsearch   → 172.18.0.3
logstash        → 172.18.0.4
kibana          → 172.18.0.5
filebeat        → 172.18.0.6
```

**Internal Communication**:
- Filebeat → Logstash: Port 5044
- Logstash → Elasticsearch: Port 9200
- Kibana → Elasticsearch: Port 9200

**External Access**:
- Jenkins: localhost:8080
- Kibana: localhost:5601
- Elasticsearch: localhost:9200

## Storage Architecture

### Docker Volumes

**jenkins_home**:
- Purpose: Jenkins data and configuration
- Contents: Jobs, builds, plugins, logs
- Location: `/var/jenkins_home` in container

**elasticsearch_data**:
- Purpose: Elasticsearch indices
- Contents: Log documents, index metadata
- Location: `/usr/share/elasticsearch/data` in container

**Volume Persistence**:
- Data persists across container restarts
- Lost when volumes are explicitly removed
- Can be backed up using `docker cp`

## Security Architecture (Testing Environment)

⚠️ **Warning**: This configuration is intentionally insecure for testing purposes.

**Security Measures Disabled**:
- Jenkins CSRF protection
- Jenkins SSL/TLS
- Elasticsearch authentication
- Kibana authentication
- Logstash authentication

**Why These Are Disabled**:
- Simplify attack scenario scripting
- Easy access for testing
- Focus on log analysis, not security hardening

**Production Considerations**:
- Enable authentication on all services
- Use TLS/SSL for all connections
- Implement CSRF protection
- Use API tokens instead of passwords
- Enable audit logging
- Implement network segmentation

## Scalability Considerations

### Current Configuration
- Single Elasticsearch node
- Single Logstash instance
- No load balancing

### Scaling Options

**Horizontal Scaling**:
```yaml
# Add more Logstash nodes
logstash-1:
  image: docker.elastic.co/logstash/logstash:8.11.0
  
logstash-2:
  image: docker.elastic.co/logstash/logstash:8.11.0
```

**Elasticsearch Cluster**:
```yaml
elasticsearch-1:
  environment:
    - cluster.name=jenkins-logs
    - node.name=es-1
    - discovery.seed_hosts=elasticsearch-2

elasticsearch-2:
  environment:
    - cluster.name=jenkins-logs
    - node.name=es-2
    - discovery.seed_hosts=elasticsearch-1
```

**Load Balancing**:
- HAProxy for Logstash input
- Nginx for Kibana
- Elasticsearch coordinating-only nodes

## Performance Tuning

### Elasticsearch

**Heap Size**:
```yaml
environment:
  - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
```

**Refresh Interval**:
```json
PUT /jenkins-logs-*/_settings
{
  "index": {
    "refresh_interval": "30s"
  }
}
```

### Logstash

**Pipeline Workers**:
```yaml
pipeline.workers: 4
pipeline.batch.size: 1000
```

**JVM Options**:
```yaml
environment:
  - "LS_JAVA_OPTS=-Xmx512m -Xms512m"
```

### Filebeat

**Queue Size**:
```yaml
queue.mem:
  events: 4096
  flush.min_events: 2048
```

## Monitoring & Observability

### Built-in Monitoring

**Docker Stats**:
```bash
docker stats
```

**Elasticsearch Health**:
```bash
curl http://localhost:9200/_cluster/health?pretty
```

**Logstash Stats**:
```bash
curl http://localhost:9600/_node/stats?pretty
```

### Kibana Monitoring

**Stack Monitoring**:
- Menu → Stack Monitoring
- View cluster health
- Index stats
- Node performance

### Log Locations

**Container Logs**:
```bash
docker logs jenkins
docker logs elasticsearch
docker logs logstash
docker logs kibana
docker logs filebeat
```

## Backup & Recovery

### Elasticsearch Snapshots

```bash
# Create snapshot repository
curl -X PUT "localhost:9200/_snapshot/backup" -H 'Content-Type: application/json' -d'
{
  "type": "fs",
  "settings": {
    "location": "/backups"
  }
}'

# Create snapshot
curl -X PUT "localhost:9200/_snapshot/backup/snapshot_1?wait_for_completion=true"
```

### Volume Backup

```bash
# Backup Jenkins data
docker run --rm \
  -v jenkins_home:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/jenkins_backup.tar.gz /data

# Backup Elasticsearch data
docker run --rm \
  -v elasticsearch_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/elasticsearch_backup.tar.gz /data
```

## API Reference

### Elasticsearch REST API

**Search Logs**:
```bash
curl -X GET "localhost:9200/jenkins-logs-*/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match": {
      "log_type": "jenkins_access"
    }
  }
}'
```

**Aggregation Query**:
```bash
curl -X GET "localhost:9200/jenkins-logs-*/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "by_response_code": {
      "terms": {
        "field": "response_code"
      }
    }
  }
}'
```

### Kibana API

**Create Index Pattern**:
```bash
curl -X POST "localhost:5601/api/saved_objects/index-pattern" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{
    "attributes": {
      "title": "jenkins-logs-*",
      "timeFieldName": "@timestamp"
    }
  }'
```

## Troubleshooting Guide

### Common Issues

**Issue**: Elasticsearch won't start  
**Cause**: Insufficient virtual memory  
**Solution**:
```bash
sudo sysctl -w vm.max_map_count=262144
```

**Issue**: No logs in Elasticsearch  
**Cause**: Filebeat not reading logs  
**Solution**:
```bash
# Check Filebeat logs
docker logs filebeat

# Verify Jenkins log files exist
docker exec jenkins ls -la /var/jenkins_home/logs/
```

**Issue**: High memory usage  
**Cause**: Elasticsearch heap too large  
**Solution**: Reduce heap size in docker-compose.yml

**Issue**: Slow queries in Kibana  
**Cause**: Too much data or inefficient query  
**Solution**: 
- Reduce time range
- Use more specific queries
- Add index lifecycle management

## Further Reading

- [Elastic Stack Documentation](https://www.elastic.co/guide/index.html)
- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Docker Documentation](https://docs.docker.com/)
- [MITRE ATT&CK Framework](https://attack.mitre.org/)
