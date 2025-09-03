from cryptography.fernet import Fernet
import secrets
fernet_key = Fernet.generate_key().decode()
print(f"AIRFLOW__CORE__FERNET_KEY={fernet_key}")
print(f"AIRFLOW__WEBSERVER__SECRET_KEY={secrets.token_hex(16)}")