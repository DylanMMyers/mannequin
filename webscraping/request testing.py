import requests
import json

# The original URL that returns the 307 redirect
url = "https://di.rlcdn.com/api/segment?pid=711444&pdata=type%3Dproduct%2Ccategory_id%3D4860026%2Cproduct_id%3D1142_1940_286%2Cproduct_name%3Dae_long_sleeve_shaker_crew_neck_sweater%2Cpage_brand%3DAE"

# Custom headers (if necessary)
headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': 'https://www.ae.com',
    'Referer': 'https://www.ae.com/',
    'Sec-CH-UA': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    'Sec-CH-UA-Mobile': '?0',
    'Sec-CH-UA-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
}

# Make the request with the custom headers and allow redirects
response = requests.get(url, headers=headers, allow_redirects=True)

# Check if the request was successful
if response.status_code == 200:
    try:
        # Parse the response content as JSON
        data = response.json()
        
        # Optionally save the raw response data as a JSON file
        with open('product_data.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)
        
        print("Data saved successfully to 'product_data.json'.")

    except json.JSONDecodeError:
        print("Failed to parse JSON response.")
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
