import json
from pathlib import Path
import logging

# Setup basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)


def migrate(input_file: str, output_dir: str):
    input_path = Path(input_file)
    output_path = Path(output_dir)

    if not input_path.exists():
        log.error(f"Input file '{input_file}' not found. Nothing to migrate.")
        return

    log.info(f"Starting migration from {input_file} to {output_dir}...")
    output_path.mkdir(parents=True, exist_ok=True)

    try:
        with open(input_path, "r") as f:
            receipts = json.load(f)
    except json.JSONDecodeError:
        log.error(f"Failed to decode JSON from {input_file}. File might be corrupt.")
        return

    if not isinstance(receipts, list):
        log.error("Input JSON is not a list of receipts.")
        return

    migrated_count = 0
    for receipt in receipts:
        receipt_id = receipt.get("receipt_id")
        if not receipt_id:
            log.warning("Found receipt without receipt_id, skipping.")
            continue

        # Add default values for new fields if they don't exist in the old data
        if "store_name" not in receipt:
            receipt["store_name"] = None
        if "store_id" not in receipt:
            # Try to extract from ID: banner~store~date...
            parts = receipt_id.split("~")
            receipt["store_id"] = parts[1] if len(parts) >= 2 else None
        if "order_type" not in receipt:
            receipt["order_type"] = "In-Store"  # Default for old data

        receipt_file = output_path / f"{receipt_id}.json"

        try:
            with open(receipt_file, "w") as f:
                json.dump(receipt, f, indent=4)
            migrated_count += 1
            log.debug(f"Migrated {receipt_id}")
        except Exception as e:
            log.error(f"Failed to write {receipt_id}: {e}")

    log.info(f"Migration complete. Migrated {migrated_count} receipts.")
    log.info(
        f"You can now safely delete '{input_file}' if you are satisfied with the results."
    )


if __name__ == "__main__":
    migrate("order_data.json", "output/receipts")
