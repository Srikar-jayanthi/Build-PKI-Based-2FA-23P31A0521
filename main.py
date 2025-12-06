# main.py
import os
import base64
import time
import platform
from fastapi import FastAPI, Response
from pydantic import BaseModel
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import pyotp

app = FastAPI()

# ---------------- CONFIGURATION ----------------
# Smart path handling: Windows local dev vs Docker Linux
if platform.system() == "Windows":
    DATA_DIR = "data"  # Local folder for Windows
else:
    DATA_DIR = "/data" # Production folder for Docker

SEED_FILE = os.path.join(DATA_DIR, "seed.txt")
PRIVATE_KEY_PATH = "student_private.pem"

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------- MODELS ----------------
class SeedRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str

# ---------------- HELPERS ----------------
def get_hex_seed():
    """Read the decrypted seed from the file system."""
    if not os.path.exists(SEED_FILE):
        return None
    try:
        with open(SEED_FILE, "r") as f:
            return f.read().strip()
    except Exception:
        return None

def get_totp_object(hex_seed: str):
    """Convert Hex Seed -> Base32 -> TOTP Object"""
    # 1. Hex to Bytes
    seed_bytes = bytes.fromhex(hex_seed)
    # 2. Bytes to Base32 (Required by TOTP standard)
    base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
    # 3. Create TOTP object (SHA1, 6 digits, 30s interval)
    return pyotp.TOTP(base32_seed, digits=6, interval=30, digest='sha1')

# ---------------- ENDPOINTS ----------------

@app.post("/decrypt-seed")
async def decrypt_seed(request: SeedRequest):
    try:
        # 1. Load Private Key
        if not os.path.exists(PRIVATE_KEY_PATH):
            return Response(content='{"error": "Private key not found"}', status_code=500, media_type="application/json")
            
        with open(PRIVATE_KEY_PATH, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(), password=None
            )

        # 2. Decode Base64 input
        encrypted_bytes = base64.b64decode(request.encrypted_seed)

        # 3. Decrypt (RSA-OAEP, SHA256, MGF1)
        decrypted_bytes = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        hex_seed = decrypted_bytes.decode('utf-8')

        # 4. Validate Format (Must be 64-char hex)
        if len(hex_seed) != 64:
            raise ValueError("Invalid seed length")
        
        # 5. Save to Persistent Storage
        with open(SEED_FILE, "w") as f:
            f.write(hex_seed)

        return {"status": "ok"}

    except Exception as e:
        print(f"Decryption Error: {e}")
        return Response(content='{"error": "Decryption failed"}', status_code=500, media_type="application/json")

@app.get("/generate-2fa")
async def generate_2fa():
    hex_seed = get_hex_seed()
    if not hex_seed:
        return Response(content='{"error": "Seed not decrypted yet"}', status_code=500, media_type="application/json")

    totp = get_totp_object(hex_seed)
    code = totp.now()
    remaining_seconds = 30 - (int(time.time()) % 30)

    return {"code": code, "valid_for": remaining_seconds}

@app.post("/verify-2fa")
async def verify_2fa(request: VerifyRequest):
    if not request.code:
        return Response(content='{"error": "Missing code"}', status_code=400, media_type="application/json")
        
    hex_seed = get_hex_seed()
    if not hex_seed:
        return Response(content='{"error": "Seed not decrypted yet"}', status_code=500, media_type="application/json")

    totp = get_totp_object(hex_seed)
    
    # Check current code with ±1 period tolerance (±30 seconds)
    is_valid = totp.verify(request.code, valid_window=1)

    return {"valid": is_valid}