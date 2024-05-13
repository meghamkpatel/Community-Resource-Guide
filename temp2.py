import requests

# Test Case: Invalid API Key
def test_invalid_api_key(api_key):
    url = f"https://www.googleapis.com/customsearch/v1?q=test&key={api_key}&num=1"
    response = requests.get(url)
    print("Invalid API Key - Response Status Code:", response.status_code)
    print("Response Content:", response.content.decode("utf-8"))

# Test Case: Restricted API Key
def test_restricted_api_key(api_key):
    url = f"https://www.googleapis.com/customsearch/v1?q=test&key={api_key}&num=1"
    response = requests.get(url)
    print("Restricted API Key - Response Status Code:", response.status_code)
    print("Response Content:", response.content.decode("utf-8"))

# Test Case: Quota Limits
def test_quota_limits(api_key):
    url = f"https://www.googleapis.com/customsearch/v1?q=test&key={api_key}&num=1"
    response = requests.get(url)
    print("Quota Limits - Response Status Code:", response.status_code)
    print("Response Content:", response.content.decode("utf-8"))

# Test Case: Incorrect API Request
def test_incorrect_api_request(api_key):
    url = f"https://www.googleapis.com/customsearch/v1?q=test&num=1"  # Missing API key
    response = requests.get(url)
    print("Incorrect API Request - Response Status Code:", response.status_code)
    print("Response Content:", response.content.decode("utf-8"))

# Test Case: Network Issues
def test_network_issues(api_key):
    url = f"https://www.googleapis.com/customsearch/v1?q=test&key={api_key}&num=1"
    response = requests.get(url)
    print("Network Issues - Response Status Code:", response.status_code)
    print("Response Content:", response.content.decode("utf-8"))

# Test Case: Server-Side Errors
def test_server_side_errors(api_key):
    url = f"https://www.googleapis.com/customsearch/v1?q=test&key={api_key}&num=1"
    response = requests.get(url)
    print("Server-Side Errors - Response Status Code:", response.status_code)
    print("Response Content:", response.content.decode("utf-8"))

# Test Case: API Changes
def test_api_changes(api_key):
    url = f"https://www.googleapis.com/customsearch/v1?q=test&key={api_key}&num=1"
    response = requests.get(url)
    print("API Changes - Response Status Code:", response.status_code)
    print("Response Content:", response.content.decode("utf-8"))

if __name__ == "__main__":
    # Replace 'YOUR_API_KEY' with your actual API key obtained from the Google Cloud Console
    api_key = ""

    test_invalid_api_key(api_key)
    test_restricted_api_key(api_key)
    test_quota_limits(api_key)
    test_incorrect_api_request(api_key)
    test_network_issues(api_key)
    test_server_side_errors(api_key)
    test_api_changes(api_key)
