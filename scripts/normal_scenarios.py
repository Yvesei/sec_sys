#!/usr/bin/env python3
"""
Normal Usage Scenarios Script
Generates legitimate user traffic for Jenkins
"""

import requests
import time
import random
import sys
import os
from requests.auth import HTTPBasicAuth
import urllib3

# Add scripts directory to path so we can import http_log_generator
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from http_log_generator import HTTPLogGenerator

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
JENKINS_URL = "http://localhost:8080"
USERNAME = "admin"
PASSWORD = "admin123"

# User agents to simulate different browsers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
]

# Jobs to interact with
JOBS = [
    "sample-build-job",
    "test-job",
    "deploy-to-production"
]

class JenkinsNormalUser:
    def __init__(self):
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(USERNAME, PASSWORD)
        self.session.headers.update({
            'User-Agent': random.choice(USER_AGENTS)
        })
        
    def login(self):
        """Simulate user login"""
        try:
            response = self.session.get(f"{JENKINS_URL}/login")
            # Log the HTTP request
            HTTPLogGenerator.log_normal_request(
                http_method="GET",
                request_path="/login",
                response_code=response.status_code,
                bytes_sent=len(response.content)
            )
            print(f"✓ Login attempt - Status: {response.status_code}")
            time.sleep(random.uniform(0.5, 1.5))
            return response.status_code == 200
        except Exception as e:
            print(f"✗ Login failed: {e}")
            return False
    
    def view_dashboard(self):
        """View main dashboard"""
        try:
            response = self.session.get(f"{JENKINS_URL}/")
            # Log the HTTP request
            HTTPLogGenerator.log_normal_request(
                http_method="GET",
                request_path="/",
                response_code=response.status_code,
                bytes_sent=len(response.content)
            )
            print(f"✓ Viewed dashboard - Status: {response.status_code}")
            time.sleep(random.uniform(1, 3))
            return response.status_code == 200
        except Exception as e:
            print(f"✗ Dashboard view failed: {e}")
            return False
    
    def list_jobs(self):
        """List all jobs"""
        try:
            response = self.session.get(f"{JENKINS_URL}/api/json")
            # Log the HTTP request
            HTTPLogGenerator.log_normal_request(
                http_method="GET",
                request_path="/api/json",
                response_code=response.status_code,
                bytes_sent=len(response.content)
            )
            print(f"✓ Listed jobs - Status: {response.status_code}")
            time.sleep(random.uniform(0.5, 1.5))
            return response.status_code == 200
        except Exception as e:
            print(f"✗ List jobs failed: {e}")
            return False
    
    def view_job(self, job_name):
        """View specific job"""
        try:
            response = self.session.get(f"{JENKINS_URL}/job/{job_name}/")
            # Log the HTTP request
            HTTPLogGenerator.log_normal_request(
                http_method="GET",
                request_path=f"/job/{job_name}/",
                response_code=response.status_code,
                bytes_sent=len(response.content)
            )
            print(f"✓ Viewed job '{job_name}' - Status: {response.status_code}")
            time.sleep(random.uniform(1, 2))
            return response.status_code == 200
        except Exception as e:
            print(f"✗ View job failed: {e}")
            return False
    
    def trigger_build(self, job_name):
        """Trigger a build"""
        try:
            # Get crumb (if CSRF is enabled)
            crumb_response = self.session.get(
                f"{JENKINS_URL}/crumbIssuer/api/json",
                timeout=5
            )
            
            headers = {}
            if crumb_response.status_code == 200:
                crumb_data = crumb_response.json()
                headers[crumb_data['crumbRequestField']] = crumb_data['crumb']
            
            # Trigger build
            response = self.session.post(
                f"{JENKINS_URL}/job/{job_name}/build",
                headers=headers
            )
            # Log the HTTP request
            HTTPLogGenerator.log_normal_request(
                http_method="POST",
                request_path=f"/job/{job_name}/build",
                response_code=response.status_code,
                bytes_sent=len(response.content) if hasattr(response, 'content') else 0
            )
            print(f"✓ Triggered build for '{job_name}' - Status: {response.status_code}")
            time.sleep(random.uniform(1, 2))
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"✗ Build trigger failed: {e}")
            return False
    
    def view_build_log(self, job_name, build_number=1):
        """View build console output"""
        try:
            response = self.session.get(
                f"{JENKINS_URL}/job/{job_name}/{build_number}/console"
            )
            # Log the HTTP request
            HTTPLogGenerator.log_normal_request(
                http_method="GET",
                request_path=f"/job/{job_name}/{build_number}/console",
                response_code=response.status_code,
                bytes_sent=len(response.content)
            )
            print(f"✓ Viewed build log for '{job_name}' #{build_number} - Status: {response.status_code}")
            time.sleep(random.uniform(1, 2))
            return response.status_code == 200
        except Exception as e:
            print(f"✗ View build log failed: {e}")
            return False
    
    def check_build_status(self, job_name, build_number=1):
        """Check build status via API"""
        try:
            response = self.session.get(
                f"{JENKINS_URL}/job/{job_name}/{build_number}/api/json"
            )
            # Log the HTTP request
            HTTPLogGenerator.log_normal_request(
                http_method="GET",
                request_path=f"/job/{job_name}/{build_number}/api/json",
                response_code=response.status_code,
                bytes_sent=len(response.content)
            )
            print(f"✓ Checked build status for '{job_name}' #{build_number} - Status: {response.status_code}")
            time.sleep(random.uniform(0.5, 1.5))
            return response.status_code == 200
        except Exception as e:
            print(f"✗ Check build status failed: {e}")
            return False

