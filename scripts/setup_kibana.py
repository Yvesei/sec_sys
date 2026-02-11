#!/usr/bin/env python3
"""
Kibana Setup Script
Configures Kibana with index patterns, visualizations, and dashboards
"""

import requests
import json
import time
import sys

KIBANA_URL = "http://localhost:5601"
ELASTICSEARCH_URL = "http://localhost:9200"

def wait_for_kibana():
    """Wait for Kibana to be ready"""
    print("Waiting for Kibana to be ready...")
    max_retries = 60
    
    for i in range(max_retries):
        try:
            response = requests.get(f"{KIBANA_URL}/api/status", timeout=5)
            if response.status_code == 200:
                print("✓ Kibana is ready!")
                return True
        except:
            pass
        
        if i < max_retries - 1:
            print(f"Waiting... ({i+1}/{max_retries})")
            time.sleep(5)
    
    print("✗ Kibana failed to start")
    return False

def wait_for_elasticsearch():
    """Wait for Elasticsearch to be ready"""
    print("Waiting for Elasticsearch to be ready...")
    max_retries = 60
    
    for i in range(max_retries):
        try:
            response = requests.get(f"{ELASTICSEARCH_URL}/_cluster/health", timeout=5)
            if response.status_code == 200:
                print("✓ Elasticsearch is ready!")
                return True
        except:
            pass
        
        if i < max_retries - 1:
            print(f"Waiting... ({i+1}/{max_retries})")
            time.sleep(5)
    
    print("✗ Elasticsearch failed to start")
    return False

