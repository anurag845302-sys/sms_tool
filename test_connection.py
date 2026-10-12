# file: test_connection.py, target: Python 3.10+
import requests

API_KEY = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE4MjMzMzQwNTUsImlhdCI6MTc5MTc5ODA1NSwicmF5IjoiM2I3NWVkZDUwMzU0ZjU1ODNkNjNmMjEzZTJkZTNkZDciLCJzdWIiOjQ2MTY3NDh9.toWh5Vb9DbCZk_B1Bb11q36H4u_wa8aeT8Oln79-S_MUsDcOSXx6rnfozaKW38CB8dI8m0u2r9wEGwM2jZG0tUjdpfh7R6N3MSxQY5JYRpJ3rE4guOBR2n8Mvu6Hkhw5avJNQmcn7ldjuWV6pXvvK5kkgWvD9va5sMeSMG2PZBIGwJHzNFMMLfZ01Qgj6ha2vKUJ2Su0-RQJmlvNpWjVdvfnuzXnsPSji_KQzquiWx1N23tfbkwszpilU5uCcOHytGr5xxfxI4AoJs5Un937M1jin1ZstKMsJdAFCIIYirNiGefFNv50RjMHrc2aiBxrzbZ3OfEV7nyCTkECVtWz6A"
URL = "https://5sim.net/v1/user/profile"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
}

try:
    response = requests.get(URL, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("Connection Successful!")
        print(f"Wallet Balance: {data.get('balance')}")
    else:
        print(f"Connection Failed. Status Code: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")