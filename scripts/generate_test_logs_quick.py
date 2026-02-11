#!/usr/bin/env python3
"""
Test Log Generator
Quickly generates test logs to verify Kibana setup without needing full demo
"""

import sys
import os
import time

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from http_log_generator import HTTPLogGenerator

def generate_test_logs():
    """Generate a comprehensive set of test logs"""
    
    print("\n" + "="*70)
    print("📝 Generating Test HTTP Access Logs")
    print("="*70 + "\n")
    
    num_normal = 0
    num_attacks = 0
    
    # Generate normal traffic
    print("Generating normal user traffic...")
    normal_requests = [
        ("127.0.0.1", "admin", "GET", "/", 200, 8234),
        ("127.0.0.1", "admin", "GET", "/api/json", 200, 5234),
        ("127.0.0.1", "admin", "GET", "/job/sample-build-job/", 200, 4567),
        ("127.0.0.1", "admin", "GET", "/job/test-job/", 200, 3456),
        ("127.0.0.1", "admin", "POST", "/job/sample-build-job/build", 201, 234),
        ("127.0.0.1", "admin", "GET", "/job/sample-build-job/1/console", 200, 12345),
        ("127.0.0.1", "admin", "GET", "/job/sample-build-job/1/api/json", 200, 2345),
        ("127.0.0.1", "user", "GET", "/", 200, 8234),
        ("127.0.0.1", "user", "GET", "/api/json", 200, 5234),
        ("127.0.0.1", "user", "GET", "/job/test-job/", 200, 3456),
    ]
    
    for client_ip, user, method, path, code, size in normal_requests:
        HTTPLogGenerator.log_normal_request(
            http_method=method,
            request_path=path,
            response_code=code,
            bytes_sent=size,
            auth_user=user,
            client_ip=client_ip
        )
        num_normal += 1
        time.sleep(0.1)
    
    print(f"✓ Generated {num_normal} normal request logs\n")
    
    # Generate attack traffic
    print("Generating attack traffic...")
    
    # Brute force attempts
    print("  - Brute force login attempts...")
    for i in range(5):
        HTTPLogGenerator.log_attack_request(
            http_method="GET",
            request_path="/login",
            response_code=401,
            bytes_sent=1234,
            auth_user=f"admin_{i}",
            client_ip="192.168.1.100",
            attack_type="brute_force"
        )
        num_attacks += 1
        time.sleep(0.05)
    
    # Path traversal attempts
    print("  - Path traversal attempts...")
    path_traversal_paths = [
        "/../../../etc/passwd",
        "/..\\..\\..\\windows\\system32\\config\\sam",
        "/..%2F..%2F..%2Fetc%2Fpasswd",
    ]
    for path in path_traversal_paths:
        HTTPLogGenerator.log_attack_request(
            http_method="GET",
            request_path=path,
            response_code=400,
            bytes_sent=342,
            client_ip="192.168.1.100",
            attack_type="path_traversal"
        )
        num_attacks += 1
        time.sleep(0.05)
    
    # Script console access
    print("  - Script console exploitation attempts...")
    for i in range(3):
        HTTPLogGenerator.log_attack_request(
            http_method="GET",
            request_path="/script",
            response_code=403,
            bytes_sent=456,
            client_ip="192.168.1.100",
            attack_type="script_console"
        )
        HTTPLogGenerator.log_attack_request(
            http_method="POST",
            request_path="/script",
            response_code=403,
            bytes_sent=512,
            client_ip="192.168.1.100",
            attack_type="script_execution"
        )
        num_attacks += 2
        time.sleep(0.05)
    
    # API enumeration
    print("  - API enumeration attempts...")
    api_endpoints = ["/api/json", "/queue/api/json", "/computer/api/json", 
                    "/systemInfo/api/json", "/manage", "/configure"]
    for endpoint in api_endpoints:
        HTTPLogGenerator.log_attack_request(
            http_method="GET",
            request_path=endpoint,
            response_code=403,
            bytes_sent=234,
            auth_user="attacker",
            client_ip="192.168.1.100",
            attack_type="api_enumeration"
        )
        num_attacks += 1
        time.sleep(0.05)
    
    # DoS via build triggering
    print("  - DoS build triggering attacks...")
    for i in range(10):
        HTTPLogGenerator.log_attack_request(
            http_method="POST",
            request_path="/job/sample-build-job/build",
            response_code=201,
            bytes_sent=100,
            auth_user="attacker",
            client_ip="192.168.1.200",
            attack_type="dos_build"
        )
        num_attacks += 1
        time.sleep(0.05)
    
    # Unauthorized access attempts
    print("  - Unauthorized admin access attempts...")
    admin_endpoints = ["/configure", "/manage", "/systemInfo", "/credentials/"]
    for endpoint in admin_endpoints:
        HTTPLogGenerator.log_attack_request(
            http_method="GET",
            request_path=endpoint,
            response_code=403,
            bytes_sent=234,
            auth_user="-",
            client_ip="192.168.1.100",
            attack_type="unauthorized_access"
        )
        num_attacks += 1
        time.sleep(0.05)
    
    print(f"✓ Generated {num_attacks} attack request logs\n")
    
    # Summary
    print("="*70)
    print("📊 Log Generation Summary")
    print("="*70)
    print(f"Total normal requests:    {num_normal}")
    print(f"Total attack requests:    {num_attacks}")
    print(f"Total logs generated:     {num_normal + num_attacks}")
    
    # Import HTTP_ACCESS_LOG variable
    from http_log_generator import HTTP_ACCESS_LOG
    print(f"Log file location:        {HTTP_ACCESS_LOG}")
    print("="*70 + "\n")
    
    # Show sample logs
    print("📋 Sample logs (last 5 entries):")
    print("-"*70)
    try:
        with open(HTTP_ACCESS_LOG, 'r') as f:
            lines = f.readlines()
            for line in lines[-5:]:
                # Truncate long lines for display
                display_line = line.rstrip()
                if len(display_line) > 120:
                    display_line = display_line[:117] + "..."
                print(display_line)
    except Exception as e:
        print(f"Could not read log file: {e}")
    
    print("-"*70 + "\n")
    
    print("✅ Test logs generated successfully!")
    print("\n📌 Next steps:")
    print("1. Start the Docker services: cd docker && docker-compose up -d")
    print("2. Wait for Elasticsearch and Kibana to be ready (~2 minutes)")
    print("3. Copy these logs to Jenkins container: docker cp ~/.jenkins-security-logs/http_access.log jenkins:/var/jenkins_home/logs/")
    print("4. Go to Kibana at http://localhost:5601")
    print("5. Create index pattern for 'jenkins-logs-*'")
    print("6. Use Discover to view the logs")
    print()

if __name__ == "__main__":
    generate_test_logs()
