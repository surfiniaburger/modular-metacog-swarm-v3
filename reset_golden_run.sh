#!/bin/bash
# Reset Script for Golden Run v2 (Resilience & Recovery)

# Model Defaults
DEFAULT_BRAIN_MODEL="ollama/qwen3.5:9b"
DEFAULT_HANDS_MODEL="ollama/qwen2.5-coder:3b"
DEFAULT_MODEL_LIST="qwen3.5:9b,qwen2.5-coder:3b"

echo "🔄 Archiving poisoned refusal logs..."
mv research_env/program.md research_env/program_refusal_archive.md

echo "📝 Preparing fresh mission grounding..."
cat <<EOF > research_env/program.md
---
**Session Reset: Golden Run v2 (Resilient) Initiated**
Mission: Extract M-Ratio and Calibration Sensitivity signals via Metacognitive Probing.
Grounding: chandra_packet.json + Fleming & Lau (2014)
---
EOF

echo "🚀 Launching Resilient Swarm..."
# Optional cleanup: set CLEAN_RESULTS=1 to wipe old benchmark outputs before run.
CLEAN_RESULTS_DEFAULT=1
if [ "${CLEAN_RESULTS:-$CLEAN_RESULTS_DEFAULT}" = "1" ]; then
  echo "🧹 Cleaning previous benchmark results..."
  rm -f research_env/results/iteration_*_results.json
  rm -f research_env/results/iteration_*_tasklog.json
  rm -f research_env/results/summary.json
  rm -f research_env/results/summary.txt
  rm -f research_env/results/summary.png
  rm -f research_env/results/summary_reliability.png
fi

# One-time full logging: first run enables task logs for reliability plots, then auto-disables.
BENCH_LOG_ONCE_MARKER="research_env/.bench_log_full_once"
if [ -f "$BENCH_LOG_ONCE_MARKER" ]; then
  BENCH_LOG_FULL_DEFAULT=0
else
  BENCH_LOG_FULL_DEFAULT=1
  mkdir -p research_env
  touch "$BENCH_LOG_ONCE_MARKER"
fi
USE_A2A_BENCHMARK=1 \
BENCH_EVERY_N=3 \
A2A_BENCH_URL=http://localhost:8004 \
A2A_BENCH_TIMEOUT=2400 \
BENCH_RETRIES=2 \
BENCH_SLEEP_SECONDS=3 \
USE_LITELLM=0 \
USE_OLLAMA=1 \
BENCH_LOG_FULL=${BENCH_LOG_FULL:-$BENCH_LOG_FULL_DEFAULT} \
BENCH_NUM_TASKS=5 \
BENCH_CONF_BINS=6 \
BENCH_BOOTSTRAP=200 \
BENCH_TRAP_BOOST=1 \
BENCH_ADVERSARIAL_SHARE=0.6 \
BENCH_PER_MODEL_MAX_SECONDS=2400 \
BENCH_SUMMARY_EVERY_N=10 \
BENCH_SUMMARY_ON_END=1 \
BENCH_MIN_ITERATION=2 \
RUN_ITERATIONS=15 \
OLLAMA_TIMEOUT=30 \
OLLAMA_RETRIES=2 \
OLLAMA_SLEEP=0.2 \
BRAIN_MODEL=${BRAIN_MODEL:-$DEFAULT_BRAIN_MODEL} \
HANDS_MODEL=${HANDS_MODEL:-$DEFAULT_HANDS_MODEL} \
CRITIC_MODEL=${CRITIC_MODEL:-$DEFAULT_BRAIN_MODEL} \
MODEL_LIST=${MODEL_LIST:-$DEFAULT_MODEL_LIST} \
BENCH_MODEL_STRONG=${BENCH_MODEL_STRONG:-$DEFAULT_BRAIN_MODEL} \
BENCH_MODEL_WEAK=${BENCH_MODEL_WEAK:-$DEFAULT_HANDS_MODEL} \
./launch_gen2.sh
