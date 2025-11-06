import requests
import json

def test_job_search():
    """
    Calls the /jobs/search endpoint of the local server and prints the response.
    """
    base_url = "https://adzuna-mcp-server-236255620233.us-central1.run.app"
    # base_url = "http://localhost:7000"
    endpoint = "/jobs/search"
    
    # Parameters for the job search
    params = {
        "what": "python developer",
        "where": "singapore",
        "country": "sg"
    }
    
    try:
        # Make the GET request
        response = requests.get(f"{base_url}{endpoint}", params=params)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse the JSON response
        data = response.json()
        
        # Print the formatted JSON response
        print(json.dumps(data, indent=2))
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    except json.JSONDecodeError:
        print("Failed to decode JSON response.")

if __name__ == "__main__":
    test_job_search()
