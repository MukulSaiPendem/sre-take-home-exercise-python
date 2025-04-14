# Endpoint Monitoring Tool

Python script to monitor the availability of HTTP endpoints specified in a YAML configuration file. The tool checks endpoints every 15 seconds and reports the cumulative availability percentage by domain.

## Getting Started

1. Clone this repository:
```bash
git clone https://github.com/MukulSaiPendem/sre-take-home-exercise-python.git
cd sre-take-home-exercise-python
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Run it

Run the script with a YAML configuration file as an argument:

```bash
python main.py sample.yaml
```

After running, you'll see something like this every 15 seconds:


```
dev-sre-take-home-exercise-rubric.us-east-1.recruiting-public.fetchrewards.com has 50% availability percentage
---
dev-sre-take-home-exercise-rubric.us-east-1.recruiting-public.fetchrewards.com has 50% availability percentage
---
```

## How it works

1. The script reads a YAML file containing endpoints to monitor
2. It pings each endpoint every 15 seconds
3. If an endpoint returns a 2xx status code within 500ms, it's considered "UP" 
4. It tracks and displays cumulative availability percentage for each domain

### YAML Configuration Format

Your YAML file should look something like this:

```yaml
- name: sample endpoint
  url: https://example.com/api/health
  method: GET
- name: another endpoint
  url: https://api.example.com/status
  method: POST
  headers:
    content-type: application/json
  body: '{"check":"status"}'
```

## Issues Fixed

The original script had a few bugs that I fixed:

1. **Fixed the "NoneType has no attribute 'upper'" error**
   
   The script crashed when a method wasn't specified in the YAML. Added a default:
   ```python
   method = endpoint.get('method', 'GET')  # Default to GET if missing
   ```

2. **Fixed JSON body handling**
   
   The script was having trouble with string JSON bodies. Changed it to:
   ```python
   # For content-type: application/json with string body
   if headers.get('content-type') == 'application/json' and isinstance(body, str):
       response = requests.request(method, url, headers=headers, data=body, timeout=0.5)
   ```

3. **Added response time checking**
   
   Endpoints were only being checked for status code but not response time. Added timing:
   ```python
   start = time.time()
   # Make request
   duration = time.time() - start
   if 200 <= response.status_code < 300 and duration <= 0.5:
       return "UP"
   ```

4. **Fixed domain parsing**
   
   Wasn't properly ignoring port numbers in domains:
   ```python
   domain = endpoint["url"].split("//")[-1].split("/")[0].split(":")[0]
   ```

5. **Made cycles run exactly every 15 seconds**
   
   The original would just sleep 15 seconds, which means the cycle time varied. Fixed:
   ```python
   cycle_start = time.time()
   # Run checks
   elapsed = time.time() - cycle_start
   time.sleep(max(0, 15 - elapsed))
   ```

6. **Better error handling**
   
   Improved exception handling throughout the code

## Testing Results

The script has been thoroughly tested with multiple YAML configurations containing various endpoints across different domains (sample-test-1.yaml file). Ran tests with additional public APIs to verify the script's behavior:

```
# Output from multi-domain testing
www.githubstatus.com has 100% availability percentage
jsonplaceholder.typicode.com has 100% availability percentage
postman-echo.com has 67% availability percentage
httpbin.org has 0% availability percentage
api.open-meteo.com has 50% availability percentage
api.chucknorris.io has 50% availability percentage
---
```

## Requirements

- Python 3.6+
- requests
- PyYAML