def simulate_normal_user_session():
    """Simulate a complete normal user session"""
    print("\n" + "="*60)
    print("Starting Normal User Session")
    print("="*60)
    
    user = JenkinsNormalUser()
    
    # Login
    if not user.login():
        print("Failed to login, aborting session")
        return
    
    # View dashboard
    user.view_dashboard()
    
    # List jobs
    user.list_jobs()
    
    # Interact with random jobs
    for _ in range(random.randint(2, 4)):
        job = random.choice(JOBS)
        
        # View job details
        user.view_job(job)
        
        # Maybe trigger a build (30% chance)
        if random.random() < 0.3:
            user.trigger_build(job)
            time.sleep(5)  # Wait for build to start
            user.check_build_status(job)
            user.view_build_log(job)
        
        # Random delay between actions
        time.sleep(random.uniform(2, 5))
    
    print("\n" + "="*60)
    print("Normal User Session Completed")
    print("="*60)

def run_continuous_normal_traffic(duration_minutes=30, users_per_minute=2):
    """
    Generate continuous normal traffic
    
    Args:
        duration_minutes: How long to run (default 30 minutes)
        users_per_minute: Average number of user sessions per minute
    """
    print("\n" + "="*60)
    print(f"Starting Continuous Normal Traffic Generation")
    print(f"Duration: {duration_minutes} minutes")
    print(f"Users per minute: {users_per_minute}")
    print("="*60)
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    session_count = 0
    
    while time.time() < end_time:
        # Simulate user sessions
        for _ in range(users_per_minute):
            session_count += 1
            print(f"\n--- Session #{session_count} ---")
            simulate_normal_user_session()
            
            # Random delay between sessions
            time.sleep(random.uniform(5, 15))
        
        # Wait remainder of minute
        elapsed = time.time() - start_time
        remaining = 60 - (elapsed % 60)
        if remaining > 0:
            print(f"\nWaiting {remaining:.1f} seconds until next minute...")
            time.sleep(remaining)
    
    print("\n" + "="*60)
    print(f"Traffic Generation Completed")
    print(f"Total sessions: {session_count}")
    print("="*60)

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║     Jenkins Normal Usage Scenarios                       ║
║     Generating Legitimate User Traffic                   ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Wait for Jenkins to be ready
    print("\nWaiting for Jenkins to be ready...")
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(JENKINS_URL, timeout=5)
            if response.status_code == 200 or response.status_code == 403:
                print("✓ Jenkins is ready!")
                break
        except:
            pass
        
        if i < max_retries - 1:
            print(f"Waiting... ({i+1}/{max_retries})")
            time.sleep(5)
        else:
            print("✗ Jenkins is not responding. Please check if it's running.")
            return
    
    # Menu
    print("\nSelect scenario:")
    print("1) Single user session (quick test)")
    print("2) Multiple user sessions (5 sessions)")
    print("3) Continuous traffic (30 minutes)")
    print("4) Custom duration continuous traffic")
    
    try:
        choice = input("\nEnter choice [1-4]: ").strip()
        
        if choice == "1":
            simulate_normal_user_session()
        
        elif choice == "2":
            for i in range(5):
                print(f"\n### Session {i+1}/5 ###")
                simulate_normal_user_session()
                time.sleep(random.uniform(10, 20))
        
        elif choice == "3":
            run_continuous_normal_traffic(duration_minutes=30, users_per_minute=2)
        
        elif choice == "4":
            duration = int(input("Enter duration in minutes: "))
            users = int(input("Enter users per minute: "))
            run_continuous_normal_traffic(duration_minutes=duration, users_per_minute=users)
        
        else:
            print("Invalid choice")
    
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()
