# MCF Orchestrator

## Overview

This repository automates the workflow of fetching orders from TikTok Shop, consolidating and fulfilling them using Amazon MCF, updating Amazon inventory, and syncing order statuses back to TikTok Shop.

---

## 🚀 New Workflow Steps

**The workflow is now fully orchestrated via `main.py` with improved automation and reliability:**

1. **Fetch TikTok Orders (`TiktokOrders/tiktok_orders.py`):**  
   Retrieves new and unfulfilled orders from TikTok Shop.

2. **Consolidate, Fulfill, and Update Amazon Inventory (`TiktokOrders/consolidate_and_mcf.py`):**  
   - Orders are consolidated by SKU.
   - Fulfillment requests are placed using Amazon MCF.
   - **NEW:** After fulfillment, the script automatically deducts the fulfilled quantities from the corresponding SKUs in your Amazon inventory.  
     _This keeps your Amazon inventory levels in sync with TikTok sales._

3. **Sync Fulfillment Status Back to TikTok (`TiktokOrders/fulfillment_sync.py`):**  
   The status of fulfilled orders is updated in TikTok Shop to reflect their new status, closing the loop.

---

## Error Handling

- If any step fails, the process halts and logs a clear error message indicating which step failed:
  - If fetching TikTok orders fails, no further action is taken.
  - If fulfillment/consolidation or Amazon inventory update fails, syncing back to TikTok does not occur.
  - If updating TikTok order status fails, a specific error is logged.

---

## Orchestration (`main.py`)

The new `main.py` script runs each step in sequence.  
**If any step fails, the workflow stops and reports the specific failure.**

**Example log output:**
```
INFO: Step 1: Fetching TikTok Shop orders...
ERROR: Step 1 failed: Fetching TikTok Orders Failed.
```

---

## How to Run

Simply execute:
```bash
python main.py
```

All steps will be performed in order. Check the logs for status and error messages.

---

## Summary of Changes

- **Amazon inventory is now automatically updated** after fulfilling TikTok orders.
- **Strict step-by-step orchestration**: each phase must succeed before the next begins.
- **Clear error reporting** on failure at any stage.

---

Feel free to reach out for support or to suggest improvements!

---

**Questions or contributions?**  
Open an issue or pull request on [GitHub](https://github.com/XeonIsh/MCF).
