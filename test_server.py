# filepath: c:\Users\ernes\Dropbox\zhihao\NTU_DS_AI\Capstone\adzuna_api\test_server.py
import requests

base_url = "http://localhost:8000"

# Test health check
print("Testing Health Check...")
response = requests.get(f"{base_url}/health")
print("Health Check:", response.json())

# Test search jobs
print("\nTesting Job Search...")
params = {"what": "data scientist", "where": "singapore", "results_per_page": 5}
response = requests.get(f"{base_url}/jobs/search", params=params)
print("Search Jobs Status:", response.status_code)
if response.status_code == 200:
    data = response.json()
    print(f"Found {data.get('count', 0)} jobs")
    if data.get('results'):
        job = data['results'][0]
        print(f"Sample job: {job.get('title')} at {job.get('company', {}).get('display_name')}")
else:
    print("Search Jobs Error:", response.json())

# Test top companies
print("\nTesting Top Companies...")
params = {"country": "sg"}
response = requests.get(f"{base_url}/jobs/top-companies", params=params)
print("Top Companies Status:", response.status_code)
if response.status_code == 200:
    print("Top Companies Response:", response.json())
else:
    print("Top Companies Error:", response.json())

# Test salary histogram
print("\nTesting Salary Histogram...")
params = {"what": "data scientist", "country": "sg"}
response = requests.get(f"{base_url}/jobs/histogram", params=params)
print("Salary Histogram Status:", response.status_code)
if response.status_code == 200:
    print("Salary Histogram Response:", response.json())
else:
    print("Salary Histogram Error:", response.json())