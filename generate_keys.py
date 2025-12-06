# generate_keys.py
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

def generate_keys():
    print("Generating 4096-bit RSA keys... this may take a moment.")
    
    # 1. Generate Private Key (4096 bits)
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096
    )

    # 2. Save Private Key (PEM)
    with open("student_private.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # 3. Save Public Key (PEM)
    public_key = private_key.public_key()
    with open("student_public.pem", "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    print("✅ Keys generated successfully: student_private.pem and student_public.pem")

if __name__ == "__main__":
    generate_keys()