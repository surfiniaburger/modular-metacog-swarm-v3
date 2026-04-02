#!/bin/bash
# launch_gen2.sh

echo "🚀 Launching Gen-2 Modular Swarm Infrastructure..."

# 0. Ensure ports are free
kill_port() {
  local port="$1"
  local pids
  pids=$(lsof -ti tcp:"$port" 2>/dev/null)
  if [ -n "$pids" ]; then
    echo "🧹 Freeing port $port (PID(s): $pids)..."
    kill $pids 2>/dev/null || true
    sleep 1
    # Force kill if still listening
    if lsof -ti tcp:"$port" >/dev/null 2>&1; then
      echo "🧹 Forcing port $port to close..."
      kill -9 $pids 2>/dev/null || true
      sleep 1
    fi
  fi
}
kill_port 8000
kill_port 8004

# 1. Start the Hub (Background)
echo "📡 Starting Observability Hub (Port 8000)..."
PYTHONPATH=. uv run hub/app.py > hub.log 2>&1 &
HUB_PID=$!

# 2. Start the Executor (Background)
echo "🐚 Starting Research Executor (MCP)..."
PYTHONPATH=. uv run executor/mcp_server.py > executor.log 2>&1 &
EXEC_PID=$!

# 3. Start the A2A Benchmark Server (Background)
echo "🧪 Starting A2A Benchmark Server (Port 8004)..."
PYTHONPATH=. uv run python -m benchmark_a2a.benchmark_server --host 0.0.0.0 --port 8004 --card-url http://localhost:8004/ > benchmark.log 2>&1 &
BENCH_PID=$!

# 4. Give them a moment to boot
sleep 5

# 5. Run the Mediator
echo "🤖 Starting Research Mediator (Main Loop)..."
PYTHONPATH=. uv run main.py

# Cleanup on exit
echo "🧹 Cleaning up infrastructure..."
kill $HUB_PID $EXEC_PID $BENCH_PID > /dev/null 2>&1
echo "✅ Swarm Retired."
