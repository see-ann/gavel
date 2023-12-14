#!/bin/bash
# entrypoint.sh

# Forward all arguments to the Python script
exec python3 /scheduler/scripts/drivers/simulate_scheduler_with_trace.py "$@"
