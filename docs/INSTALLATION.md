# Installation Guide

## System Requirements

### Minimum Requirements
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Disk**: 10 GB free space
- **OS**: Linux, macOS, or Windows with WSL2

### Software Requirements
- Docker 20.10+
- Docker Compose 2.0+
- Python 3.8+
- pip3

## Step-by-Step Installation

### 1. Install Docker

#### Ubuntu/Debian
```bash
# Update package index
sudo apt-get update

# Install dependencies
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### macOS
```bash
# Download and install Docker Desktop from:
# https://docs.docker.com/desktop/install/mac-install/

# Or use Homebrew
brew install --cask docker
```

#### Windows
1. Enable WSL2
2. Download Docker Desktop from: https://docs.docker.com/desktop/install/windows-install/
3. Install and restart

### 2. Install Docker Compose

Docker Compose is now included with Docker Desktop. For standalone installation:

```bash
# Linux
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. Install Python 3

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip
```

#### macOS
```bash
brew install python3
```

#### Windows (WSL2)
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip
```

### 4. Verify Installation

```bash
# Check Docker
docker --version
# Expected: Docker version 20.10.x or higher

# Check Docker Compose
docker-compose --version
# Expected: Docker Compose version 2.x.x or higher

# Check Python
python3 --version
# Expected: Python 3.8.x or higher

# Check pip
pip3 --version
# Expected: pip 20.x.x or higher
```

### 5. Clone or Extract the Project

```bash
# If from git
git clone <repository-url>
cd jenkins-security-logs

# If from archive
unzip jenkins-security-logs.zip
cd jenkins-security-logs
```

### 6. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

### 7. Configure System Settings (Linux Only)

For Elasticsearch to work properly:

```bash
# Increase virtual memory
sudo sysctl -w vm.max_map_count=262144

# Make it permanent
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
```

### 8. Make Scripts Executable

```bash
chmod +x run.sh
chmod +x scripts/*.py
```

## Quick Start

### Option 1: Interactive Menu (Recommended)

```bash
./run.sh
```

Select option 5 for full demonstration.

### Option 2: Manual Steps

```bash
# Start all services
cd docker
docker-compose up -d

# Wait for services to be ready (2-3 minutes)
sleep 180

# Setup Kibana
cd ..
python3 scripts/setup_kibana.py

# Generate normal traffic
python3 scripts/normal_scenarios.py

# Generate attack traffic
python3 scripts/attack_scenarios.py
```

## Verifying Installation

### Check Service Status

```bash
# View running containers
docker ps

# Expected output: 5 containers running
# - jenkins
# - elasticsearch
# - logstash
# - kibana
# - filebeat
```

### Access Web Interfaces

1. **Jenkins**: http://localhost:8080
   - Login with: admin / admin123

2. **Kibana**: http://localhost:5601
   - No authentication required

3. **Elasticsearch**: http://localhost:9200
   - Should return cluster information

## Troubleshooting

### Services Don't Start

```bash
# View logs
docker-compose logs

# Restart services
docker-compose restart
```

### Elasticsearch Won't Start

```bash
# Check virtual memory setting
sysctl vm.max_map_count

# Should be at least 262144
# If not, set it:
sudo sysctl -w vm.max_map_count=262144
```

### Port Conflicts

If you get port conflict errors:

```bash
# Check what's using the ports
sudo lsof -i :8080  # Jenkins
sudo lsof -i :5601  # Kibana
sudo lsof -i :9200  # Elasticsearch

# Stop conflicting services or modify docker-compose.yml
```

### Jenkins Takes Long to Start

Jenkins may take 2-3 minutes to fully initialize. Wait and check:

```bash
docker logs jenkins -f
```

Look for: "Jenkins is fully up and running"

### Logs Not Appearing in Kibana

1. Check Filebeat is running:
```bash
docker logs filebeat
```

2. Verify Logstash is processing:
```bash
docker logs logstash
```

3. Check Elasticsearch indices:
```bash
curl http://localhost:9200/_cat/indices?v
```

Should see `jenkins-logs-*` indices.

### Python Script Errors

Make sure dependencies are installed:
```bash
pip3 install -r requirements.txt
```

## Uninstallation

### Remove All Containers and Data

```bash
cd docker
docker-compose down -v

# This will:
# - Stop all containers
# - Remove all containers
# - Remove all volumes (data will be lost)
```

### Remove Docker Images

```bash
docker rmi jenkins/jenkins:lts
docker rmi docker.elastic.co/elasticsearch/elasticsearch:8.11.0
docker rmi docker.elastic.co/logstash/logstash:8.11.0
docker rmi docker.elastic.co/kibana/kibana:8.11.0
docker rmi docker.elastic.co/beats/filebeat:8.11.0
```

## Next Steps

After installation:

1. Access Kibana and explore the Discover page
2. Run normal scenarios to generate baseline traffic
3. Run attack scenarios to generate security events
4. Create visualizations and dashboards
5. Implement detection rules

See [README.md](../README.md) for detailed usage instructions.
