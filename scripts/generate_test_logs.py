#!/usr/bin/env python3
"""
Script to generate test logs and verify the Jenkins logging pipeline.
This script will:
1. Generate sample access logs
2. Generate sample application logs  
3. Generate sample build logs
4. Verify that logs are being collected and parsed correctly
"""

import os
import time
import requests
import json
from datetime import datetime
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_sample_access_logs(log_dir="/var/jenkins_home/logs"):
    """Generate sample access logs with various HTTP requests"""
    try:
        os.makedirs(log_dir, exist_ok=True)
        access_log_path = os.path.join(log_dir, "access.log")
        
        sample_access_logs = [
            '192.168.1.100 - admin [10/Oct/2023:13:55:36 +0000] "GET / HTTP/1.1" 200 1234 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"',
            '192.168.1.101 - anonymous [10/Oct/2023:13:55:37 +0000] "POST /job/sample-build-job/build HTTP/1.1" 201 456 "http://jenkins:8080/" "curl/7.68.0"',
            '10.0.0.50 - attacker [10/Oct/2023:13:55:38 +0000] "GET /script HTTP/1.1" 403 123 "-" "Mozilla/5.0"',
            '192.168.1.102 - user1 [10/Oct/2023:13:55:39 +0000] "GET /job/sample-build-job/lastBuild/consoleText HTTP/1.1" 200 5678 "http://jenkins:8080/" "Mozilla/5.0"',
            '10.0.0.51 - scanner [10/Oct/2023:13:55:40 +0000] "GET /api/json HTTP/1.1" 200 890 "-" "Python-urllib/3.8"',
            '192.168.1.103 - admin [10/Oct/2023:13:55:41 +0000] "POST /createItem?name=new-job HTTP/1.1" 200 345 "http://jenkins:8080/" "Mozilla/5.0"',
            '10.0.0.52 - attacker [10/Oct/2023:13:55:42 +0000] "GET /../etc/passwd HTTP/1.1" 404 234 "-" "nikto/2.1.6"',
            '192.168.1.104 - user2 [10/Oct/2023:13:55:43 +0000] "GET /job/test-job/configure HTTP/1.1" 200 6789 "http://jenkins:8080/" "Mozilla/5.0"'
        ]
        
        with open(access_log_path, 'a') as f:
            for log_entry in sample_access_logs:
                f.write(log_entry + '\n')
        
        logger.info(f"Generated {len(sample_access_logs)} sample access log entries at {access_log_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate access logs: {e}")
        return False

def generate_sample_application_logs(log_dir="/var/jenkins_home/logs"):
    """Generate sample application logs"""
    try:
        os.makedirs(log_dir, exist_ok=True)
        app_log_path = os.path.join(log_dir, "jenkins.log")
        
        sample_app_logs = [
            '2023-10-10 13:55:36.123 [Jenkins initialization] INFO  jenkins.model.Jenkins - Jenkins started successfully',
            '2023-10-10 13:55:37.456 [Plugin Manager] INFO  jenkins.plugin.PluginManager - Loaded 50 plugins',
            '2023-10-10 13:55:38.789 [Security] WARNING jenkins.security.SecurityListener - Failed login attempt for user "attacker"',
            '2023-10-10 13:55:39.123 [Job Executor] INFO  hudson.model.Executor - Starting build for job sample-build-job',
            '2023-10-10 13:55:40.456 [System] ERROR jenkins.model.Jenkins - Plugin installation failed: timeout',
            '2023-10-10 13:55:41.789 [Authentication] INFO  jenkins.security.AuthenticationManager - User admin logged in successfully',
            '2023-10-10 13:55:42.123 [Job Executor] INFO  hudson.model.Executor - Build completed: SUCCESS',
            '2023-10-10 13:55:43.456 [Security] WARNING jenkins.security.SecurityListener - Multiple failed login attempts detected'
        ]
        
        with open(app_log_path, 'a') as f:
            for log_entry in sample_app_logs:
                f.write(log_entry + '\n')
        
        logger.info(f"Generated {len(sample_app_logs)} sample application log entries at {app_log_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate application logs: {e}")
        return False

def generate_sample_build_logs(log_dir="/var/jenkins_home/logs"):
    """Generate sample build logs"""
    try:
        os.makedirs(log_dir, exist_ok=True)
        build_log_path = os.path.join(log_dir, "build.log")
        
        sample_build_logs = [
            '2023-10-10 13:55:36 Starting build for job sample-build-job',
            '2023-10-10 13:55:37 [sample-build-job] Running shell script',
            '2023-10-10 13:55:38 Building project...',
            '2023-10-10 13:55:39 Compiling source code',
            '2023-10-10 13:55:40 Running unit tests',
            '2023-10-10 13:55:41 All tests passed',
            '2023-10-10 13:55:42 Build completed successfully',
            '2023-10-10 13:55:43 BUILD SUCCESS',
            '2023-10-10 13:55:44 Starting build for job test-job',
            '2023-10-10 13:55:45 Running tests...',
            '2023-10-10 13:55:46 ERROR: Test failed',
            '2023-10-10 13:55:47 BUILD FAILED'
        ]
        
        with open(build_log_path, 'a') as f:
            for log_entry in sample_build_logs:
                f.write(log_entry + '\n')
        
        logger.info(f"Generated {len(sample_build_logs)} sample build log entries at {build_log_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate build logs: {e}")
        return False

def generate_sample_audit_logs(log_dir="/var/jenkins_home/logs"):
    """Generate sample audit logs in JSON format"""
    try:
        os.makedirs(log_dir, exist_ok=True)
        audit_log_path = os.path.join(log_dir, "audit.log")
        
        sample_audit_logs = [
            {
                "timestamp": "2023-10-10T13:55:36Z",
                "user": "admin",
                "action": "login",
                "status": "success",
                "ip": "192.168.1.100",
                "resource": "/login"
            },
            {
                "timestamp": "2023-10-10T13:55:37Z", 
                "user": "attacker",
                "action": "login",
                "status": "failed",
                "ip": "10.0.0.50",
                "resource": "/login"
            },
            {
                "timestamp": "2023-10-10T13:55:38Z",
                "user": "admin",
                "action": "create_job",
                "status": "success",
                "ip": "192.168.1.100",
                "resource": "/createItem"
            },
            {
                "timestamp": "2023-10-10T13:55:39Z",
                "user": "user1",
                "action": "access_job",
                "status": "success",
                "ip": "192.168.1.101",
                "resource": "/job/sample-build-job"
            },
            {
                "timestamp": "2023-10-10T13:55:40Z",
                "user": "attacker",
                "action": "access_script_console",
                "status": "denied",
                "ip": "10.0.0.51",
                "resource": "/script"
            }
        ]
        
        with open(audit_log_path, 'a') as f:
            for log_entry in sample_audit_logs:
                f.write(json.dumps(log_entry) + '\n')
        
        logger.info(f"Generated {len(sample_audit_logs)} sample audit log entries at {audit_log_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate audit logs: {e}")
        return False

def verify_elasticsearch_connection():
    """Verify that Elasticsearch is running and accessible"""
    try:
        response = requests.get('http://elasticsearch:9200/_cluster/health', timeout=10)
        if response.status_code == 200:
            logger.info("Elasticsearch is running and accessible")
            return True
        else:
            logger.error(f"Elasticsearch returned status code: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Failed to connect to Elasticsearch: {e}")
        return False

def check_kibana_index_pattern():
    """Check if the Jenkins logs index pattern exists in Kibana"""
    try:
        # Check if index exists in Elasticsearch
        response = requests.get('http://elasticsearch:9200/jenkins-logs-*', timeout=10)
        if response.status_code == 200:
            logger.info("Jenkins logs index pattern exists in Elasticsearch")
            return True
        else:
            logger.warning("Jenkins logs index pattern not found in Elasticsearch")
            return False
    except Exception as e:
        logger.error(f"Failed to check Kibana index pattern: {e}")
        return False

def main():
    """Main function to generate test logs and verify the pipeline"""
    logger.info("Starting test log generation and pipeline verification...")
    
    # Generate sample logs
    success_count = 0
    
    if generate_sample_access_logs():
        success_count += 1
    
    if generate_sample_application_logs():
        success_count += 1
        
    if generate_sample_build_logs():
        success_count += 1
        
    if generate_sample_audit_logs():
        success_count += 1
    
    logger.info(f"Generated test logs: {success_count}/4 successful")
    
    # Wait for Filebeat to process the logs
    logger.info("Waiting for Filebeat to process logs...")
    time.sleep(30)
    
    # Verify Elasticsearch connection
    if verify_elasticsearch_connection():
        # Check if logs are being indexed
        if check_kibana_index_pattern():
            logger.info("✅ Pipeline verification successful! Logs are being collected and indexed.")
        else:
            logger.warning("⚠️  Logs may not be properly indexed. Check Filebeat and Logstash logs.")
    else:
        logger.error("❌ Pipeline verification failed. Elasticsearch is not accessible.")
    
    logger.info("Test log generation completed.")

if __name__ == "__main__":
    main()