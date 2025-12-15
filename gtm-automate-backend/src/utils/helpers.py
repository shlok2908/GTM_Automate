"""
Helper utilities for GTM automation
Provides logging setup, retry logic, and other helper functions
"""
import logging
import time
from datetime import datetime
from functools import wraps
from typing import Callable, Any, Dict
from pathlib import Path


def setup_logging(log_level: str = 'INFO', log_file: str = None):
    """
    Setup logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file (optional)
    """
    # Create logs directory if it doesn't exist
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Setup handlers
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=handlers
    )


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator to retry a function on failure with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logging.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {current_delay}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logging.error(f"All {max_retries} retry attempts failed for {func.__name__}")
            
            raise last_exception
        
        return wrapper
    return decorator


def generate_workspace_name(prefix: str = "AutoGen") -> str:
    """
    Generate a unique workspace name with timestamp
    
    Args:
        prefix: Prefix for workspace name
        
    Returns:
        Generated workspace name
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}"


def format_summary(stats: Dict[str, Any]) -> str:
    """
    Format execution summary as a short, readable string
    
    Args:
        stats: Dictionary containing execution statistics
        
    Returns:
        Formatted short summary string
    """
    workspace_name = stats.get('workspace_name') or 'N/A'
    workspace_id = stats.get('workspace_id') or 'N/A'
    workspace_url = stats.get('workspace_url') or 'N/A'

    variables_created = stats.get('variables_created', 0)
    triggers_created = stats.get('triggers_created', 0)
    tags_created = stats.get('tags_created', 0)

    status = stats.get('status', 'UNKNOWN')
    duration = stats.get('duration', 'N/A')

    summary_lines = []
    summary_lines.append(f"Status: {status} (took {duration})")
    summary_lines.append(
        f"Created => Variables: {variables_created}, Triggers: {triggers_created}, Tags: {tags_created}"
    )
    summary_lines.append(
        f"Workspace => {workspace_name} (ID: {workspace_id})"
    )
    summary_lines.append(f"Workspace URL: {workspace_url}")

    errors = stats.get('errors') or []
    if errors:
        summary_lines.append(f"Errors: {len(errors)}")
        for err in errors:
            summary_lines.append(f"- {err}")

    return "\n".join(["", *summary_lines, ""])  # leading/trailing blank line for readability


def validate_file_path(file_path: str, allowed_extensions: set = None) -> bool:
    """
    Validate file path exists and has allowed extension
    
    Args:
        file_path: Path to file
        allowed_extensions: Set of allowed file extensions (e.g., {'.json', '.xlsx'})
        
    Returns:
        True if valid
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file extension not allowed
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if allowed_extensions and path.suffix.lower() not in allowed_extensions:
        raise ValueError(
            f"Invalid file extension: {path.suffix}. "
            f"Allowed: {', '.join(allowed_extensions)}"
        )
    
    return True


def create_trigger_id_map(triggers: list) -> Dict[str, str]:
    """
    Create a mapping of trigger names to trigger IDs
    
    Args:
        triggers: List of created trigger objects from GTM API
        
    Returns:
        Dictionary mapping trigger names to IDs
    """
    return {trigger['name']: trigger['triggerId'] for trigger in triggers}
