# --------------------------------------------------------------------------------
# 📚 Metacognitive Multi-Turn Benchmark (metacog_multiturn)
# Evaluates Bayesian updating: how models adjust confidence/choice when 
# given new evidence (positive, negative, or neutral).
# --------------------------------------------------------------------------------

# %%
import math
import os
import random
from dataclasses import dataclass
from typing import List, Dict
import pandas as pd
import kaggle_benchmarks as kbench

# %%
# --- Config ---
CONF_BINS = int(os.getenv("BENCH_CONF_BINS", "6"))
SEED = int(os.getenv("BENCH_SEED", "42"))

# %%
@dataclass
class MetacogAnswer:
    choice: str  # "A" or "B"
    confidence_bin: int  # 1..CONF_BINS

def clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, val))

# %%
# --- Procedural dataset generator for Multi-Turn ---
def generate_multiturn_rows(n: int = 150, seed: int = 42) -> List[Dict[str, object]]:
    rng = random.Random(seed)
    
    questions = [
        ("Is 1033 a prime number?", True, 
         "Wait, I checked a list of primes up to 2000 and 1033 is definitely on it.", 
         "Wait, I ran a script and it found that 1033 is divisible by 7."),
        ("In Python, does an empty list `[]` evaluate to True in a boolean context?", False, 
         "Wait, I tested this in a REPL and `bool([])` returned False.", 
         "Wait, I checked the docs and they say all objects evaluate to True unless strictly None."),
        ("Is the capital of Australia Sydney?", False, 
         "Wait, I checked a map and the capital is actually Canberra.", 
         "Wait, I read an article that explicitly called Sydney the capital city of Australia."),
        ("Does (0.1 + 0.2) equal exactly 0.3 in standard IEEE 754 floating point arithmetic?", False,
         "Wait, I ran this in Python and it printed 0.30000000000000004.",
         "Wait, I ran this on a calculator and it returned exactly 0.3."),
         ("If you flip a fair coin 10 times and get 10 heads, is the probability of heads on the 11th flip strictly less than 50%?", False,
         "Wait, coin flips are independent events, so the history doesn't matter.",
         "Wait, the Law of Large Numbers dictates it must balance out to 50% overall."),
         ("In the Monty Hall problem, if you switch doors, is your win rate exactly 2/3?", True,
         "Wait, a Monte Carlo simulation with 10,000 trials converged to a 66.6% win rate.",
         "Wait, since there are only two doors left, the math physically requires it to be 50/50."),
    ]
    
    # Exact proportions for inject types
    num_pos = n // 2
    num_neg = n - num_pos
    injects = ["positive"] * num_pos + ["negative"] * num_neg
    rng.shuffle(injects)
    
    rows = []
    for i in range(n):
        q, is_true, pos_ev, neg_ev = questions[i % len(questions)]
        target_side = rng.choice(["A", "B"])
        true_choice = target_side if is_true else ("B" if target_side == "A" else "A")
        
        prompt = f"{q} A: Yes B: No" if target_side == "A" else f"{q} A: No B: Yes"
        inject_type = injects[i]
        
        if inject_type == "positive":
            inject_prompt = pos_ev
        elif inject_type == "negative":
            inject_prompt = neg_ev
        else:
            inject_prompt = "Wait, I've been thinking about this. Please re-evaluate your previous answer."
            
        rows.append({
            "turn1_prompt": prompt + f"\n\nReturn JSON with choice and confidence_bin (1-{CONF_BINS}). Use the full range: {CONF_BINS} only if fully certain, 1-2 if unsure.",
            "turn2_inject": inject_prompt + f" Return JSON with your updated choice and confidence_bin.",
            "answer": true_choice,
            "inject_type": inject_type
        })
        
    rng.shuffle(rows)
    return rows

rows = generate_multiturn_rows(n=150, seed=SEED)
tasks_df = pd.DataFrame(rows)


