# TikTok to Amazon MCF Automation

This repository provides a robust Python automation pipeline for integrating TikTok Seller Center orders with Amazon MCF (Multi-Channel Fulfillment), allowing you to:

- Fetch new orders from TikTok Seller Center
- Consolidate and create a single Amazon MCF order for all TikTok orders
- Track Amazon fulfillment status and sync updates back to TikTok

## Folder Structure

```
MCF/
│
├── TiktokOrders/
│   ├── tiktok_orders.py            # Fetch orders from TikTok Seller Center
│   ├── consolidate_and_mcf.py      # Consolidate TikTok orders & create Amazon MCF order
│   └── fulfillment_sync.py         # Track Amazon fulfillment & update TikTok order status
│
└── main.py                         # Orchestrates the full workflow
```

---

## How It Works

1. **Fetch TikTok Orders:**  
   Retrieves orders from TikTok using API credentials.

2. **Consolidate & Place Amazon MCF Order:**  
   Combines all TikTok orders into one order and sends it to Amazon MCF.

3. **Track Fulfillment & Update TikTok:**  
   Checks Amazon fulfillment status and posts tracking/status updates back to TikTok.

The main.py script orchestrates these steps in sequence.

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/XeonIsh/MCF.git
cd MCF
```

### 2. Install Python Requirements

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables

Export your credentials before running scripts (in your shell or use a `.env` manager):

```bash
export TIKTOK_ACCESS_TOKEN="your_tiktok_access_token"
export AMAZON_ACCESS_TOKEN="your_amazon_access_token"
export AMAZON_SELLER_ID="your_seller_id"
export AMAZON_MARKETPLACE_ID="your_marketplace_id"
```

### 4. Run the Automation

```bash
python main.py
```

---

## File Descriptions

- `TiktokOrders/tiktok_orders.py`  
  Fetches new TikTok orders.

- `TiktokOrders/consolidate_and_mcf.py`  
  Consolidates TikTok orders and places a single Amazon MCF order.

- `TiktokOrders/fulfillment_sync.py`  
  Tracks Amazon fulfillment and updates TikTok with status/tracking.

- `main.py`  
  Runs the whole workflow in order.

---

## Customization & Extending

- Modular design—add more integrations or logic as needed.
- Each script can be run independently for testing or troubleshooting.

---

## Requirements

- Python 3.7+
- [requests](https://pypi.org/project/requests/)

---

## License

MIT License (see [LICENSE](LICENSE) file)

---

**Questions or contributions?**  
Open an issue or pull request on [GitHub](https://github.com/XeonIsh/MCF).
