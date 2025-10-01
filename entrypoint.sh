#!/bin/sh
set -e

# Start the FastAPI app with Uvicorn
exec uvicorn fms_proxy.app:app --host 0.0.0.0 --port 8000
