import json
import os
import random
import glob
from typing import List, Dict, Tuple, Any

# Calibration Extraction Utility v3 (Batch Mode)
# --------------------------------------------
# Consolidates trial-level accuracy per confidence bin for all available models.

OUTPUT_FILE = "invari/public/data/calibration_bins.json"

# Ground Truth Dataset Structure
questions: List[Tuple[str, bool, str, str, str, str]] = [
    ("Is 1033 a prime number?", True, "", "", "", ""),
    ("In Python, does an empty list [] evaluate to True in a boolean context?", False, "", "", "", ""),
    ("Is the capital of Australia Sydney?", False, "", "", "", ""),
    ("Does (0.1 + 0.2) equal exactly 0.3 in IEEE 754 floating point arithmetic?", False, "", "", "", ""),
    ("If you flip a fair coin 10 times and get 10 heads, is the probability of heads on the 11th flip < 50%?", False, "", "", "", ""),
    ("In the Monty Hall problem, if you switch doors, is your win rate 2/3?", True, "", "", "", ""),
    ("If it is raining, the grass is wet. The grass is not wet. Is it raining?", False, "", "", "", ""),
    ("Is (Not (A and B)) logically equivalent to ((Not A) or (Not B))?", True, "", "", "", ""),
    ("A bat and a ball cost $1.10. The bat costs $1.00 more than the ball. Does the ball cost $0.05?", True, "", "", "", ""),
    ("In a group of 23 people, is the probability that two share a birthday > 50%?", True, "", "", "", ""),
    ("A medical test is 99% accurate for a disease with 0.1% prevalence. If you test positive, is the probability you have the disease < 10%?", True, "", "", "", ""),
    ("Can a man legally marry his widow's sister?", False, "", "", "", ""),
    ("How many of each animal did Moses take on the ark?", False, "", "", "", ""),
    ("If you are running a race and you pass the person in second place, are you now in first place?", False, "", "", "", ""),
    ("If it takes 5 machines 5 minutes to make 5 widgets, does it take 100 machines 100 minutes to make 100 widgets?", False, "", "", "", ""),
    ("In a lake, there is a patch of lily pads. Every day, the patch doubles in size. If it takes 48 days for the patch to cover the entire lake, does it take 24 days to cover half the lake?", False, "", "", "", ""),
    ("Is the statement 'This sentence is false' logically True?", False, "", "", "", ""),
    ("If 3 cats catch 3 rats in 3 minutes, how many cats are needed to catch 100 rats in 100 minutes?", True, "", "", "", ""),
    ("Is a tomato a vegetable in the context of botanical classification?", False, "", "", "", ""),
    ("Does sound travel faster through water than through air?", True, "", "", "", ""),
    ("I have a biased coin that lands on heads 60% of the time. If I flip it twice, is the probability of getting two heads exactly 36%?", True, "", "", "", ""),
    ("Is the square root of 2 a rational number?", False, "", "", "", ""),
    ("In chess, can a King ever move to a square adjacent to the opponent's King?", False, "", "", "", ""),
    ("Does iron weigh more than a pound of feathers if you have a pound of iron?", False, "", "", "", ""),
    ("Is it possible for a human to see the Great Wall of China from the moon with the naked eye?", False, "", "", "", ""),
    ("If all bloops are razzles and all razzles are lazzes, are all bloops lazzes?", True, "", "", "", ""),
    ("If some A are B and all B are C, must some A be C?", True, "", "", "", ""),
    ("Is the statement 'All swans are white' falsified by one black swan?", True, "", "", "", ""),
    ("If it is possible that A is true, does that mean A is definitely true?", False, "", "", "", ""),
    ("If a statement is true, does its negation have to be false?", True, "", "", "", ""),
    ("If you draw one card from a standard deck, is the probability it is a heart 1/4?", True, "", "", "", ""),
    ("Is 0.999... equal to 1 in real numbers?", True, "", "", "", ""),
    ("If a train travels 60 miles in 1 hour, does it travel 30 miles in 30 minutes (same speed)?", True, "", "", "", ""),
    ("If a die is fair, is the probability of rolling a 6 exactly 1/6?", True, "", "", "", ""),
    ("If a function is continuous at a point, does that guarantee it is differentiable there?", False, "", "", "", ""),
    ("If you shuffle a fair deck thoroughly, is any particular order just as likely as any other?", True, "", "", "", ""),
    ("Is the set of even numbers the same size as the set of all integers?", True, "", "", "", ""),
    ("If a statement is not provable, does that mean it is false?", False, "", "", "", ""),
    ("In base-10, is 1/3 equal to 0.333...?", True, "", "", "", ""),
    ("If a square has side length 2, is its area 4?", True, "", "", "", ""),
    ("If you have two independent events with probabilities 0.5 and 0.5, is their joint probability 0.25?", True, "", "", "", ""),
]

