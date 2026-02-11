#!/usr/bin/env python3
"""
Script to trigger Jenkins activity and generate real logs.
This script will:
1. Trigger sample jobs to run
2. Access various Jenkins endpoints
3. Generate authentication events
4. Create more realistic log data
"""

import requests
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

JENKINS_URL = "http://jenkins:8080"
JENKINS_USER = "admin"
JENKINS_PASS = "admin123"

def trigger_jenkins_job(job_name):
    """Trigger a Jenkins job to generate build logs"""
    try:
        url = f"{JENKINS_URL}/job/{job_name}/build"
        auth = (JENKINS_USER, JENKINS_PASS)
        
        response = requests.post(url, auth=auth, timeout=30)
        
        if response.status_code == 201:
            logger.info(f"✅ Successfully triggered job: {job_name}")
            return True
        else:
            logger.error(f"❌ Failed to trigger job {job_name}. Status code: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Exception triggering job {job_name}: {e}")
        return False

def access_jenkins_endpoints():
    """Access various Jenkins endpoints to generate access logs"""
    try:
        auth = (JENKINS_USER, JENKINS_PASS)
        endpoints = [
            "/",
            "/api/json",
            "/job/sample-build-job/",
            "/job/test-job/",
            "/job/deploy-to-production/",
            "/manage/",
            "/systemInfo",
            "/pluginManager/",
            "/credentials/",
            "/computer/",
            "/asynchPeople/",
            "/view/all/",
            "/queue/",
            "/builds/",
            "/log/"
        ]
        
        success_count = 0
        for endpoint in endpoints:
            try:
                url = f"{JENKINS_URL}{endpoint}"
                response = requests.get(url, auth=auth, timeout=10)
                
                if response.status_code == 200:
                    logger.info(f"✅ Successfully accessed: {endpoint}")
                    success_count += 1
                else:
                    logger.warning(f"⚠️  Accessed {endpoint} with status code: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ Exception accessing {endpoint}: {e}")
        
        logger.info(f"Accessed {success_count}/{len(endpoints)} endpoints successfully")
        return success_count > 0
        
    except Exception as e:
        logger.error(f"❌ Exception accessing Jenkins endpoints: {e}")
        return False

def simulate_authentication_events():
    """Simulate various authentication events"""
    try:
        # Successful login
        auth_url = f"{JENKINS_URL}/j_acegi_security_check"
        auth_data = {
            'j_username': JENKINS_USER,
            'j_password': JENKINS_PASS,
            'from': '/',
            'Submit': 'Sign in'
        }
        
        response = requests.post(auth_url, data=auth_data, timeout=10, allow_redirects=False)
        
        if response.status_code == 302:
            logger.info("✅ Successful authentication event generated")
        else:
            logger.warning(f"⚠️  Authentication returned status code: {response.status_code}")
        
        # Failed login attempt (wrong credentials)
        wrong_auth_data = {
            'j_username': 'attacker',
            'j_password': 'wrongpassword',
            'from': '/',
            'Submit': 'Sign in'
        }
        
        response = requests.post(auth_url, data=wrong_auth_data, timeout=10, allow_redirects=False)
        
        if response.status_code == 200:
            logger.info("✅ Failed authentication event generated")
        else:
            logger.warning(f"⚠️  Failed authentication returned status code: {response.status_code}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Exception simulating authentication events: {e}")
        return False

def check_job_status(job_name):
    """Check the status of a Jenkins job"""
    try:
        url = f"{JENKINS_URL}/job/{job_name}/lastBuild/api/json"
        auth = (JENKINS_USER, JENKINS_PASS)
        
        response = requests.get(url, auth=auth, timeout=10)
        
        if response.status_code == 200:
            job_data = response.json()
            result = job_data.get('result', 'UNKNOWN')
            duration = job_data.get('duration', 0)
            logger.info(f"✅ Job {job_name} status: {result}, duration: {duration}ms")
            return True
        else:
            logger.error(f"❌ Failed to get job status for {job_name}. Status code: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Exception checking job status for {job_name}: {e}")
        return False

def main():
    """Main function to trigger Jenkins activity"""
    logger.info("Starting Jenkins activity generation...")
    
    # Wait for Jenkins to be ready
    logger.info("Waiting for Jenkins to be ready...")
    time.sleep(15)
    
    # Trigger sample jobs
    jobs_to_trigger = ["sample-build-job", "test-job", "deploy-to-production"]
    
    for job in jobs_to_trigger:
        trigger_jenkins_job(job)
        time.sleep(5)  # Wait between job triggers
    
    # Access various endpoints
    access_jenkins_endpoints()
    
    # Simulate authentication events
    simulate_authentication_events()
    
    # Wait for jobs to complete
    logger.info("Waiting for jobs to complete...")
    time.sleep(60)
    
    # Check job statuses
    for job in jobs_to_trigger:
        check_job_status(job)
        time.sleep(2)
    
    logger.info("✅ Jenkins activity generation completed!")

if __name__ == "__main__":
    main()