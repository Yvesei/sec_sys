# Quick Start Guide

Get up and running with Jenkins Security Log Analysis in 5 minutes!

## Prerequisites Check

```bash
docker --version        # Should be 20.10+
docker-compose --version # Should be 2.0+
python3 --version       # Should be 3.8+
```

If any are missing, see [INSTALLATION.md](docs/INSTALLATION.md)

## Installation in 3 Steps

### Step 1: Get the Code

```bash
cd jenkins-security-logs
```

### Step 2: Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

### Step 3: Run the Demo

```bash
./run.sh
```

Select **option 5** (Run full demo)

The script will:
1. Start all Docker services (2-3 minutes)
2. Configure Kibana
3. Generate normal traffic
4. Generate attack traffic

## What You Get

After the demo completes, you'll have:

✅ **Jenkins** running at http://localhost:8080
   - Login: admin / admin123

✅ **Kibana** running at http://localhost:5601
   - ~10,000 log events
   - Normal and attack traffic
   - Pre-configured searches

✅ **Elasticsearch** running at http://localhost:9200
   - Indexed and searchable logs

## First Steps in Kibana

### 1. Open Kibana
Navigate to http://localhost:5601

### 2. Go to Discover
Menu → Discover

### 3. Try These Queries

**View all failed logins:**
```
log_type: "jenkins_access" AND response_code: (401 OR 403)
```

**Find path traversal attempts:**
```
tags: path_traversal_attempt
```

**See script console access:**
```
tags: script_console_access
```

**Detect API enumeration:**
```
tags: api_access
```

## Quick Commands

```bash
# Start services
./run.sh  # Select option 1

# Stop services
./run.sh  # Select option 7

# View logs
./run.sh  # Select option 6

# Clean up everything
./run.sh  # Select option 8
```

## Manual Control

If you prefer manual control:

```bash
# Start services
cd docker
docker-compose up -d

# Stop services
docker-compose down

# Remove all data
docker-compose down -v
```

## Generate More Traffic

```bash
# Normal traffic
python3 scripts/normal_scenarios.py

# Attack traffic  
python3 scripts/attack_scenarios.py
```

## Common Issues

### Services won't start
```bash
# Check Docker is running
docker ps

# View logs
docker-compose logs
```

### Elasticsearch errors
```bash
# Linux only - increase virtual memory
sudo sysctl -w vm.max_map_count=262144
```

### Port conflicts
```bash
# Check what's using the ports
sudo lsof -i :8080  # Jenkins
sudo lsof -i :5601  # Kibana
sudo lsof -i :9200  # Elasticsearch
```

## Next Steps

1. **Explore the Data**
   - Go to Kibana Discover
   - Filter by attack types
   - Create time series charts

2. **Create Visualizations**
   - Analytics → Visualize
   - Build charts and graphs
   - Save your visualizations

3. **Build Dashboards**
   - Analytics → Dashboard
   - Add your visualizations
   - Create security monitoring views

4. **Implement Detection Rules**
   - Use the example queries
   - Set up alerting (requires setup)
   - Correlate multiple events

## Learn More

- [README.md](README.md) - Full project documentation
- [SCENARIOS.md](scenarios/SCENARIOS.md) - Attack details
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Technical deep dive
- [INSTALLATION.md](docs/INSTALLATION.md) - Detailed setup

## Need Help?

1. Check the logs: `docker-compose logs [service]`
2. Review documentation in `/docs`
3. Create an issue on the project repository

## Clean Up

When you're done:

```bash
./run.sh
# Select option 8 (Cleanup)
```

This removes all containers, volumes, and data.

---

Happy analyzing! 🔍
