import os
import requests
import json
from typing import List, Dict, Any

def get_env_token(var_name: str) -> str:
    """Get sensitive token from environment variable or raise an error."""
    token = os.getenv(var_name)
    if not token:
        raise EnvironmentError(f"Environment variable '{var_name}' is not set.")
    return token

def get_tiktok_orders(limit: int = 10, status: str = "awaiting_fulfillment") -> List[Dict[str, Any]]:
    """
    Fetch orders from TikTok Seller Center API.

    Args:
        limit (int): Number of orders to fetch (default: 10).
        status (str): Status filter for orders (default: 'awaiting_fulfillment').

    Returns:
        List[Dict[str, Any]]: List of order dictionaries, or empty list on failure.
    """
    TIKTOK_ACCESS_TOKEN = get_env_token("TIKTOK_ACCESS_TOKEN")
    TIKTOK_API_URL = "https://api.tiktokglobal.com/orders"

    headers = {
        "Authorization": f"Bearer {TIKTOK_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    params = {
        "status": status,
        "limit": limit
    }
    try:
        response = requests.get(TIKTOK_API_URL, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get("orders", [])
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] HTTP Request failed: {e}")
    except ValueError:
        print("[ERROR] Failed to parse JSON response.")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
    return []

if __name__ == "__main__":
    orders = get_tiktok_orders()
    print(json.dumps(orders, indent=4))
