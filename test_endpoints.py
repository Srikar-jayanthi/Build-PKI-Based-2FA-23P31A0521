# test_endpoints.py
import requests
import json
import time

# CRITICAL: Docker is running on port 8080
BASE_URL = "http://127.0.0.1:8080"

def run_tests():
    print(f"🚀 STARTING TESTS against {BASE_URL}...")
    
    # ---------------------------------------------------------
    # TEST 1: Decrypt the Seed
    # ---------------------------------------------------------
    print("\n[1] Testing /decrypt-seed...")
    try:
        # Check if file exists first
        try:
            with open("encrypted_seed.txt", "r") as f:
                enc_seed = f.read().strip()
        except FileNotFoundError:
            print("❌ Error: encrypted_seed.txt not found! Run request_seed.py first.")
            return

        payload = {"encrypted_seed": enc_seed}
        resp = requests.post(f"{BASE_URL}/decrypt-seed", json=payload)
        
        if resp.status_code == 200:
            print("✅ Decryption SUCCESS!")
        else:
            print(f"❌ Decryption FAILED: {resp.text}")
            return
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION ERROR: Could not reach {BASE_URL}. Is Docker running?")
        return

    # ---------------------------------------------------------
    # TEST 2: Generate TOTP
    # ---------------------------------------------------------
    print("\n[2] Testing /generate-2fa...")
    resp = requests.get(f"{BASE_URL}/generate-2fa")
    
    code = ""
    if resp.status_code == 200:
        data = resp.json()
        code = data.get("code")
        valid_for = data.get("valid_for")
        print(f"✅ Generated Code: {code}")
        print(f"   Valid for: {valid_for} seconds")
    else:
        print(f"❌ Generation FAILED: {resp.text}")
        return

    # ---------------------------------------------------------
    # TEST 3: Verify TOTP
    # ---------------------------------------------------------
    print("\n[3] Testing /verify-2fa...")
    payload = {"code": code}
    resp = requests.post(f"{BASE_URL}/verify-2fa", json=payload)
    
    if resp.status_code == 200:
        result = resp.json()
        if result.get("valid") is True:
            print("✅ Verification SUCCESS! The code is valid.")
        else:
            print("❌ Verification returned False. Something is wrong.")
    else:
        print(f"❌ Verification Endpoint Failed: {resp.text}")

if __name__ == "__main__":
    run_tests()