# file: buy_and_get_otp.py, target: Python 3.10+
import requests
import time

API_KEY = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE4MjMzMzQwNTUsImlhdCI6MTc5MTc5ODA1NSwicmF5IjoiM2I3NWVkZDUwMzU0ZjU1ODNkNjNmMjEzZTJkZTNkZDciLCJzdWIiOjQ2MTY3NDh9.toWh5Vb9DbCZk_B1Bb11q36H4u_wa8aeT8Oln79-S_MUsDcOSXx6rnfozaKW38CB8dI8m0u2r9wEGwM2jZG0tUjdpfh7R6N3MSxQY5JYRpJ3rE4guOBR2n8Mvu6Hkhw5avJNQmcn7ldjuWV6pXvvK5kkgWvD9va5sMeSMG2PZBIGwJHzNFMMLfZ01Qgj6ha2vKUJ2Su0-RQJmlvNpWjVdvfnuzXnsPSji_KQzquiWx1N23tfbkwszpilU5uCcOHytGr5xxfxI4AoJs5Un937M1jin1ZstKMsJdAFCIIYirNiGefFNv50RjMHrc2aiBxrzbZ3OfEV7nyCTkECVtWz6A"
BASE_URL = "https://5sim.net/v1/user"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
}

def buy_number(country="colombia", operator="virtual34", service="telegram"):
    """Request a phone number safely with text/json fallback handling."""
    url = f"{BASE_URL}/buy/activation/{country}/{operator}/{service}"
    print(f"Requesting number from operator {operator} ({country})...")
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"[+] Number Acquired: {data.get('phone')}")
            print(f"[+] Order ID: {data.get('id')}")
            return data.get('id'), data.get('phone')
        except requests.exceptions.JSONDecodeError:
            print(f"[-] API Non-JSON Response: {response.text}")
            return None, None
    else:
        print(f"[-] Purchase Failed (Status {response.status_code}): {response.text}")
        return None, None

def cancel_order(order_id):
    """Cancel order to refund funds on timeout."""
    url = f"{BASE_URL}/cancel/{order_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print(f"\n[+] Order {order_id} cancelled successfully. Funds refunded.")
    else:
        print(f"\n[-] Failed to cancel order: {response.text}")

def poll_otp(order_id, timeout=120, interval=5):
    """Poll 5SIM for incoming OTP code."""
    url = f"{BASE_URL}/check/{order_id}"
    print("Waiting for SMS OTP...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            try:
                data = response.json()
                status = data.get('status')
                
                if status == 'RECEIVED':
                    sms_list = data.get('sms', [])
                    if sms_list:
                        code = sms_list[0].get('code')
                        print(f"\n[+] OTP Code Received: {code}")
                        return code
                elif status == 'CANCELLED':
                    print("\n[-] Order was cancelled.")
                    return None
            except requests.exceptions.JSONDecodeError:
                pass
                
        time.sleep(interval)
        print(".", end="", flush=True)
        
    print("\n[-] Timeout waiting for OTP. Cancelling order...")
    cancel_order(order_id)
    return None

if __name__ == "__main__":
    order_id, phone = buy_number(country="colombia", operator="virtual34", service="telegram")
    
    if order_id:
        otp_code = poll_otp(order_id)
        if otp_code:
            print(f"\nFinal Result -> Phone: {phone} | OTP: {otp_code}")