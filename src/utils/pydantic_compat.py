"""
Pydantic compatibility utilities for handling different versions

This module helps suppress or handle compatibility warnings when mixing
Pydantic V1 and V2 models in the application.
"""

import warnings
import os

# Set environment variable to suppress warnings
os.environ["PYDANTIC_WARN_ABOUT_USED_DEPRECATED_VERSION"] = "0"

# Filter out the specific warning about mixing V1 and V2 models
warnings.filterwarnings(
    "ignore", 
    message="Mixing V1 models and V2 models.*", 
    category=UserWarning
)

def init():
    """
    Initialize compatibility settings.
    Call this early in your application to suppress warnings.
    """
    # The setting of environment variables and warning filters above
    # happens at import time, so this is just a no-op to make the
    # intent clear when this is called.
    pass
