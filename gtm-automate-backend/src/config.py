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
    
    # Service Account Configuration
    SERVICE_ACCOUNT_JSON_PATH = os.getenv(
        'SERVICE_ACCOUNT_JSON_PATH', 
        'config/service_account.json'
    )
    
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
        """Validate that required configuration is present

        Args:
            require_account_id: When True, fail if GTM_ACCOUNT_ID is not set.
            require_container_id: When True, fail if GTM_CONTAINER_ID is not set.
        """
        errors = []

        if require_account_id and not cls.GTM_ACCOUNT_ID:
            errors.append("GTM_ACCOUNT_ID is not set in .env file")

        if require_container_id and not cls.GTM_CONTAINER_ID:
            errors.append("GTM_CONTAINER_ID is not set in .env file")

        if not Path(cls.SERVICE_ACCOUNT_JSON_PATH).exists():
            errors.append(f"Service account file not found: {cls.SERVICE_ACCOUNT_JSON_PATH}")
        
        if errors:
            raise ValueError(f"Configuration errors:\n  - " + "\n  - ".join(errors))
        
        return True
    
    @classmethod
    def get_parent_path(cls):
        """Get the parent path for GTM API calls"""
        return f'accounts/{cls.GTM_ACCOUNT_ID}/containers/{cls.GTM_CONTAINER_ID}'
