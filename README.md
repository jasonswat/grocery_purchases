# Grocery Purchases
Python app to pull grocery purchase history. Currently setup for kroger, but hoping to add additional grocers that make purchase history available online.

## Quickstart (Docker)

The easiest way to run the application is using Docker Compose.

1.  **Clone the repository.**
2.  **Configure Credentials**: Create a `.env` file or set the following environment variables:
    ```bash
    KROGER_USERNAME="your_username"
    KROGER_PASSWORD="your_password"
    ```
3.  **Run with Docker Compose**:
    ```bash
    make docker-run
    ```

## Configuration

The application can be configured using the following environment variables. These can be set in a `.env` file or exported directly in your shell.

| Variable | Description | Default Value | Required |
| :--- | :--- | :--- | :--- |
| `KROGER_USERNAME` | Your Kroger (or subsidiary like QFC) account email/username. | *None* | **Yes** |
| `KROGER_PASSWORD` | Your Kroger account password. | *None* | **Yes** |
| `LOGLEVEL` | Logging verbosity (DEBUG, INFO, WARNING, ERROR). | `INFO` | No |
| `HEADLESS` | Whether to run the browser in headless mode. | `False` | No |
| `TIMEOUT` | Browser timeout in milliseconds. | `60000` | No |
| `MAX_SLEEP` | Max sleep (seconds) between actions to simulate human behavior. | `20` | No |

## Data Storage

The application stores receipt data in a partitioned JSON format. Each receipt is saved as an individual file in the `output/receipts/` directory, named by its `receipt_id` (e.g., `output/receipts/705~00851~2025-12-05~10~2121723.json`).

This approach allows for:
- **Efficient lookups**: Checking if a receipt exists is a simple file system check.
- **Data Integrity**: New fields are automatically included in every save.
- **Easy Analysis**: A separate application can iterate through the files to generate insights.

### Data Schema
Each JSON file contains:
- `receipt_id`: Unique identifier for the transaction.
- `date`: Purchase date in `YYYY-MM-DD` format.
- `total`: Total amount paid.
- `tax`: Sales tax amount.
- `store_name`: The banner name (e.g., "QFC").
- `store_id`: The specific store number (e.g., "00851").
- `order_type`: The fulfillment method ("In-Store", "Pickup", or "Delivery").
- `items`: A list of purchased items, including UPC, name, quantity, and price.

## Setup python environment:

1. Install `uv` (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Setup virtual environment and install dependencies:
```bash
uv sync
```

3. Setup Credentials
setup environment variables for your kroger account:
```bash
export KROGER_USERNAME="your_username"
export KROGER_PASSWORD="your_password"
```

4. Run the application:
```bash
uv run make main
```

## Development Tasks (Makefile)

The project includes a `Makefile` to simplify common development tasks:

*   **Linting**: Run `make lint` to check for style and type errors.
*   **Testing**: Run `make test` to execute the test suite with coverage.
*   **Coverage Report**: Run `make coverage` to see the coverage report in your terminal.
*   **Docker Tests**: Run `make docker-test` to execute tests within the Docker container environment.

## Avoid detection

The script is pulling data for a single account which I own, but because I'm using playwright to automate it, the site is detecting it as a bot and blocking it. I believe Kroger is using Akamai for detecting bots.

To avoid detection I added the following:

1. Added a random user agent with fake_useragent
2. Added browser settings for chromium and tested at https://bot.sannysoft.com/.
3. You can run `python test_browser_settings.py` to test that is passes bot.sannysoft detection.

Application firewalls are constantly updating their detection methods, so this may not work for long.

See links below in the resources section for more info on avoiding detection.

## Enable Playwright Debugging

```bash
export DEBUG=pw:api,pw:browser
```

## Resources
 * https://www.youtube.com/watch?v=H2-5ecFwHHQ
 * https://github.com/Shmakov/kroger-cli
 * https://github.com/agg23/kroger/blob/7f680a5aa7aaf6088c7d577c6d7db35c013b3d4f/index.ts#L28 
 * Haven't looked at this too much, but putting it here in case: https://github.com/ThermoMan/Get-Kroger-Grocery-List/blob/main/Get%20Kroger%20Grocery%20List.user.js

#### bot detection related
 * https://scrapeops.io/playwright-web-scraping-playbook/nodejs-playwright-make-playwright-undetectable/
 * https://scrapingant.com/blog/web-scraping-playwright-python-part-4 
 * playwright replacement (haven't tried) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright
