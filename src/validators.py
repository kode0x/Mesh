"""
Input validation utilities.

Provides reusable validation logic for project names, API keys, and other inputs.
"""

import re
from typing import Tuple

from config import (
    INVALID_FILENAME_CHARS,
    MIN_PROJECT_NAME_LENGTH,
    MAX_PROJECT_NAME_LENGTH,
)
from exceptions import ValidationError


def validate_project_name(name: str) -> Tuple[bool, str]:
    """
    Validate a project name.
    
    Args:
        name: The project name to validate.
        
    Returns:
        A tuple of (is_valid, error_message).
    """
    name = name.strip()
    
    if not name:
        return False, "Project name cannot be empty"
    
    if len(name) < MIN_PROJECT_NAME_LENGTH or len(name) > MAX_PROJECT_NAME_LENGTH:
        return False, f"Project name must be between {MIN_PROJECT_NAME_LENGTH} and {MAX_PROJECT_NAME_LENGTH} characters"
    
    if re.search(INVALID_FILENAME_CHARS, name):
        return False, "Project name contains invalid characters. Use only letters, numbers, spaces, and basic punctuation"
    
    return True, ""


def validate_api_key(key: str) -> Tuple[bool, str]:
    """
    Validate an API key.
    
    Args:
        key: The API key to validate.
        
    Returns:
        A tuple of (is_valid, error_message).
    """
    key = key.strip()
    
    if not key:
        return False, "API key cannot be empty"
    
    if len(key) < 10:  # Basic check
        return False, "API key appears to be too short"
    
    return True, ""


def validate_not_empty(value: str, field_name: str) -> Tuple[bool, str]:
    """
    Generic validation for non-empty strings.
    
    Args:
        value: The value to validate.
        field_name: The name of the field being validated.
        
    Returns:
        A tuple of (is_valid, error_message).
    """
    if not value or not value.strip():
        return False, f"{field_name} cannot be empty"
    
    return True, ""


def assert_valid_project_name(name: str) -> None:
    """
    Assert that a project name is valid, raising ValidationError if not.
    
    Args:
        name: The project name to validate.
        
    Raises:
        ValidationError: If validation fails.
    """
    is_valid, error_msg = validate_project_name(name)
    if not is_valid:
        raise ValidationError(error_msg)


def assert_valid_api_key(key: str) -> None:
    """
    Assert that an API key is valid, raising ValidationError if not.
    
    Args:
        key: The API key to validate.
        
    Raises:
        ValidationError: If validation fails.
    """
    is_valid, error_msg = validate_api_key(key)
    if not is_valid:
        raise ValidationError(error_msg)
