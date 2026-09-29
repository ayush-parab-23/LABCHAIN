import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Flask Security settings
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'labchain.db').replace('\\', '/')}"
    )


    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secure Upload Settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    ALLOWED_EXTENSIONS = {"pdf"}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB limit

    # Blockchain Configuration
    BLOCKCHAIN_RPC_URL = os.environ.get("BLOCKCHAIN_RPC_URL", "http://127.0.0.1:8545")
    CONTRACT_INFO_PATH = os.path.join(BASE_DIR, "blockchain", "contract_info.json")
    
    # Dev-only default Hardhat private key (Account #0)
    OWNER_PRIVATE_KEY = os.environ.get(
        "PRIVATE_KEY",
        "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
    )
