import os
import logging
from sp_api.api import Inventory, Listings
from sp_api.base import SellingApiException, Marketplaces
from tiktok_orders import fetch_new_tiktok_orders  # Adjust this import if needed

# Set up logging
logging.basicConfig(level=logging.INFO)

# Amazon credentials from environment
REFRESH_TOKEN = os.environ.get('AMAZON_REFRESH_TOKEN')
CLIENT_ID = os.environ.get('AMAZON_CLIENT_ID')
CLIENT_SECRET = os.environ.get('AMAZON_CLIENT_SECRET')
AWS_ACCESS_KEY = os.environ.get('AMAZON_AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AMAZON_AWS_SECRET_KEY')
ROLE_ARN = os.environ.get('AMAZON_ROLE_ARN')
MARKETPLACE = os.environ.get('AMAZON_MARKETPLACE', 'US')

MARKETPLACE_MAP = {
    "US": Marketplaces.US,
    "CA": Marketplaces.CA,
    "UK": Marketplaces.UK,
    "DE": Marketplaces.DE,
    "FR": Marketplaces.FR,
    # Add more as needed
}

def get_marketplace():
    return MARKETPLACE_MAP.get(MARKETPLACE, Marketplaces.US)

def main():
    # 1. Fetch new TikTok orders
    tiktok_orders = fetch_new_tiktok_orders()  # Must return list of orders with items (sku, quantity)
    if not tiktok_orders:
        logging.info("No new TikTok orders to process.")
        return

    # 2. Consolidate TikTok orders (aggregate items by SKU)
    consolidated_items = {}
    order_sku_map = {}  # Map order_id to SKUs so we can track fulfillment per order
    for order in tiktok_orders:
        order_id = order.get("order_id")
        for item in order.get("items", []):
            sku = item.get("sku")
            qty = item.get("quantity", 0)
            if not sku or qty <= 0:
                logging.warning(f"Invalid TikTok item: {item}")
                continue
            consolidated_items[sku] = consolidated_items.get(sku, 0) + qty
            if order_id:
                if order_id not in order_sku_map:
                    order_sku_map[order_id] = []
                order_sku_map[order_id].append(sku)

    if not consolidated_items:
        logging.info("No valid items to fulfill.")
        return

    # 3. Place Amazon MCF order (pseudo-code, adapt to your actual MCF logic)
    amazon_order_success = True
    try:
        # Prepare order payload as needed for your Amazon MCF integration
        order_payload = [{"sku": sku, "quantity": qty} for sku, qty in consolidated_items.items()]
        # Example: place_mcf_order(order_payload)
        # If any error, set amazon_order_success = False
        logging.info(f"Placed Amazon MCF order: {order_payload}")
    except Exception as e:
        logging.error(f"Failed to place Amazon MCF order: {e}")
        amazon_order_success = False

    # 4. If MCF order succeeded, update inventory for fulfilled SKUs
    if amazon_order_success:
        inv = Inventory(
            refresh_token=REFRESH_TOKEN,
            lwa_app_id=CLIENT_ID,
            lwa_client_secret=CLIENT_SECRET,
            aws_access_key=AWS_ACCESS_KEY,
            aws_secret_key=AWS_SECRET_KEY,
            role_arn=ROLE_ARN,
            marketplace=get_marketplace(),
        )
        listings = Listings(
            refresh_token=REFRESH_TOKEN,
            lwa_app_id=CLIENT_ID,
            lwa_client_secret=CLIENT_SECRET,
            aws_access_key=AWS_ACCESS_KEY,
            aws_secret_key=AWS_SECRET_KEY,
            role_arn=ROLE_ARN,
            marketplace=get_marketplace(),
        )

        unmatched_skus = []
        failed_order_ids = set()
        for sku, to_deduct in consolidated_items.items():
            try:
                logging.info(f"Updating Amazon inventory for SKU {sku}: deducting {to_deduct}")
                r = inv.get_inventory_summary(sellerSkus=[sku])
                summaries = r.payload.get("inventorySummaries", [])
                if not summaries:
                    logging.error(f"SKU '{sku}' from TikTok orders was not found in Amazon inventory! Cannot update inventory for this SKU.")
                    unmatched_skus.append(sku)
                    # Add all orders referencing this SKU to failed list
                    for oid, sku_list in order_sku_map.items():
                        if sku in sku_list:
                            failed_order_ids.add(oid)
                    continue
                current_qty = summaries[0]["totalQuantity"]
                new_qty = max(0, current_qty - to_deduct)
                patch_body = {
                    "productType": "PRODUCT",
                    "patches": [
                        {
                            "op": "replace",
                            "path": "/attributes/quantity",
                            "value": [{"value": int(new_qty)}]
                        }
                    ]
                }
                try:
                    listings.patch_listing_item(sku=sku, body=patch_body)
                    logging.info(f"Successfully updated inventory for {sku}: {current_qty} -> {new_qty}")
                except Exception as e:
                    logging.error(f"Failed to update inventory for SKU {sku}: {e}")
                    # Add all orders referencing this SKU to failed list
                    for oid, sku_list in order_sku_map.items():
                        if sku in sku_list:
                            failed_order_ids.add(oid)
            except SellingApiException as e:
                logging.error(f"Amazon SP-API error for SKU {sku}: {e}")
                for oid, sku_list in order_sku_map.items():
                    if sku in sku_list:
                        failed_order_ids.add(oid)
            except Exception as e:
                logging.error(f"Error updating inventory for SKU {sku}: {e}")
                for oid, sku_list in order_sku_map.items():
                    if sku in sku_list:
                        failed_order_ids.add(oid)

        if unmatched_skus:
            logging.error(f"Failed to match the following SKUs to Amazon inventory: {unmatched_skus}")

        if failed_order_ids:
            logging.error(f"{len(failed_order_ids)} TikTok orders were not fulfilled in Amazon due to errors: {list(failed_order_ids)}")
        else:
            logging.info("All TikTok orders were successfully fulfilled and inventory updated in Amazon.")

    else:
        logging.warning("Amazon order not placed; inventory not updated.")

if __name__ == "__main__":
    main()