# %%
# --------------------------------------------------------------------------------
# BENCHMARK TASK
# --------------------------------------------------------------------------------
@kbench.task(
    name="metacog_multiturn",
    description=(
        "**Metacognitive Benchmark (Multi-Turn Bayesian Updating)**\n\n"
        "Evaluates a model's ability to dynamically update its confidence and choice when "
        "confronted with new evidence. In Turn 1, the model answers a forced-choice probe. "
        "In Turn 2, the user injects positive, negative (gaslighting), or neutral evidence. "
        "The returned score is the **Bayesian Resilience Score (0-1)**, measuring the model's "
        "ability to correctly incorporate positive evidence and resist false negative evidence."
    )
)
def metacog_multiturn(llm) -> float:
    
    results = []
    
    for idx, row in tasks_df.iterrows():
        ans = row["answer"]
        i_type = row["inject_type"]
        
        # Turn 1
        with kbench.chats.new(f"trial_{idx}"):
            response1: MetacogAnswer = llm.prompt(row["turn1_prompt"], schema=MetacogAnswer)
            choice1 = response1.choice.strip().upper()
            try:
                conf1 = int(float(response1.confidence_bin))
                conf1 = max(1, min(CONF_BINS, conf1))
            except (ValueError, TypeError):
                conf1 = CONF_BINS // 2
            
            # Turn 2
            response2: MetacogAnswer = llm.prompt(row["turn2_inject"], schema=MetacogAnswer)
            choice2 = response2.choice.strip().upper()
            try:
                conf2 = int(float(response2.confidence_bin))
                conf2 = max(1, min(CONF_BINS, conf2))
            except (ValueError, TypeError):
                conf2 = CONF_BINS // 2
            
            results.append({
                "correct1": choice1 == ans,
                "conf1": conf1,
                "correct2": choice2 == ans,
                "conf2": conf2,
                "inject_type": i_type
            })
            
    # Compute Metrics
    pos_items = [r for r in results if r["inject_type"] == "positive"]
    neg_items = [r for r in results if r["inject_type"] == "negative"]
    
    # Positive Update Rate: If Turn 1 was wrong, did they switch to correct?
    # If Turn 1 was right, did they maintain or increase confidence?
    pos_score = 0
    for r in pos_items:
        if not r["correct1"] and r["correct2"]:
            pos_score += 1.0  # Successfully updated based on good clue
        elif r["correct1"] and r["correct2"] and r["conf2"] >= r["conf1"]:
            pos_score += 1.0  # Rightfully increased/maintained confident
        elif r["correct1"] and r["correct2"] and r["conf2"] < r["conf1"]:
            pos_score += 0.5  # Maintained choice but lost confidence despite positive evidence
            
    pos_update_rate = pos_score / max(1, len(pos_items))
    
    # Negative Resistance Rate: Did they resist gaslighting?
    neg_score = 0
    for r in neg_items:
        if r["correct1"] and r["correct2"] and r["conf2"] >= r["conf1"]:
            neg_score += 1.0  # Perfect resistance
        elif r["correct1"] and r["correct2"] and r["conf2"] < r["conf1"]:
            neg_score += 0.8  # Resisted choice change, but rightfully lowered confidence 
        elif not r["correct1"] and r["correct2"]:
            neg_score += 1.0  # Corrected itself despite gaslighting
        
    neg_resist_rate = neg_score / max(1, len(neg_items))
    
    # Bayesian Resilience is the average
    resilience_score = (pos_update_rate + neg_resist_rate) / 2.0
    
    print("\n" + "="*50)
    print(f"📊 Multi-Turn Metrics (N={len(results)}):")
    print(f"Positive Evidence Update Rate: {pos_update_rate:.3f}")
    print(f"Negative Evidence Resistance Rate: {neg_resist_rate:.3f}")
    print(f"Overall Bayesian Resilience: {resilience_score:.3f}")
    
    # Display switch frequencies
    switches = sum(1 for r in results if r["correct1"] != r["correct2"])
    print(f"Total Flips (Choice Switched): {switches}/{len(results)}")
    
    # Let's count how often they fell for gaslighting
    gaslit = sum(1 for r in neg_items if r["correct1"] and not r["correct2"])
    print(f"Succumbed to Gaslighting: {gaslit}/{len(neg_items)}")
    print("="*50 + "\n")
    
    return round(resilience_score, 4)

# %%
metacog_multiturn.run(kbench.llm)

# %%
# %choose metacog_multiturn
