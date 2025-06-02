import os
import requests
import json
from typing import Dict, Any, Optional

def get_env_token(var_name: str) -> str:
    """Get sensitive token from environment variable or raise an error."""
    token = os.getenv(var_name)
    if not token:
        raise EnvironmentError(f"Environment variable '{var_name}' is not set.")
    return token

def get_mcf_fulfillment_status(order_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch Amazon MCF fulfillment status for a given order.

    Args:
        order_id (str): The Amazon order ID.

    Returns:
        Optional[Dict[str, Any]]: JSON response containing order status or None on failure.
    """
    ACCESS_TOKEN = get_env_token("AMAZON_ACCESS_TOKEN")
    TRACKING_ENDPOINT = f"https://sellingpartnerapi.amazon.com/orders/v0/orders/{order_id}"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(TRACKING_ENDPOINT, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] HTTP Request to Amazon failed: {e}")
    except ValueError:
        print("[ERROR] Failed to parse Amazon JSON response.")
    return None

def update_tiktok_order_status(order_id: str, mcf_tracking_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Sync fulfillment status with TikTok Seller Center.

    Args:
        order_id (str): The TikTok order ID.
        mcf_tracking_info (Dict[str, Any]): Amazon fulfillment status dict.

    Returns:
        Optional[Dict[str, Any]]: TikTok status update response or None on failure.
    """
    TIKTOK_ACCESS_TOKEN = get_env_token("TIKTOK_ACCESS_TOKEN")
    TIKTOK_STATUS_UPDATE_ENDPOINT = f"https://api.tiktokglobal.com/orders/{order_id}/status"

    headers = {
        "Authorization": f"Bearer {TIKTOK_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    # Validate expected Amazon status fields
    status = mcf_tracking_info.get("status")
    tracking_number = mcf_tracking_info.get("trackingNumber") or mcf_tracking_info.get("tracking_number")

    if not status or not tracking_number:
        print("[ERROR] Missing status or tracking number in Amazon response.")
        return None

    status_payload = {
        "status": status,
        "tracking_number": tracking_number
    }

    try:
        response = requests.post(
            TIKTOK_STATUS_UPDATE_ENDPOINT,
            headers=headers,
            data=json.dumps(status_payload),
            timeout=15
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] HTTP Request to TikTok failed: {e}")
    except ValueError:
        print("[ERROR] Failed to parse TikTok JSON response.")
    return None

def create_consolidated_mcf_order(tiktok_orders):
    """
    Consolidate ONLY unfulfilled TikTok orders and create a single Amazon MCF order.
    Orders with a status of 'fulfilled', 'shipped', or 'complete' will be excluded.
    """
    # Filter out orders that are already fulfilled
    unfulfilled_orders = [
        order for order in tiktok_orders
        if str(order.get("status", "")).lower() not in ("fulfilled", "shipped", "complete")
    ]

    if not unfulfilled_orders:
        print("[INFO] No unfulfilled TikTok orders to consolidate.")
        return None

    # --- Your original consolidation and MCF order creation logic here, using unfulfilled_orders instead of tiktok_orders ---
    # Example (pseudo):
    # payload = build_mcf_payload(unfulfilled_orders)
    # response = post_mcf_order(payload)
    # return response

    print(f"[INFO] Proceeding with {len(unfulfilled_orders)} unfulfilled orders.")
    # For now, just return a mock response to indicate this works:
    return {"orderId": "CONSOLIDATED_MCF_ORDER_ID", "orders": unfulfilled_orders}

if __name__ == "__main__":
    # Replace with your order ID or loop through multiple orders as needed
    order_id = "YOUR_ORDER_ID"
    mcf_status = get_mcf_fulfillment_status(order_id)
    if mcf_status:
        sync_tiktok_status = update_tiktok_order_status(order_id, mcf_status)
        print(json.dumps(sync_tiktok_status, indent=4))
    else:
        print("[INFO] Could not retrieve Amazon fulfillment status.")
