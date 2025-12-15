"""
Configuration management for GTM Automation
Loads environment variables and provides configuration constants
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for GTM automation"""
    
    # GTM Configuration
    GTM_ACCOUNT_ID = os.getenv('GTM_ACCOUNT_ID', '')
    GTM_CONTAINER_ID = os.getenv('GTM_CONTAINER_ID', '')
    
    # Service Account Configuration (from .env)
    GTM_TYPE = os.getenv("GTM_TYPE")
    GTM_PROJECT_ID = os.getenv("GTM_PROJECT_ID")
    GTM_PRIVATE_KEY_ID = os.getenv("GTM_PRIVATE_KEY_ID")
    GTM_PRIVATE_KEY = os.getenv("GTM_PRIVATE_KEY")
    GTM_CLIENT_EMAIL = os.getenv("GTM_CLIENT_EMAIL")
    GTM_CLIENT_ID = os.getenv("GTM_CLIENT_ID")
    GTM_AUTH_URI = os.getenv("GTM_AUTH_URI")
    GTM_TOKEN_URI = os.getenv("GTM_TOKEN_URI")
    GTM_AUTH_PROVIDER_CERT_URL = os.getenv("GTM_AUTH_PROVIDER_CERT_URL")
    GTM_CLIENT_CERT_URL = os.getenv("GTM_CLIENT_CERT_URL")
    GTM_UNIVERSE_DOMAIN = os.getenv("GTM_UNIVERSE_DOMAIN")

    @classmethod
    def get_service_account_info(cls):
        return {
            "type": cls.GTM_TYPE,
            "project_id": cls.GTM_PROJECT_ID,
            "private_key_id": cls.GTM_PRIVATE_KEY_ID,
            "private_key": cls.GTM_PRIVATE_KEY,
            "client_email": cls.GTM_CLIENT_EMAIL,
            "client_id": cls.GTM_CLIENT_ID,
            "auth_uri": cls.GTM_AUTH_URI,
            "token_uri": cls.GTM_TOKEN_URI,
            "auth_provider_x509_cert_url": cls.GTM_AUTH_PROVIDER_CERT_URL,
            "client_x509_cert_url": cls.GTM_CLIENT_CERT_URL,
            "universe_domain": cls.GTM_UNIVERSE_DOMAIN,
        }
    
    # API Scopes
    GTM_SCOPES = ['https://www.googleapis.com/auth/tagmanager.edit.containers']
    
    # Workspace Configuration
    WORKSPACE_NAME_PREFIX = os.getenv('WORKSPACE_NAME_PREFIX', 'AutoGen')
    
    
    # File Upload Configuration
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'json', 'xlsx', 'xls'}
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    
    @classmethod
    def validate(cls, require_account_id: bool = True, require_container_id: bool = True):
        """Validate that required configuration is present"""
        errors = []
        # Check all required GTM fields
        required_fields = [
            cls.GTM_TYPE, cls.GTM_PROJECT_ID, cls.GTM_PRIVATE_KEY_ID, cls.GTM_PRIVATE_KEY,
            cls.GTM_CLIENT_EMAIL, cls.GTM_CLIENT_ID, cls.GTM_AUTH_URI, cls.GTM_TOKEN_URI,
            cls.GTM_AUTH_PROVIDER_CERT_URL, cls.GTM_CLIENT_CERT_URL, cls.GTM_UNIVERSE_DOMAIN
        ]
        if not all(required_fields):
            errors.append("One or more GTM service account fields are missing in .env")
        if require_account_id and not cls.GTM_ACCOUNT_ID:
            errors.append("GTM_ACCOUNT_ID is not set in .env file")
        if require_container_id and not cls.GTM_CONTAINER_ID:
            errors.append("GTM_CONTAINER_ID is not set in .env file")
        if errors:
            raise ValueError(f"Configuration errors:\n  - " + "\n  - ".join(errors))
        return True
    
    @classmethod
    def get_parent_path(cls):
        """Get the parent path for GTM API calls"""
        return f'accounts/{cls.GTM_ACCOUNT_ID}/containers/{cls.GTM_CONTAINER_ID}'
