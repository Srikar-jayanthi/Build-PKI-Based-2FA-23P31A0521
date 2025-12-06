# scripts/log_2fa_cron.py
import os
import datetime
import base64
import pyotp

# Use absolute path for Docker consistency
SEED_FILE = "/data/seed.txt"

def main():
    if not os.path.exists(SEED_FILE):
        return

    try:
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()

        # Convert Hex -> Bytes -> Base32
        seed_bytes = bytes.fromhex(hex_seed)
        base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
        
        totp = pyotp.TOTP(base32_seed, digits=6, interval=30, digest='sha1')
        code = totp.now()
        
        # UTC Timestamp
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        timestamp = now_utc.strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"{timestamp} - 2FA Code: {code}")

    except Exception as e:
        print(f"Cron Error: {e}")

if __name__ == "__main__":
    main()
    