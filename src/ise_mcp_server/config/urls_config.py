import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..config.settings import logger

def load_urls(file_name='urls.json') -> List[Dict[str, Any]]:
    """
    Load the URLs configuration from a JSON file.
    
    Args:
        file_name: Name of the JSON file with URL definitions.
        
    Returns:
        A list of URL definitions, each as a dictionary.
    """
    # Get the base directory of the package
    base_dir = Path(__file__).resolve().parent.parent
    
    # Try different possible locations for the urls.json file
    possible_paths = [
        base_dir / 'config' / file_name,  # New location in config dir
        base_dir / file_name,             # Old location in package root
    ]
    
    for file_path in possible_paths:
        try:
            with open(file_path, 'r') as f:
                logger.info(f"📂 Loaded URLs configuration from {file_path}")
                return json.load(f)
        except FileNotFoundError:
            # Try the next path
            continue
        except json.JSONDecodeError:
            logger.error(f"❌ Error decoding JSON from {file_path}. Cannot register tools.")
            return []
    
    # If we get here, we didn't find the file in any location
    logger.error(f"❌ URLS file not found in any expected location. Tried: {', '.join(str(p) for p in possible_paths)}")
    return []