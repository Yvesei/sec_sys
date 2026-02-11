#!/usr/bin/env python3
"""
Script to configure Kibana to display Loki logs.
This script will:
1. Create Loki data source in Kibana
2. Set up index patterns for Loki logs
3. Create sample visualizations and dashboards
"""

import requests
import json
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

KIBANA_URL = "http://kibana:5601"
ELASTICSEARCH_URL = "http://elasticsearch:9200"
LOKI_URL = "http://loki:3100"

def wait_for_kibana():
    """Wait for Kibana to be ready"""
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(f"{KIBANA_URL}/api/status", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Kibana is ready")
                return True
        except Exception as e:
            logger.info(f"Waiting for Kibana... (attempt {attempt + 1}/{max_attempts})")
            time.sleep(10)
            attempt += 1
    
    logger.error("❌ Kibana did not become ready")
    return False

def wait_for_loki():
    """Wait for Loki to be ready"""
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(f"{LOKI_URL}/ready", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Loki is ready")
                return True
        except Exception as e:
            logger.info(f"Waiting for Loki... (attempt {attempt + 1}/{max_attempts})")
            time.sleep(10)
            attempt += 1
    
    logger.error("❌ Loki did not become ready")
    return False

def create_loki_data_source():
    """Create Loki data source in Kibana"""
    try:
        # Check if data source already exists
        response = requests.get(f"{KIBANA_URL}/api/data_source", timeout=30)
        if response.status_code == 200:
            data_sources = response.json()
            for source in data_sources:
                if source.get('name') == 'Loki':
                    logger.info("✅ Loki data source already exists")
                    return True
        
        # Create new Loki data source
        loki_data_source = {
            "name": "Loki",
            "type": "loki",
            "config": {
                "url": LOKI_URL,
                "timeout": 30000,
                "customHeaders": {}
            },
            "description": "Loki log data source for container logs"
        }
        
        response = requests.post(
            f"{KIBANA_URL}/api/data_source",
            headers={"Content-Type": "application/json", "kbn-xsrf": "true"},
            data=json.dumps(loki_data_source),
            timeout=30
        )
        
        if response.status_code == 200:
            logger.info("✅ Successfully created Loki data source")
            return True
        else:
            logger.error(f"❌ Failed to create Loki data source: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Exception creating Loki data source: {e}")
        return False

def create_index_patterns():
    """Create index patterns for all log types"""
    try:
        index_patterns = [
            {
                "name": "jenkins-logs-*",
                "title": "jenkins-logs-*",
                "type": "logs"
            },
            {
                "name": "loki-logs-*",
                "title": "loki-logs-*",
                "type": "logs"
            },
            {
                "name": "container-logs-*",
                "title": "container-logs-*",
                "type": "logs"
            }
        ]
        
        success_count = 0
        for pattern in index_patterns:
            try:
                response = requests.post(
                    f"{KIBANA_URL}/api/saved_objects/index-pattern",
                    headers={"Content-Type": "application/json", "kbn-xsrf": "true"},
                    data=json.dumps({
                        "attributes": {
                            "title": pattern["title"],
                            "timeFieldName": "@timestamp"
                        }
                    }),
                    timeout=30
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Created index pattern: {pattern['name']}")
                    success_count += 1
                else:
                    logger.warning(f"⚠️  Index pattern {pattern['name']} may already exist")
                    
            except Exception as e:
                logger.error(f"❌ Exception creating index pattern {pattern['name']}: {e}")
        
        logger.info(f"Created {success_count}/{len(index_patterns)} index patterns")
        return success_count > 0
        
    except Exception as e:
        logger.error(f"❌ Exception creating index patterns: {e}")
        return False

def create_sample_visualizations():
    """Create sample visualizations for Jenkins and Loki logs"""
    try:
        visualizations = [
            {
                "name": "Jenkins HTTP Requests",
                "type": "histogram",
                "index_pattern": "jenkins-logs-*",
                "query": 'log_type: "jenkins_access"',
                "x_axis": "@timestamp",
                "y_axis": "count()"
            },
            {
                "name": "Container Logs by Service",
                "type": "pie",
                "index_pattern": "loki-logs-*",
                "query": 'log_type: "loki_container"',
                "metric": "count()",
                "bucket": "compose_service"
            },
            {
                "name": "Jenkins Build Status",
                "type": "pie",
                "index_pattern": "jenkins-logs-*",
                "query": 'log_type: "jenkins_build"',
                "metric": "count()",
                "bucket": "tags"
            },
            {
                "name": "Error Logs Over Time",
                "type": "line",
                "index_pattern": "jenkins-logs-*",
                "query": 'log_level: "ERROR" OR tags: "http_error"',
                "x_axis": "@timestamp",
                "y_axis": "count()"
            }
        ]
        
        success_count = 0
        for viz in visualizations:
            try:
                visualization_data = {
                    "attributes": {
                        "title": viz["name"],
                        "visState": json.dumps({
                            "title": viz["name"],
                            "type": viz["type"],
                            "params": {
                                "shareYAxis": True,
                                "addTooltip": True,
                                "addLegend": True,
                                "legendPosition": "right",
                                "times": [],
                                "addTimeMarker": False
                            },
                            "aggs": [
                                {
                                    "id": "1",
                                    "enabled": True,
                                    "type": "count",
                                    "schema": "metric",
                                    "params": {}
                                },
                                {
                                    "id": "2",
                                    "enabled": True,
                                    "type": "date_histogram",
                                    "schema": "segment",
                                    "params": {
                                        "field": viz.get("x_axis", "@timestamp"),
                                        "interval": "auto",
                                        "customInterval": "2h",
                                        "min_doc_count": 1,
                                        "extended_bounds": {}
                                    }
                                }
                            ]
                        }),
                        "uiStateJSON": "{}",
                        "description": f"{viz['type']} visualization for {viz['index_pattern']}",
                        "version": 1,
                        "kibanaSavedObjectMeta": {
                            "searchSourceJSON": json.dumps({
                                "index": viz["index_pattern"],
                                "query": {
                                    "query": viz["query"],
                                    "language": "kuery"
                                },
                                "filter": []
                            })
                        }
                    },
                    "type": "visualization",
                    "references": [
                        {
                            "type": "index-pattern",
                            "id": viz["index_pattern"],
                            "name": "kibanaSavedObjectMeta.searchSourceJSON.index"
                        }
                    ]
                }
                
                response = requests.post(
                    f"{KIBANA_URL}/api/saved_objects/visualization",
                    headers={"Content-Type": "application/json", "kbn-xsrf": "true"},
                    data=json.dumps(visualization_data),
                    timeout=30
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Created visualization: {viz['name']}")
                    success_count += 1
                else:
                    logger.warning(f"⚠️  Visualization {viz['name']} may already exist")
                    
            except Exception as e:
                logger.error(f"❌ Exception creating visualization {viz['name']}: {e}")
        
        logger.info(f"Created {success_count}/{len(visualizations)} visualizations")
        return success_count > 0
        
    except Exception as e:
        logger.error(f"❌ Exception creating visualizations: {e}")
        return False

def create_sample_dashboard():
    """Create a sample dashboard with all visualizations"""
    try:
        dashboard_data = {
            "attributes": {
                "title": "Jenkins & Loki Logs Dashboard",
                "description": "Comprehensive dashboard for Jenkins and container logs",
                "panelsJSON": json.dumps([
                    {
                        "id": "jenkins-http-requests",
                        "type": "visualization",
                        "gridData": {"x": 0, "y": 0, "w": 24, "h": 12},
                        "embeddableConfig": {}
                    },
                    {
                        "id": "container-logs-by-service",
                        "type": "visualization",
                        "gridData": {"x": 0, "y": 12, "w": 12, "h": 12},
                        "embeddableConfig": {}
                    },
                    {
                        "id": "jenkins-build-status",
                        "type": "visualization",
                        "gridData": {"x": 12, "y": 12, "w": 12, "h": 12},
                        "embeddableConfig": {}
                    },
                    {
                        "id": "error-logs-over-time",
                        "type": "visualization",
                        "gridData": {"x": 0, "y": 24, "w": 24, "h": 12},
                        "embeddableConfig": {}
                    }
                ]),
                "version": 1,
                "timeRestore": True,
                "kibanaSavedObjectMeta": {
                    "searchSourceJSON": json.dumps({
                        "query": {"query": "", "language": "kuery"},
                        "filter": []
                    })
                }
            },
            "type": "dashboard",
            "references": []
        }
        
        response = requests.post(
            f"{KIBANA_URL}/api/saved_objects/dashboard",
            headers={"Content-Type": "application/json", "kbn-xsrf": "true"},
            data=json.dumps(dashboard_data),
            timeout=30
        )
        
        if response.status_code == 200:
            logger.info("✅ Created comprehensive dashboard")
            return True
        else:
            logger.error(f"❌ Failed to create dashboard: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Exception creating dashboard: {e}")
        return False

def main():
    """Main function to configure Kibana for Loki logs"""
    logger.info("Starting Kibana Loki configuration...")
    
    # Wait for services to be ready
    if not wait_for_kibana():
        logger.error("❌ Kibana not ready, aborting configuration")
        return
    
    if not wait_for_loki():
        logger.error("❌ Loki not ready, aborting configuration")
        return
    
    # Configure Kibana
    success_count = 0
    
    if create_loki_data_source():
        success_count += 1
    
    if create_index_patterns():
        success_count += 1
    
    if create_sample_visualizations():
        success_count += 1
    
    if create_sample_dashboard():
        success_count += 1
    
    logger.info(f"Kibana configuration completed: {success_count}/4 tasks successful")
    
    if success_count >= 3:
        logger.info("✅ Kibana Loki configuration successful!")
        logger.info("📊 Access Kibana at http://localhost:5601 to view the logs")
    else:
        logger.warning("⚠️  Some configuration tasks failed, check logs for details")

if __name__ == "__main__":
    main()