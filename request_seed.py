# request_seed.py
import requests
import json
import os

# CONFIGURATION
API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"
REPO_URL = "https://github.com/Srikar-jayanthi/Build-PKI-Based-2FA-23P31A0521"
STUDENT_ID = "23P31A0521" 

def get_seed():
    print(f"Reading public key for {STUDENT_ID}...")
    
    if not os.path.exists("student_public.pem"):
        print("❌ Error: student_public.pem not found.")
        return

    with open("student_public.pem", "r") as f:
        public_key_content = f.read()

    # The API expects the key to be formatted with explicit newlines if sent in JSON,
    # but usually, standard string transmission works if the backend handles it.
    # Let's send it as read from the file.

    payload = {
        "student_id": STUDENT_ID,
        "github_repo_url": REPO_URL,
        "public_key": public_key_content
    }

    print("Sending request to Instructor API...")
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            if "encrypted_seed" in data:
                seed = data["encrypted_seed"]
                with open("encrypted_seed.txt", "w") as f:
                    f.write(seed)
                print("✅ Success! Encrypted seed saved to 'encrypted_seed.txt'")
                print("⚠️  DO NOT COMMIT encrypted_seed.txt TO GIT!")
            else:
                print("❌ API returned 200 but no seed found:", data)
        else:
            print(f"❌ Failed. Status: {response.status_code}")
            print("Response:", response.text)
            
    except Exception as e:
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    get_seed()