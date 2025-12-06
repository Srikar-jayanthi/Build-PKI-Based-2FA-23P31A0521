# Secure PKI-Based 2FA Microservice

This project implements a secure, containerized microservice for Two-Factor Authentication (2FA) using Public Key Infrastructure (PKI). It demonstrates enterprise-grade security practices including RSA-4096 encryption, TOTP generation, and automated auditing via cron jobs.

## Features

- **RSA-4096 Encryption:** Uses RSA/OAEP with SHA-256 to securely decrypt authentication seeds.
- **TOTP Implementation:** Generates time-based one-time passwords (SHA-1, 6 digits, 30s period).
- **Dockerized Architecture:** Multi-stage Docker build with optimized caching and security.
- **Persistent Storage:** Uses Docker volumes to persist sensitive data and logs across container restarts.
- **Automated Auditing:** Background cron job logs valid 2FA codes every minute.

## Prerequisites

- Docker
- Docker Compose

## Setup & Installation

1. **Clone the repository:**

   ```bash
   git clone [https://github.com/Srikar-jayanthi/Build-PKI-Based-2FA-23P31A0521.git](https://github.com/Srikar-jayanthi/Build-PKI-Based-2FA-23P31A0521.git)
   cd Build-PKI-Based-2FA-23P31A0521
   ```

2. **Build and Start the Container:**

   ```bash
   docker-compose up -d --build
   ```

The API server will start on port **8080**.

## API Endpoints

### 1. Decrypt Seed

Decrypts the encrypted seed using the stored student private key and saves it to persistent storage.

- **URL:** `POST /decrypt-seed`
- **Content-Type:** `application/json`
- **Body:**

  ```json
  {
    "encrypted_seed": "BASE64_ENCODED_STRING..."
  }
  ```

### 2. Generate 2FA Code

Returns the current valid TOTP code and remaining validity time.

- **URL:** `GET /generate-2fa`
- **Response:**

  ```json
  {
    "code": "123456",
    "valid_for": 25
  }
  ```

### 3. Verify 2FA Code

Verifies a provided code against the stored seed (allows ±1 period tolerance).

- **URL:** `POST /verify-2fa`
- **Content-Type:** `application/json`
- **Body:**

  ```json
  {
    "code": "123456"
  }
  ```

## Verifying the Cron Job

To check that the background cron job is logging codes correctly (wait ~60 seconds after starting):

```bash
docker exec -it build-pki-based-2fa-23p31a0521-app-1 cat /cron/last_code.txt
```

## Security Disclosure

**Note:** The `student_private.pem` file is included in this repository **explicitly** to satisfy the assignment grading requirements. In a real-world production environment, private keys would never be committed to version control and would be managed via a secrets management service (e.g., AWS Secrets Manager, HashiCorp Vault).
