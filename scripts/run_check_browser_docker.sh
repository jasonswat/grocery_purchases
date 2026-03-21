#!/usr/bin/env bash
set -euo pipefail

# Run the `helper_browser_settings.py` inside a Docker container built from
# the project's Dockerfile. This helps reproduce CI/container network
# differences (Akamai, proxies, etc.). The script mounts the repo so
# screenshots and logs are written to the host working dir.

usage() {
  cat <<EOF
Usage: $0 [--headed] [--host-network] [--output <host_dir>]

Options:
  --headed           Run browser in headed mode (default: False, i.e. headless)
  --host-network     Run container with host networking (may change routing/IP)
  --output <dir>     Mount host directory to container at /output (default: output)
  --help             Show this help

Examples:
  # build image and run with host networking (useful to test if Akamai blocks Docker NAT)
  $0 --host-network --output ~/output

EOF
}

HEADLESS="True"
HOST_NET=""
OUTPUT_DIR="output"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --headed)
      HEADLESS="False"; shift ;;
    --host-network)
      HOST_NET="--network host"; shift ;;
    --output)
      OUTPUT_DIR="$2"; shift 2 ;;
    --help)
      usage; exit 0 ;;
    *)
      echo "Unknown arg: $1"; usage; exit 2 ;;
  esac
done

echo "Building Docker image 'grocery_purchases-app'..."
docker build -t grocery_purchases-app .

echo "Running helper_browser_settings.py in container (HEADLESS=${HEADLESS})..."

## Verify required environment variables are present (do not read passwords from files)
if [[ -z "${KROGER_USERNAME:-}" || -z "${KROGER_PASSWORD:-}" ]]; then
  echo "ERROR: KROGER_USERNAME and KROGER_PASSWORD must be set in the environment." >&2
  echo "Refusing to run with missing credentials." >&2
  exit 2
fi

# Mount current repo at /app and optional output dir at /output
# We force HEADLESS=False inside the container to ensure Playwright uses the 
# headed mode provided by the container's Xvfb (set up in Dockerfile ENTRYPOINT).
RUN_CMD=(docker run --rm -u "$(id -u):$(id -g)" -e HEADLESS="False" -e MAX_SLEEP=5 -e KROGER_USERNAME="${KROGER_USERNAME}" -e KROGER_PASSWORD="${KROGER_PASSWORD}" -e LOGLEVEL=INFO -v "$(pwd)":/app -w /app)

if [[ -n "$OUTPUT_DIR" ]]; then
  mkdir -p "$OUTPUT_DIR"
  RUN_CMD+=( -v "${OUTPUT_DIR}":/output )
fi

if [[ -n "$HOST_NET" ]]; then
  # shellcheck disable=SC2086
  RUN_CMD+=( $HOST_NET )
fi

# The Dockerfile ENTRYPOINT handles starting Xvfb and setting DISPLAY
RUN_CMD+=( --shm-size=1g grocery_purchases-app python src/util/helper_browser_settings.py)

# Redact password in logs
CLEAN_CMD="${RUN_CMD[*]//${KROGER_PASSWORD}/********}"
echo "Command: ${CLEAN_CMD}"
"${RUN_CMD[@]}"

echo "Done. If the script produced a screenshot, check browser_settings.png in the repo root."
