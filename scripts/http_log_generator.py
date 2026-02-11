#!/usr/bin/env python3
"""
HTTP Log Generator
Generates Common Log Format (CLF) entries for HTTP requests
These logs are written to files that Filebeat will collect
"""

import os
import time
import random
from datetime import datetime
import socket

# Jenkins logs directory - try container path first, fallback to local path
JENKINS_HOME = "/var/jenkins_home"
LOGS_DIR = os.path.join(JENKINS_HOME, "logs")

# Check if we're in a container, otherwise use a local directory
if not os.path.exists(JENKINS_HOME):
    # Running locally, use a temporary logs directory
    LOGS_DIR = os.path.expanduser("~/.jenkins-security-logs")

# Ensure logs directory exists
try:
    os.makedirs(LOGS_DIR, exist_ok=True)
except Exception as e:
    print(f"⚠️ Warning: Could not create logs directory {LOGS_DIR}: {e}")

# HTTP access log file path
HTTP_ACCESS_LOG = os.path.join(LOGS_DIR, "http_access.log")

# HTTP response codes and their meanings
HTTP_RESPONSES = {
    200: "OK",
    201: "Created",
    204: "No Content",
    301: "Moved Permanently",
    302: "Found",
    304: "Not Modified",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
}

# User agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "curl/7.68.0",
    "python-requests/2.31.0",
]

# Common referrers
REFERRERS = [
    "-",
    "http://localhost:8080/",
    "http://localhost:8080/api/json",
    "http://jenkins:8080/",
]


class HTTPLogGenerator:
    """Generate HTTP access logs in Common Log Format (CLF)"""
    
    @staticmethod
    def format_timestamp():
        """Format current time in CLF format: [12/Feb/2026:10:30:45 +0000]"""
        return datetime.now().strftime("[%d/%b/%Y:%H:%M:%S +0000]")
    
    @staticmethod
    def generate_log_entry(
        client_ip: str,
        auth_user: str,
        http_method: str,
        request_path: str,
        http_version: str,
        response_code: int,
        bytes_sent: int,
        user_agent: str = None,
        referrer: str = None,
        timestamp: str = None
    ) -> str:
        """
        Generate a Common Log Format (CLF) entry
        
        Format:
        client_ip ident auth_user [timestamp] "method path HTTP/version" response_code bytes_sent "referrer" "user_agent"
        
        Example:
        127.0.0.1 - admin [12/Feb/2026:10:30:45 +0000] "GET /api/json HTTP/1.1" 200 5234 "-" "Mozilla/5.0"
        """
        if timestamp is None:
            timestamp = HTTPLogGenerator.format_timestamp()
        
        if user_agent is None:
            user_agent = random.choice(USER_AGENTS)
        
        if referrer is None:
            referrer = random.choice(REFERRERS)
        
        # Escape quotes in user_agent and referrer
        user_agent = user_agent.replace('"', '\\"')
        referrer = referrer.replace('"', '\\"')
        
        log_entry = f'{client_ip} - {auth_user} {timestamp} "{http_method} {request_path} HTTP/{http_version}" {response_code} {bytes_sent} "{referrer}" "{user_agent}"'
        return log_entry
    
    @staticmethod
    def log_request(
        client_ip: str,
        auth_user: str,
        http_method: str,
        request_path: str,
        http_version: str,
        response_code: int,
        bytes_sent: int,
        user_agent: str = None,
        referrer: str = None,
        timestamp: str = None,
        log_file: str = None
    ) -> None:
        """
        Write an HTTP request to the access log file
        
        Args:
            client_ip: Client IP address
            auth_user: Authenticated username
            http_method: HTTP method (GET, POST, etc.)
            request_path: Request path/URI
            http_version: HTTP version (1.0, 1.1, 2.0)
            response_code: HTTP response code
            bytes_sent: Bytes sent in response
            user_agent: User-Agent header (optional)
            referrer: Referer header (optional)
            timestamp: Log timestamp (optional, auto-generated if not provided)
            log_file: Log file path (default: HTTP_ACCESS_LOG)
        """
        if log_file is None:
            log_file = HTTP_ACCESS_LOG
        
        # Generate the log entry
        log_entry = HTTPLogGenerator.generate_log_entry(
            client_ip=client_ip,
            auth_user=auth_user,
            http_method=http_method,
            request_path=request_path,
            http_version=http_version,
            response_code=response_code,
            bytes_sent=bytes_sent,
            user_agent=user_agent,
            referrer=referrer,
            timestamp=timestamp
        )
        
        # Write to log file
        try:
            with open(log_file, 'a') as f:
                f.write(log_entry + '\n')
                f.flush()
        except Exception as e:
            print(f"⚠️  Could not write to log file {log_file}: {e}")
    
    @staticmethod
    def log_normal_request(
        http_method: str,
        request_path: str,
        response_code: int = 200,
        bytes_sent: int = None,
        auth_user: str = "admin",
        client_ip: str = "127.0.0.1"
    ) -> None:
        """Log a normal (legitimate) HTTP request"""
        if bytes_sent is None:
            bytes_sent = random.randint(1000, 10000)
        
        HTTPLogGenerator.log_request(
            client_ip=client_ip,
            auth_user=auth_user,
            http_method=http_method,
            request_path=request_path,
            http_version="1.1",
            response_code=response_code,
            bytes_sent=bytes_sent
        )
    
    @staticmethod
    def log_attack_request(
        http_method: str,
        request_path: str,
        response_code: int = 401,
        bytes_sent: int = None,
        auth_user: str = "-",
        client_ip: str = "192.168.1.100",
        attack_type: str = ""
    ) -> None:
        """Log an attack HTTP request"""
        if bytes_sent is None:
            bytes_sent = random.randint(100, 5000)
        
        HTTPLogGenerator.log_request(
            client_ip=client_ip,
            auth_user=auth_user,
            http_method=http_method,
            request_path=request_path,
            http_version="1.1",
            response_code=response_code,
            bytes_sent=bytes_sent
        )


def test_log_generator():
    """Test the log generator"""
    print("Testing HTTP Log Generator...")
    
    # Test normal request
    HTTPLogGenerator.log_normal_request(
        http_method="GET",
        request_path="/api/json",
        response_code=200,
        bytes_sent=5234
    )
    
    # Test attack request
    HTTPLogGenerator.log_attack_request(
        http_method="GET",
        request_path="/login",
        response_code=401,
        bytes_sent=1234
    )
    
    # Test path traversal attack
    HTTPLogGenerator.log_attack_request(
        http_method="GET",
        request_path="/../../../etc/passwd",
        response_code=400,
        bytes_sent=342
    )
    
    # Test script console access
    HTTPLogGenerator.log_attack_request(
        http_method="POST",
        request_path="/script",
        response_code=403,
        bytes_sent=456
    )
    
    print(f"✓ Log entries written to {HTTP_ACCESS_LOG}")
    
    # Try to read back
    try:
        with open(HTTP_ACCESS_LOG, 'r') as f:
            lines = f.readlines()
            print(f"\nLast {min(4, len(lines))} log entries:")
            for line in lines[-4:]:
                print(f"  {line.strip()}")
    except Exception as e:
        print(f"Could not read log file: {e}")


if __name__ == "__main__":
    test_log_generator()