def create_index_pattern():
    """Create index pattern in Kibana"""
    print("\nCreating index pattern...")
    
    headers = {
        'kbn-xsrf': 'true',
        'Content-Type': 'application/json'
    }
    
    index_pattern = {
        "attributes": {
            "title": "jenkins-logs-*",
            "timeFieldName": "@timestamp"
        }
    }
    
    try:
        response = requests.post(
            f"{KIBANA_URL}/api/saved_objects/index-pattern/jenkins-logs-pattern",
            headers=headers,
            json=index_pattern,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print("✓ Index pattern created successfully")
            return True
        elif response.status_code == 409:
            print("ℹ Index pattern already exists")
            return True
        else:
            print(f"✗ Failed to create index pattern: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"✗ Error creating index pattern: {e}")
        return False

def set_default_index_pattern():
    """Set the default index pattern"""
    print("\nSetting default index pattern...")
    
    headers = {
        'kbn-xsrf': 'true',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            f"{KIBANA_URL}/api/kibana/settings/defaultIndex",
            headers=headers,
            json={"value": "jenkins-logs-pattern"},
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print("✓ Default index pattern set")
            return True
        else:
            print(f"ℹ Could not set default index pattern (this is optional)")
            return True
    except Exception as e:
        print(f"ℹ Could not set default index pattern: {e}")
        return True

def create_visualizations():
    """Create sample visualizations"""
    print("\nCreating visualizations...")
    
    headers = {
        'kbn-xsrf': 'true',
        'Content-Type': 'application/json'
    }
    
    visualizations = [
        {
            "id": "failed-logins-metric",
            "type": "metric",
            "attributes": {
                "title": "Failed Login Attempts",
                "visState": json.dumps({
                    "title": "Failed Login Attempts",
                    "type": "metric",
                    "params": {
                        "addTooltip": True,
                        "addLegend": False,
                        "type": "metric",
                        "metric": {
                            "colorSchema": "Green to Red",
                            "colorsRange": [
                                {"from": 0, "to": 10},
                                {"from": 10, "to": 50},
                                {"from": 50, "to": 1000}
                            ]
                        }
                    }
                })
            }
        },
        {
            "id": "http-status-codes",
            "type": "visualization",
            "attributes": {
                "title": "HTTP Status Codes Distribution",
                "visState": json.dumps({
                    "title": "HTTP Status Codes",
                    "type": "pie"
                })
            }
        }
    ]
    
    success_count = 0
    for viz in visualizations:
        try:
            response = requests.post(
                f"{KIBANA_URL}/api/saved_objects/{viz['type']}/{viz['id']}",
                headers=headers,
                json=viz,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"✓ Created visualization: {viz['id']}")
                success_count += 1
            elif response.status_code == 409:
                print(f"ℹ Visualization already exists: {viz['id']}")
                success_count += 1
        except Exception as e:
            print(f"✗ Error creating visualization {viz['id']}: {e}")
    
    return success_count > 0

def create_sample_searches():
    """Create sample saved searches"""
    print("\nCreating saved searches...")
    
    headers = {
        'kbn-xsrf': 'true',
        'Content-Type': 'application/json'
    }
    
    searches = [
        {
            "id": "failed-authentications",
            "attributes": {
                "title": "Failed Authentications",
                "description": "All failed login attempts (401 and 403 responses)",
                "columns": ["client_ip", "auth", "http_method", "request_path", "response_code"],
                "kibanaSavedObjectMeta": {
                    "searchSourceJSON": json.dumps({
                        "index": "jenkins-logs-pattern",
                        "query": {
                            "query": "log_type: jenkins_access AND response_code: (401 OR 403)",
                            "language": "kuery"
                        },
                        "filter": []
                    })
                }
            }
        },
        {
            "id": "path-traversal-attempts",
            "attributes": {
                "title": "Path Traversal Attempts",
                "description": "Detected path traversal attack attempts",
                "columns": ["client_ip", "request_path", "response_code"],
                "kibanaSavedObjectMeta": {
                    "searchSourceJSON": json.dumps({
                        "index": "jenkins-logs-pattern",
                        "query": {
                            "query": "tags: path_traversal_attempt",
                            "language": "kuery"
                        },
                        "filter": []
                    })
                }
            }
        },
        {
            "id": "script-console-access",
            "attributes": {
                "title": "Script Console Access",
                "description": "All attempts to access the script console",
                "columns": ["client_ip", "auth", "request_path", "response_code"],
                "kibanaSavedObjectMeta": {
                    "searchSourceJSON": json.dumps({
                        "index": "jenkins-logs-pattern",
                        "query": {
                            "query": "tags: script_console_access",
                            "language": "kuery"
                        },
                        "filter": []
                    })
                }
            }
        }
    ]
    
    success_count = 0
    for search in searches:
        try:
            response = requests.post(
                f"{KIBANA_URL}/api/saved_objects/search/{search['id']}",
                headers=headers,
                json=search,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"✓ Created search: {search['id']}")
                success_count += 1
            elif response.status_code == 409:
                print(f"ℹ Search already exists: {search['id']}")
                success_count += 1
        except Exception as e:
            print(f"✗ Error creating search {search['id']}: {e}")
    
    return success_count > 0

def print_usage_instructions():
    """Print instructions for using Kibana"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                 Kibana Setup Complete!                       ║
╚══════════════════════════════════════════════════════════════╝

🎉 Kibana is now configured and ready to use!

📍 Access Kibana at: {KIBANA_URL}

🔍 Quick Start Guide:

1. Navigate to Discover:
   Menu → Discover

2. Select the index pattern:
   jenkins-logs-*

3. Try these sample queries:

   View all failed logins:
   ─────────────────────────────────────────────────────────────
   log_type: "jenkins_access" AND response_code: (401 OR 403)
   ─────────────────────────────────────────────────────────────

   Detect brute force attempts:
   ─────────────────────────────────────────────────────────────
   tags: authentication_failure
   ─────────────────────────────────────────────────────────────

   Find path traversal attempts:
   ─────────────────────────────────────────────────────────────
   tags: path_traversal_attempt
   ─────────────────────────────────────────────────────────────

   Script console access:
   ─────────────────────────────────────────────────────────────
   tags: script_console_access
   ─────────────────────────────────────────────────────────────

   API enumeration:
   ─────────────────────────────────────────────────────────────
   tags: api_access
   ─────────────────────────────────────────────────────────────

4. Create Visualizations:
   Analytics → Visualize → Create visualization

5. Build Dashboards:
   Analytics → Dashboard → Create dashboard

📊 Saved Searches Available:
   - Failed Authentications
   - Path Traversal Attempts
   - Script Console Access

🛡️ Detection Rules to Implement:

   Rule 1: Multiple Failed Logins
   ─────────────────────────────────────────────────────────────
   Threshold: 5 attempts in 5 minutes from same IP
   Query: log_type: "jenkins_access" AND response_code: (401 OR 403)
   ─────────────────────────────────────────────────────────────

   Rule 2: Path Traversal
   ─────────────────────────────────────────────────────────────
   Threshold: 1 attempt
   Query: tags: path_traversal_attempt
   ─────────────────────────────────────────────────────────────

   Rule 3: Script Console Access
   ─────────────────────────────────────────────────────────────
   Threshold: 1 access
   Query: tags: script_console_access
   ─────────────────────────────────────────────────────────────

Happy analyzing! 🔍
""".format(KIBANA_URL=KIBANA_URL))

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║              Kibana Configuration Setup                      ║
║     Setting up index patterns and visualizations             ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Wait for services
    if not wait_for_elasticsearch():
        sys.exit(1)
    
    if not wait_for_kibana():
        sys.exit(1)
    
    time.sleep(5)  # Give Kibana a moment to fully initialize
    
    # Create index pattern
    if not create_index_pattern():
        print("⚠️  Failed to create index pattern, but continuing...")
    
    time.sleep(2)
    
    # Set default index pattern
    set_default_index_pattern()
    
    time.sleep(2)
    
    # Create visualizations
    create_visualizations()
    
    time.sleep(2)
    
    # Create saved searches
    create_sample_searches()
    
    print("\n" + "="*70)
    print("✅ Kibana setup completed successfully!")
    print("="*70)
    
    # Print usage instructions
    print_usage_instructions()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        sys.exit(1)