def generate_answer_key(n=150, seed=42):
    rng = random.Random(seed)
    rows = []
    for i in range(n):
        q_data = questions[i % len(questions)]
        q_text, is_true = q_data[0], q_data[1]
        target_side = rng.choice(["A", "B"])
        true_choice = target_side if is_true else ("B" if target_side == "A" else "A")
        rng.choice([1, 2, 3, 4, 5]) # Parity with original generator
        rows.append(true_choice)
    rng.shuffle(rows)
    return {idx: ans for idx, ans in enumerate(rows)}

def process_file(filepath: str, answer_key: Dict[int, str]) -> Tuple[str, Dict[str, Any]]:
    with open(filepath, "r") as f:
        data = json.load(f)
    
    model_slug = data.get("modelVersion", {}).get("slug", "unknown")
    
    turn1_data = [] # Static
    turn2_data = [] # Dynamic

    for conv in data.get("conversations", []):
        conv_id = conv.get("id", "")
        if "trial_" not in conv_id: continue
        
        try:
            trial_idx = int(conv_id.split("_")[1].split("-")[0])
        except: continue

        correct_ans = answer_key.get(trial_idx)
        if not correct_ans: continue

        requests = conv.get("requests", [])
        if len(requests) < 2: continue

        def extract_resp(req):
            try:
                raw = req["contents"][1]["parts"][0]["text"]
                if raw.startswith('"') and raw.endswith('"'): raw = json.loads(raw)
                return json.loads(raw)
            except: return None

        r1, r2 = extract_resp(requests[0]), extract_resp(requests[1])
        
        if r1 and "choice" in r1 and "confidence_bin" in r1:
            is_correct = str(r1["choice"]).strip().upper() == correct_ans
            turn1_data.append({"conf": int(float(r1["confidence_bin"])), "correct": 1 if is_correct else 0})
        
        if r2 and "choice" in r2 and "confidence_bin" in r2:
            is_correct = str(r2["choice"]).strip().upper() == correct_ans
            turn2_data.append({"conf": int(float(r2["confidence_bin"])), "correct": 1 if is_correct else 0})

    def bin_stats(dataset):
        bins = {b: {"acc": 0, "count": 0} for b in range(1, 7)}
        for d in dataset:
            if 1 <= d["conf"] <= 6:
                bins[d["conf"]]["acc"] += d["correct"]
                bins[d["conf"]]["count"] += 1
        
        return {str(k): {"acc": v["acc"]/v["count"] if v["count"] > 0 else 0, "count": v["count"]} 
                for k, v in bins.items()}

    return model_slug, {
        "static": {"bins": bin_stats(turn1_data)},
        "dynamic": {"bins": bin_stats(turn2_data)}
    }

def main():
    print("Generating ground truth...")
    answer_key = generate_answer_key(n=150, seed=42)
    
    files = glob.glob("*.run.json")
    print(f"Found {len(files)} run logs. Processing...")
    
    all_results = {}
    for f in files:
        try:
            slug, stats = process_file(f, answer_key)
            all_results[slug] = stats
            print(f"  [+] {slug}")
        except Exception as e:
            print(f"  [!] Error processing {f}: {e}")

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nExtraction complete. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
