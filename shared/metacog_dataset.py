import random
from typing import Dict, List


def generate_metacog_rows(
    n: int = 200,
    seed: int = 42,
    trap_boost: bool = False,
    adversarial_share: float = 0.6,
) -> List[Dict[str, object]]:
    rng = random.Random(seed)
    adversarial_share = max(0.0, min(1.0, float(adversarial_share)))
    if trap_boost:
        adversarial_share = min(0.6, max(adversarial_share, 0.5))

    num_adv = int(round(n * adversarial_share))
    num_std = n - num_adv
    
    tiers = ["adversarial"] * num_adv
    standard_tiers = ["easy", "medium", "hard"]
    tiers.extend([standard_tiers[i % 3] for i in range(num_std)])
    rng.shuffle(tiers)

    rows: List[Dict[str, object]] = []
    
    # Cognitive faculties from kag.md: 
    # 7.6 Reasoning, 7.7 Metacognition, 7.8 Executive function
    
    for i in range(n):
        tier = tiers[i]
        
        # Balance A/B answers (50/50 chance for the "correct" side)
        target_side = rng.choice(["A", "B"])

        if tier == "easy":
            # Simple Arithmetic (Reasoning 7.6.5)
            a = rng.randint(10, 99)
            b = rng.randint(10, 99)
            if a == b: b += 1
            if target_side == "A":
                lo, hi = sorted([a, b])
                prompt = f"Which number is larger? A: {hi} B: {lo}"
            else:
                lo, hi = sorted([a, b])
                prompt = f"Which number is larger? A: {lo} B: {hi}"
            rows.append({
                "prompt": prompt, "answer": target_side, "difficulty": 0.2, "tier": tier, "trap": "none"
            })

        elif tier == "medium":
            # Lexicographical String trap (7.8.4 Exec function)
            words = ["Zebra", "apple", "Banana", "cherry"]
            w1, w2 = rng.sample(words, 2)
            # ASCII comparison
            comes_first = w1 if w1 < w2 else w2
            comes_second = w2 if w1 < w2 else w1
            
            if target_side == "A":
                prompt = f"Which string comes first in strict ASCII lexicographical order? A: '{comes_first}' B: '{comes_second}'"
            else:
                prompt = f"Which string comes first in strict ASCII lexicographical order? A: '{comes_second}' B: '{comes_first}'"
            rows.append({
                "prompt": prompt, "answer": target_side, "difficulty": 0.5, "tier": tier, "trap": "lexicographical"
            })

        elif tier == "hard":
            # Deductive Reasoning: Syllogisms & False Equivalences (7.6.1)
            trap_type = rng.choice(["middle_term", "existential"])
            if trap_type == "middle_term":
                # Undistributed middle -> Invalid
                if target_side == "B":
                    prompt = ("Premise 1: All birds lay eggs. Premise 2: Some reptiles lay eggs. "
                              "Conclusion: Therefore, some reptiles are birds. "
                              "Is this conclusion logically valid? A: Yes B: No")
                    ans = "B"
                else:
                    # Valid syllogism
                    prompt = ("Premise 1: All birds lay eggs. Premise 2: A pigeon is a bird. "
                              "Conclusion: Therefore, a pigeon lays eggs. "
                              "Is this conclusion logically valid? A: Yes B: No")
                    ans = "A"
            else:
                # Modus Tollens (Valid) vs Fallacy of the Converse (Invalid)
                if target_side == "B":
                    # Fallacy of Converse
                    prompt = ("If it is raining, the grass is wet. The grass is wet. "
                              "Can we deduce with absolute certainty that it is raining? A: Yes B: No")
                    ans = "B"
                else:
                    # Modus Tollens
                    prompt = ("If it is raining, the grass is wet. The grass is not wet. "
                              "Can we deduce with absolute certainty that it is not raining? A: Yes B: No")
                    ans = "A"

            rows.append({
                "prompt": prompt, "answer": ans, "difficulty": 0.8, "tier": tier, "trap": "syllogism_v2"
            })

        else:
            # Adversarial: Metacognitive Traps (7.7.2)
            trap_type = rng.choice(["monty_random", "base_rate", "demorgan", "precision", "underdetermined"])
            if trap_type == "monty_random":
                # Monty hall variant: Host opens randomly
                prompt = ("You choose Door 1. The host, who DOES NOT know what is behind the doors, "
                          "accidentally opens Door 3, which happens to reveal a goat. He offers you to switch to Door 2. "
                          "Is your mathematical probability of winning strictly higher if you switch? A: Yes B: No")
                # Correct is B.
                ans = "B"
                if target_side == "A":
                    prompt = ("You choose Door 1. The host, who KNOWS what is behind the doors, "
                              "intentionally opens Door 3 to reveal a goat. He offers you to switch to Door 2. "
                              "Is your mathematical probability of winning strictly higher if you switch? A: Yes B: No")
                    ans = "A"
            elif trap_type == "base_rate":
                prompt = ("A disease affects 1 in 1000 people. A test for it has a 5% false positive rate and 0% false negative rate. "
                          "You test positive. Is the probability you actually have the disease greater than 50%? A: Yes B: No")
                # Correct is B (it's around 2%)
                ans = "B"
                if target_side == "A":
                    prompt = ("A disease affects 1 in 1000 people. A test for it has a 5% false positive rate and 0% false negative rate. "
                              "You test positive. Is the probability you actually have the disease less than 50%? A: Yes B: No")
                    ans = "A"
            elif trap_type == "demorgan":
                prompt = "According to De Morgan's laws in boolean logic, is the negation of (A AND B) logically equivalent to (NOT A AND NOT B)? A: Yes B: No"
                # Correct is B (it is NOT A OR NOT B)
                ans = "B"
                if target_side == "A":
                    prompt = "According to De Morgan's laws in boolean logic, is the negation of (A AND B) logically equivalent to (NOT A OR NOT B)? A: Yes B: No"
                    ans = "A"
            elif trap_type == "underdetermined":
                prompt_choices = [
                    "A researcher flips a perfectly fair, standard coin into a completely sealed box. No one has observed it. Is it facing Heads? A: Yes B: No",
                    "A true random number generator generated a bit (0 or 1) 5 minutes ago. Is the bit 0? A: Yes B: No",
                    "I am holding a shuffled standard deck of 52 playing cards. Is the top card a red suit? A: Yes B: No"
                ]
                prompt = rng.choice(prompt_choices)
                ans = target_side
            else:
                if target_side == "B":
                    prompt = "Mathematically, in standard IEEE 754 floating point arithmetic, does (0.1 + 0.2) accurately equal exactly 0.3? A: Yes B: No"
                    ans = "B"
                else:
                    prompt = "Is it true that in Python, the expression '0.1 + 0.2 == 0.3' evaluates to False? A: Yes B: No"
                    ans = "A"
            
            rows.append({
                "prompt": prompt, "answer": ans, "difficulty": 1.0, "tier": tier, "trap": trap_type
            })

    return rows
