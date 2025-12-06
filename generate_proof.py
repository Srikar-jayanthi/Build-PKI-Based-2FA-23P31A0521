# generate_proof.py
import subprocess
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

def generate_proof():
    print("Generating submission proof...")
    
    # 1. Get current git commit hash
    try:
        # Get the hash of the HEAD commit
        commit_hash = subprocess.check_output(['git', 'log', '-1', '--format=%H']).strip().decode('ascii')
        print(f"Commit Hash: {commit_hash}")
    except Exception as e:
        print(f"❌ Error getting git hash: {e}")
        return

    # 2. Sign with Student Private Key (RSA-PSS)
    try:
        with open("student_private.pem", "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)
            
        signature = private_key.sign(
            commit_hash.encode('utf-8'), # Sign the ASCII bytes
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
    except FileNotFoundError:
        print("❌ student_private.pem not found!")
        return

    # 3. Encrypt Signature with Instructor Public Key (RSA-OAEP)
    try:
        with open("instructor_public.pem", "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())

        encrypted_signature = public_key.encrypt(
            signature,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # 4. Output Base64
        b64_sig = base64.b64encode(encrypted_signature).decode('utf-8')
        print("\nSUCCESS! Here is your Encrypted Signature (Copy this single line):")
        print("-" * 60)
        print(b64_sig)
        print("-" * 60)
        
    except FileNotFoundError:
        print("❌ instructor_public.pem not found! Please download it from the course dashboard.")
        return

if __name__ == "__main__":
    generate_proof()