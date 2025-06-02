from TiktokOrders.tiktok_orders import get_tiktok_orders
from TiktokOrders.consolidate_and_mcf import create_consolidated_mcf_order
from TiktokOrders.fulfillment_sync import get_mcf_fulfillment_status, update_tiktok_order_status
import json

def main():
    # Step 1: Fetch TikTok orders
    tiktok_orders = get_tiktok_orders()
    if not tiktok_orders:
        print("[INFO] No TikTok orders to process.")
        return

    # Only work with unfulfilled orders
    unfulfilled_orders = [
        order for order in tiktok_orders
        if str(order.get("status", "")).lower() not in ("fulfilled", "shipped", "complete")
    ]
    if not unfulfilled_orders:
        print("[INFO] No unfulfilled TikTok orders to process.")
        return

    # Step 2: Consolidate and create Amazon MCF order
    mcf_response = create_consolidated_mcf_order(unfulfilled_orders)
    if not mcf_response or "orderId" not in mcf_response:
        print("[ERROR] Failed to create Amazon MCF order.")
        return

    amazon_order_id = mcf_response["orderId"]

    # Step 3: Track Amazon fulfillment & sync back to TikTok
    mcf_status = get_mcf_fulfillment_status(amazon_order_id)
    if not mcf_status:
        print("[ERROR] Could not retrieve Amazon fulfillment status.")
        return

    for tiktok_order in unfulfilled_orders:
        tiktok_order_id = tiktok_order.get("order_id") or tiktok_order.get("id")
        if not tiktok_order_id:
            print("[WARNING] TikTok order missing ID, skipping...")
            continue
        update_result = update_tiktok_order_status(tiktok_order_id, mcf_status)
        print(f"[INFO] Updated TikTok order {tiktok_order_id}:")
        print(json.dumps(update_result, indent=4))

if __name__ == "__main__":
    main()
