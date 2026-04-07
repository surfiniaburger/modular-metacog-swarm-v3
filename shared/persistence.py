# shared/persistence.py
import json
import os
import sqlite3
import subprocess
import logging
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger("persistence")

class ExperienceStore:
    def __init__(self, db_path: str = "experience.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS experiences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    iteration INTEGER,
                    verdict TEXT,
                    strategy TEXT,
                    critic_review TEXT,
                    is_rejected BOOLEAN,
                    d_plus_proxy TEXT,
                    d_minus_proxy TEXT
                )
            """)

    def archive_failure(self, iteration: int, strategy: str, review: str):
        """
        Archives a rejected iteration for later distillation (The Moat).
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO experiences (timestamp, iteration, verdict, strategy, critic_review, is_rejected) VALUES (?, ?, ?, ?, ?, ?)",
                (datetime.utcnow().isoformat(), iteration, "REJECT", strategy, review, True)
            )
        logger.info(f"Iteration {iteration} failure archived to Experience Store.")

class StateManager:
    def __init__(self, state_dir: str = "research_env/vault/state"):
        self.state_dir = state_dir
        os.makedirs(self.state_dir, exist_ok=True)
        self._init_git_checkpoint()

    def _init_git_checkpoint(self):
        try:
            # Ensure we are on a research branch or at least have git init
            subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            logger.warning("Not a git repository. Git checkpointing disabled.")

    def save_iteration_state(self, iteration: int, state: Dict[str, Any], commit: bool = True):
        state_file = os.path.join(self.state_dir, f"iteration_{iteration}.json")
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)
        
        if commit:
            self._git_checkpoint(iteration)

    def _git_checkpoint(self, iteration: int):
        """
        Automatically commits the iteration state to a local 'research_state' branch.
        """
        try:
            subprocess.run(["git", "add", self.state_dir], check=False)
            subprocess.run(
                ["git", "commit", "-m", f"Research Checkpoint: Iteration {iteration} stabilized."],
                check=False, capture_output=True
            )
            logger.info(f"Git checkpoint created for iteration {iteration}.")
        except Exception as e:
            logger.error(f"Git checkpoint failed: {e}")

    def load_latest_state(self) -> Optional[Dict[str, Any]]:
        files = sorted([f for f in os.listdir(self.state_dir) if f.endswith(".json")])
        if not files:
            return None
        with open(os.path.join(self.state_dir, files[-1]), "r") as f:
            return json.load(f)
