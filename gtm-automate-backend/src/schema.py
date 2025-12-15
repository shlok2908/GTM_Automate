"""
Schema Validation Module
Validates input data structure against JSON schema
"""
import logging
from typing import Dict, List, Any
from jsonschema import validate, ValidationError, Draft7Validator

logger = logging.getLogger(__name__)


# JSON Schema for GTM input data
GTM_INPUT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "variables": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                    "parameter": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "key": {"type": "string"},
                                "type": {"type": "string"},
                                "value": {"type": "string"}
                            },
                            "required": ["key", "type", "value"]
                        }
                    }
                },
                "required": ["name", "type"]
            }
        },
        "triggers": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "type": {"type": "string"},  # Allow any trigger type (web + server-side)
                    "filter": {"type": "array"},
                    "customEventFilter": {"type": "array"},
                    "autoEventFilter": {"type": "array"}
                },
                "required": ["name", "type"]
            }
        },
        "tags": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                    "parameter": {"type": "array"},
                    "firingTriggerId": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "blockingTriggerId": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["name", "type"]
            }
        }
    },
    "required": ["variables", "triggers", "tags"]
}


def validate_input_data(data: Dict) -> bool:
    """
    Validate input data against GTM schema
    
    Args:
        data: Input data dictionary to validate
        
    Returns:
        True if validation passes
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        validate(instance=data, schema=GTM_INPUT_SCHEMA)
        logger.info("✓ Input data validation passed")
        return True
        
    except ValidationError as e:
        logger.error(f"✗ Input data validation failed: {e.message}")
        logger.error(f"  Failed at path: {'.'.join(str(p) for p in e.path)}")
        raise


def validate_trigger_references(data: Dict) -> bool:
    """
    Validate that all trigger references in tags exist in triggers list
    
    Args:
        data: Input data dictionary
        
    Returns:
        True if all references are valid
        
    Raises:
        ValueError: If invalid references found
    """
    # Get all trigger names
    trigger_names = {trigger['name'] for trigger in data.get('triggers', [])}
    
    # Check firing triggers
    invalid_refs = []
    for tag in data.get('tags', []):
        # Check firing triggers
        for trigger_name in tag.get('firingTriggerId', []):
            if trigger_name not in trigger_names:
                invalid_refs.append(f"Tag '{tag['name']}' references non-existent firing trigger '{trigger_name}'")
        
        # Check blocking triggers
        for trigger_name in tag.get('blockingTriggerId', []):
            if trigger_name not in trigger_names:
                invalid_refs.append(f"Tag '{tag['name']}' references non-existent blocking trigger '{trigger_name}'")
    
    if invalid_refs:
        error_msg = "Invalid trigger references found:\n  - " + "\n  - ".join(invalid_refs)
        logger.error(f"✗ {error_msg}")
        raise ValueError(error_msg)
    
    logger.info("✓ All trigger references are valid")
    return True


def validate_all(data: Dict) -> bool:
    """
    Run all validations on input data
    
    Args:
        data: Input data dictionary
        
    Returns:
        True if all validations pass
    """
    validate_input_data(data)
    validate_trigger_references(data)
    return True
