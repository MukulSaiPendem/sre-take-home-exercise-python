import yaml
import requests
import time
import json
import sys
from collections import defaultdict


def load_config(file_path):
    """Load the YAML config file"""
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def check_health(endpoint):
    """
    Check if an endpoint is healthy (UP) or not (DOWN).
    An endpoint is UP if it returns a 2xx status and responds within 500ms.
    """
    url = endpoint['url']
    # Default to GET
    method = endpoint.get('method', 'GET')
    headers = endpoint.get('headers', {})
    
    # Handle the body
    body = None
    if 'body' in endpoint:
        if isinstance(endpoint['body'], str):
            # Try to parse JSON
            try:
                body = json.loads(endpoint['body'])
            except:
                # Just use the string as-is
                body = endpoint['body']
        else:
            body = endpoint['body']
    
    try:
        # Make the request with a 500ms timeout
        start = time.time()
        
        # Handle content-type edge case
        if headers.get('content-type') == 'application/json' and isinstance(body, str):
            response = requests.request(
                method, url, headers=headers, data=body, timeout=0.5
            )
        else:
            response = requests.request(
                method, url, headers=headers, json=body, timeout=0.5
            )
            
        duration = time.time() - start
        
        # Consider it UP only if status code is 2xx and response time is <= 500ms
        if 200 <= response.status_code < 300 and duration <= 0.5:
            return "UP"
        else:
            return "DOWN"
    except:
        # Any errors (timeout, connection issues, etc.) count as DOWN
        return "DOWN"


def monitor_endpoints(config_path):
    """Main monitoring function that runs in a loop"""
    # Load the endpoints from YAML
    endpoints = load_config(config_path)
    
    stats = defaultdict(lambda: {"up": 0, "total": 0})
    
    print(f"Starting to monitor {len(endpoints)} endpoints...")
    
    # Main monitoring loop
    while True:
        cycle_start = time.time()
        
        # Check each endpoint
        for endpoint in endpoints:
            # Extract domain name (ignore port if present)
            domain = endpoint["url"].split("//")[-1].split("/")[0].split(":")[0]
            
            # Check if endpoint is up or down
            result = check_health(endpoint)
            
            # Update stats
            stats[domain]["total"] += 1
            if result == "UP":
                stats[domain]["up"] += 1
        
        # Print current availability for each domain
        for domain, domain_stats in stats.items():
            availability = round(100 * domain_stats["up"] / domain_stats["total"])
            print(f"{domain} has {availability}% availability percentage")
        
        print("---")
        
        # Sleep to make the cycle take exactly 15 seconds
        elapsed = time.time() - cycle_start
        time.sleep(max(0, 15 - elapsed))


if __name__ == "__main__":
    # check for config file
    if len(sys.argv) != 2:
        print("Usage: python monitor.py <config_file>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    try:
        monitor_endpoints(config_file)
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)