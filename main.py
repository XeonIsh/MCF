import logging
from TiktokOrders.tiktok_orders import main as fetch_tiktok_orders
from TiktokOrders.consolidate_and_mcf import main as consolidate_and_fulfill
from TiktokOrders.fulfillment_sync import main as sync_fulfillment_status

def main():
    logging.basicConfig(level=logging.INFO)
    
    # 1. Fetch TikTok Orders
    try:
        logging.info("Step 1: Fetching TikTok Shop orders...")
        result = fetch_tiktok_orders()
        if result is False:
            logging.error("Step 1 failed: Fetching TikTok Orders Failed.")
            return
        logging.info("TikTok Shop orders fetched successfully.")
    except Exception as e:
        logging.error(f"Step 1 failed: Fetching TikTok Orders Failed. Exception: {e}")
        return

    # 2. Consolidate, fulfill, and update Amazon inventory
    try:
        logging.info("Step 2: Consolidating and fulfilling orders + updating Amazon inventory...")
        result = consolidate_and_fulfill()
        if result is False:
            logging.error("Step 2 failed: Fulfilling and Updating Amazon Inventory failed.")
            return
        logging.info("Consolidation and fulfillment complete.")
    except Exception as e:
        logging.error(f"Step 2 failed: Fulfilling and Updating Amazon Inventory failed. Exception: {e}")
        return

    # 3. Sync fulfillment status back to TikTok
    try:
        logging.info("Step 3: Syncing fulfillment status back to TikTok Shop...")
        result = sync_fulfillment_status()
        if result is False:
            logging.error("Step 3 failed: The update in TikTok Shop of fulfilled orders failed.")
            return
        logging.info("Fulfillment status sync to TikTok complete.")
    except Exception as e:
        logging.error(f"Step 3 failed: The update in TikTok Shop of fulfilled orders failed. Exception: {e}")
        return

if __name__ == "__main__":
    main()
