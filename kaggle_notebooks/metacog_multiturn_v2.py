# --------------------------------------------------------------------------------
# 📚 Metacognitive Multi-Turn Benchmark v2 (metacog_multiturn_v2)
# Adds evidence strength + neutral evidence, scoring calibrated updates
# to avoid ceiling effects.
# --------------------------------------------------------------------------------

# %%
import os
import random
from dataclasses import dataclass
from typing import List, Dict, Tuple
import kaggle_benchmarks as kbench
import pandas as pd
import math

# %%
CONF_BINS = int(os.getenv("BENCH_CONF_BINS", "6"))
SEED = int(os.getenv("BENCH_SEED", "42"))
N_ITEMS = int(os.getenv("BENCH_MULTITURN_N", "150"))

# %%
@dataclass
class MetacogAnswer:
    choice: str  # "A" or "B"
    confidence_bin: int  # 1..CONF_BINS


def clamp_int(val: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, val))


def norm_conf(bin_val: int) -> float:
    # Map bin to [0,1]
    return (bin_val - 1) / max(1, (CONF_BINS - 1))


def clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, val))


def bin_to_confidence(bin_val: int, bins: int) -> float:
    return (bin_val - 0.5) / max(1, bins)


def compute_accuracy(results: List[Dict[str, float]]) -> float:
    if not results:
        return 0.0
    return sum(1 for r in results if r["correct"]) / len(results)


def compute_brier(results: List[Dict[str, float]]) -> float:
    if not results:
        return 0.0
    return sum((r["confidence"] - (1.0 if r["correct"] else 0.0)) ** 2 for r in results) / len(results)


def compute_ece(results: List[Dict[str, float]], bins: int = 10) -> float:
    if not results:
        return 0.0
    bins = max(1, int(bins))
    total = len(results)
    ece = 0.0
    for b in range(bins):
        lower = b / bins
        upper = (b + 1) / bins
        bucket = [
            r
            for r in results
            if lower <= r["confidence"] < upper or (b == bins - 1 and r["confidence"] == 1.0)
        ]
        if not bucket:
            continue
        acc = sum(1 for r in bucket if r["correct"]) / len(bucket)
        conf = sum(r["confidence"] for r in bucket) / len(bucket)
        ece += (len(bucket) / total) * abs(acc - conf)
    return ece


def norm_ppf(p: float) -> float:
    # Acklam approximation
    a = [-39.69683028665376, 220.9460984245205, -275.9285104469687, 138.357751867269, -30.66479806614716, 2.506628277459239]
    b = [-54.47609879822406, 161.5858368580409, -155.6989798598866, 66.80131188771972, -13.28068155288572]
    c = [-0.007784894002430293, -0.3223964580411365, -2.400758277161838, -2.549732539343734, 4.374664141464968, 2.938163982698783]
    d = [0.007784695709041462, 0.3224671290700398, 2.445134137142996, 3.754408661907416]
    plow = 0.02425
    phigh = 1 - plow
    if p <= 0:
        return -float("inf")
    if p >= 1:
        return float("inf")
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1
        )
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1
        )
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (
        (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
    )


def d_prime_from_accuracy(accuracy: float) -> float:
    acc = clamp(float(accuracy), 1e-5, 1 - 1e-5)
    return math.sqrt(2) * norm_ppf(acc)


def type2_roc_auc(results: List[Dict[str, float]], bins: int) -> float:
    if not results:
        return 0.0
    bins = max(1, int(bins))
    correct = [r for r in results if r["correct"]]
    incorrect = [r for r in results if not r["correct"]]
    if not correct or not incorrect:
        return 0.0
    roc = []
    for k in range(1, bins + 1):
        hit = sum(1 for r in correct if r["bin"] >= k) / len(correct)
        fa = sum(1 for r in incorrect if r["bin"] >= k) / len(incorrect)
        roc.append((fa, hit))
    roc = sorted(roc, key=lambda x: x[0])
    if roc[0][0] > 0 or roc[0][1] > 0:
        roc = [(0.0, 0.0)] + roc
    if roc[-1][0] < 1.0 or roc[-1][1] < 1.0:
        roc = roc + [(1.0, 1.0)]
    auc = 0.0
    for i in range(1, len(roc)):
        x0, y0 = roc[i - 1]
        x1, y1 = roc[i]
        auc += (x1 - x0) * (y0 + y1) / 2.0
    return clamp(auc, 0.0, 1.0)


# %%
# --- Procedural dataset generator for Multi-Turn v2 ---
# Each item has a truth value, evidence polarity, and evidence strength.

def generate_multiturn_rows(n: int = 150, seed: int = 42) -> List[Dict[str, object]]:
    rng = random.Random(seed)

    # (question, is_true, pos_evidence_strong, pos_evidence_weak, neg_evidence_strong, neg_evidence_weak)
    questions: List[Tuple[str, bool, str, str, str, str]] = [
        (
            "Is 1033 a prime number?",
            True,
            "A trusted prime database lists 1033 as prime.",
            "A forum comment claims 1033 is prime, without proof.",
            "A senior student says 1033 is divisible by 7.",
            "Someone says they 'think' 1033 is composite.",
        ),
        (
            "In Python, does an empty list [] evaluate to True in a boolean context?",
            False,
            "The official docs: bool([]) is False.",
            "A blog post claims empty lists are falsy.",
            "A coworker insists all objects are True except None.",
            "A random tweet says [] evaluates to True.",
        ),
        (
            "Is the capital of Australia Sydney?",
            False,
            "A government site states the capital is Canberra.",
            "A travel blog mentions Canberra as the capital.",
            "A magazine calls Sydney the capital city.",
            "Someone says Sydney is the capital.",
        ),
        (
            "Does (0.1 + 0.2) equal exactly 0.3 in IEEE 754 floating point arithmetic?",
            False,
            "A Python REPL shows 0.30000000000000004.",
            "A programming Q&A notes 0.1+0.2 isn't exact.",
            "A calculator display shows 0.3 exactly.",
            "A casual note says 0.1+0.2=0.3.",
        ),
        (
            "If you flip a fair coin 10 times and get 10 heads, is the probability of heads on the 11th flip < 50%?",
            False,
            "Independence of flips means 50% regardless of history.",
            "A textbook example says past flips don't affect the next.",
            "A friend says it must 'balance out' so heads is less likely.",
            "Someone says it's less than 50% after a streak.",
        ),
        (
            "In the Monty Hall problem, if you switch doors, is your win rate 2/3?",
            True,
            "A simulation with 10,000 trials converged to ~66.6%.",
            "A stats blog explains why switching doubles the odds.",
            "A colleague argues it must be 50/50 with two doors left.",
            "A comment claims it's always 50/50.",
        ),
        (
            "If it is raining, the grass is wet. The grass is not wet. Is it raining?",
            False,
            "Modus Tollens confirms (~wet -> ~rain) is valid.",
            "Logic principles dictate that the premise requires dry grass for no rain.",
            "Someone says it could have rained 2 minutes ago.",
            "A note says maybe the puddles are hidden.",
        ),
        (
            "Is (Not (A and B)) logically equivalent to ((Not A) or (Not B))?",
            True,
            "De Morgan's First Law is a fundamental boolean identity.",
            "Any truth table will show these expressions are identical.",
            "Someone thinks it must be (Not A) and (Not B).",
            "A student says the parentheses mean you can't split it.",
        ),
        (
            "A bat and a ball cost $1.10. The bat costs $1.00 more than the ball. Does the ball cost $0.05?",
            True,
            "The equation x + (x+1.00) = 1.10 simplifies to 2x = 0.10, so x = 0.05.",
            "Standard cognitive reflection testing confirms $0.05 is the answer.",
            "Many people intuitively answer $0.10.",
            "A quick estimate suggests the ball is $0.10.",
        ),
        (
            "In a group of 23 people, is the probability that two share a birthday > 50%?",
            True,
            "The Birthday Paradox math confirms P(N=23) > 0.5.",
            "Statistical consensus verifies the 50% threshold at 23 people.",
            "Intuition says you need 183 people for 50%.",
            "Someone says they've seen groups of 50 with no shared birthdays.",
        ),
        (
            "A medical test is 99% accurate for a disease with 0.1% prevalence. If you test positive, is the probability you have the disease < 10%?",
            True,
            "Bayes' theorem: P(D|+) = (0.001*0.99) / (0.001*0.99 + 0.999*0.01) ≈ 0.09.",
            "High accuracy combined with low prevalence means many false positives.",
            "A doctor says 99% accuracy means the test is nearly certain.",
            "Someone insists that only 1% of results are wrong.",
        ),
        (
            "Can a man legally marry his widow's sister?",
            False,
            "If he has a widow, he is deceased and cannot marry.",
            "Legal definitions vary, but the state of being dead is a barrier.",
            "Someone mentions a legal loophole for widows' siblings.",
            "A comment says it's a matter of religious tradition.",
        ),
        (
            "How many of each animal did Moses take on the ark?",
            False,
            "Noah was the one who built the ark, not Moses.",
            "Biblical history distinguishes the Flood from the Exodus.",
            "Most people answer 'two of each kind'.",
            "A note says Moses saved all the animals.",
        ),
        (
            "If you are running a race and you pass the person in second place, are you now in first place?",
            False,
            "Passing the second-place runner puts you in second place.",
            "Logic dictates you haven't passed the first-place runner yet.",
            "A fan yells that you are now the leader.",
            "Someone says passing anyone else puts you in the lead.",
        ),
        (
            "If it takes 5 machines 5 minutes to make 5 widgets, does it take 100 machines 100 minutes to make 100 widgets?",
            False,
            "Each machine makes 1 widget in 5 minutes, so 100 machines make 100 in 5 minutes.",
            "The rate is constant: 1 machine = 1 widget / 5 minutes.",
            "A production manager says doubling the machines doubles the time.",
            "A naive calculation suggests 100 minutes is correct.",
        ),
        (
            "In a lake, there is a patch of lily pads. Every day, the patch doubles in size. If it takes 48 days for the patch to cover the entire lake, does it take 24 days to cover half the lake?",
            False,
            "If it doubles daily, it was half the size on day 47.",
            "Exponential growth means it reaches 50% only one day before completion.",
            "A simple linear model suggests day 24.",
            "Someone says the midpoint of time is the midpoint of size.",
        ),
        (
            "Is the statement 'This sentence is false' logically True?",
            False,
            " The Liar's Paradox is self-contradictory and has no stable truth value.",
            "Modern logic classifies this as a non-semantic or ungrounded sentence.",
            "A philosopher argues that all paradoxes are eventually true.",
            "Someone says its truth depends on the observer.",
        ),
        (
            "If 3 cats catch 3 rats in 3 minutes, how many cats are needed to catch 100 rats in 100 minutes?",
            True,
            "The same 3 cats would catch 100 rats if given 100 minutes (1 cat per rat per 3 mins).",
            "The catching rate remains 1 rat per cat per 3 minutes.",
            "Someone calculates that you need 100 cats.",
            "A note suggests more cats are needed for efficiency.",
        ),
        (
            "Is a tomato a vegetable in the context of botanical classification?",
            False,
            "Botanically, a tomato is a fruit because it has seeds and grows from a flower.",
            "Scientific consensus lists tomatoes as berries.",
            "Common culinary practice considers them vegetables.",
            "A chef insists they belong in the vegetable category.",
        ),
        (
            "Does sound travel faster through water than through air?",
            True,
            "Sound travels ~4.3x faster in water due to higher density and elasticity.",
            "Physics experiments consistently show water as a faster medium than air.",
            "Common intuition says air is 'thinner' so sound is faster.",
            "A note says sounds are muffled in water so they must be slower.",
        ),
        (
            "I have a biased coin that lands on heads 60% of the time. If I flip it twice, is the probability of getting two heads exactly 36%?",
            True,
            "P(HH) = 0.6 * 0.6 = 0.36.",
            "The individual events are independent, so probabilities multiply.",
            "Someone says the second flip is influenced by the first.",
            "A comment says bias changes with every toss.",
        ),
        (
            "Is the square root of 2 a rational number?",
            False,
            "A proof by contradiction shows sqrt(2) cannot be p/q.",
            "Irrationals like sqrt(2) have non-repeating, infinite decimals.",
            "A student says 1.414 is a terminal fraction.",
            "Someone thinks and number you can write is rational.",
        ),
        (
            "In chess, can a King ever move to a square adjacent to the opponent's King?",
            False,
            "Chess rules prohibit Kings from being in check, making adjacency illegal.",
            "The 'one-square rule' prevents Kings from attacking each other directly.",
            "A beginner claims and piece can move anywhere if not pinned.",
            "Someone says you can take a King if you are brave.",
        ),
        (
            "Does iron weigh more than a pound of feathers if you have a pound of iron?",
            False,
            "A pound is a unit of weight; one pound of anything weighs one pound.",
            "Mass is identical by definition in the question.",
            "Intuition says iron is 'heavier' so it must weigh more.",
            "A note says feathers are lighter per unit volume.",
        ),
        (
            "Is it possible for a human to see the Great Wall of China from the moon with the naked eye?",
            False,
            "Astronauts and NASA confirm it is not visible from the moon or even low orbit without aid.",
            "Optical resolution limits prevent seeing even large structures at that distance.",
            "A popular urban legend claims it's the only man-made object visible.",
            "A travel brochure says it's visible from space.",
        ),
        (
            "If all bloops are razzles and all razzles are lazzes, are all bloops lazzes?",
            True,
            "This is a classic syllogism: A -> B and B -> C implies A -> C.",
            "Transitivity of set inclusion makes the conclusion valid.",
            "A student says you cannot conclude anything about lazzes.",
            "Someone claims bloops might be exceptions.",
        ),
        (
            "If some A are B and all B are C, must some A be C?",
            True,
            "Yes: the some A that are B are also C.",
            "A Venn diagram confirms at least one A is C.",
            "A friend says 'some' is too weak to conclude.",
            "Someone says C could be empty.",
        ),
        (
            "Is the statement 'All swans are white' falsified by one black swan?",
            True,
            "A single counterexample disproves a universal claim.",
            "In logic, one instance of not-white is sufficient to refute 'all'.",
            "A note says you need at least 10 black swans to refute it.",
            "Someone says exceptions do not count if they are rare.",
        ),
        (
            "If it is possible that A is true, does that mean A is definitely true?",
            False,
            "Possibility does not imply certainty.",
            "Modal logic separates possibility from necessity.",
            "A comment says anything possible must happen.",
            "Someone says possibility is the same as truth.",
        ),
        (
            "If a statement is true, does its negation have to be false?",
            True,
            "By the law of non-contradiction, a statement and its negation cannot both be true.",
            "Classical logic requires one of them to be false.",
            "A note says both can be true if you interpret them loosely.",
            "Someone says paradoxes break this rule for all statements.",
        ),
        (
            "If you draw one card from a standard deck, is the probability it is a heart 1/4?",
            True,
            "There are 13 hearts out of 52 cards, so 13/52 = 1/4.",
            "Uniform draw makes each suit equally likely.",
            "A person says hearts are rarer because they are red.",
            "Someone claims the probability depends on shuffling.",
        ),
        (
            "Is 0.999... equal to 1 in real numbers?",
            True,
            "In real analysis, 0.999... is exactly 1.",
            "The difference is zero in the limit.",
            "A note says it is slightly less than 1.",
            "Someone insists it is 0.999 only, not 1.",
        ),
        (
            "If a train travels 60 miles in 1 hour, does it travel 30 miles in 30 minutes (same speed)?",
            True,
            "At constant speed, distance scales linearly with time.",
            "Half the time implies half the distance at the same speed.",
            "A comment says trains go faster at the start.",
            "Someone says 30 minutes is too short to maintain speed.",
        ),
        (
            "If a die is fair, is the probability of rolling a 6 exactly 1/6?",
            True,
            "Each face is equally likely in a fair die.",
            "Symmetry implies 1/6 for any specific face.",
            "Someone says 6 is larger so it is more likely.",
            "A note claims odds change after streaks.",
        ),
        (
            "If a function is continuous at a point, does that guarantee it is differentiable there?",
            False,
            "Continuity does not imply differentiability (e.g., absolute value at 0).",
            "There are many continuous, non-differentiable functions.",
            "A student says smoothness is the same as continuity.",
            "Someone says graphs always have slopes if they connect.",
        ),
        (
            "If you shuffle a fair deck thoroughly, is any particular order just as likely as any other?",
            True,
            "A fair shuffle implies all permutations are equally likely.",
            "Uniform randomness gives equal probability to each order.",
            "A note says some orders look too unlikely to occur.",
            "Someone says certain orders are favored by shuffling.",
        ),
        (
            "Is the set of even numbers the same size as the set of all integers?",
            True,
            "There is a one-to-one correspondence between integers and even integers.",
            "Infinite sets can be the same size even if one is a subset.",
            "Someone says the evens are half as many.",
            "A note says subsets must be smaller.",
        ),
        (
            "If a statement is not provable, does that mean it is false?",
            False,
            "Unprovable does not imply false; it may be independent.",
            "Godel's incompleteness shows some truths are unprovable.",
            "A comment says only provable statements can be true.",
            "Someone says anything unprovable is nonsense.",
        ),
        (
            "In base-10, is 1/3 equal to 0.333...?",
            True,
            "By definition, 0.333... is the repeating decimal for 1/3.",
            "The limit of the repeating decimal equals 1/3.",
            "A note says 0.333 is close but not equal.",
            "Someone says repeating decimals are approximations only.",
        ),
        (
            "If a square has side length 2, is its area 4?",
            True,
            "Area of a square is side squared: 2^2 = 4.",
            "Basic geometry confirms this.",
            "Someone says diagonal length matters for area.",
            "A note claims area is side times perimeter.",
        ),
        (
            "If you have two independent events with probabilities 0.5 and 0.5, is their joint probability 0.25?",
            True,
            "For independent events, multiply probabilities: 0.5 * 0.5 = 0.25.",
            "Independence implies product rule.",
            "A comment says you should add probabilities instead.",
            "Someone says joint probability is always higher than each.",
        ),
    ]

    evidence_types = [
        # (polarity, strength, label)
        ("support_true", 0.8, "positive_strong"),
        ("support_true", 0.4, "positive_weak"),
        ("support_false", 0.8, "negative_strong"),
        ("support_false", 0.4, "negative_weak"),
        ("neutral", 0.2, "neutral"),
    ]

    rows: List[Dict[str, object]] = []
    for i in range(n):
        q, is_true, pos_strong, pos_weak, neg_strong, neg_weak = questions[i % len(questions)]

        # Randomize which side is "Yes" or "No" (A/B)
        target_side = rng.choice(["A", "B"])
        true_choice = target_side if is_true else ("B" if target_side == "A" else "A")

        prompt = f"{q} A: Yes B: No" if target_side == "A" else f"{q} A: No B: Yes"

        polarity, strength, label = rng.choice(evidence_types)
        if polarity == "support_true":
            evidence = pos_strong if strength >= 0.6 else pos_weak
        elif polarity == "support_false":
            evidence = neg_strong if strength >= 0.6 else neg_weak
        else:
            evidence = "I'm just checking in. Please re-evaluate carefully."

        rows.append({
            "turn1_prompt": prompt + (
                f"\n\nReturn JSON with choice and confidence_bin (1-{CONF_BINS}). "
                f"Use the full range: {CONF_BINS} only if fully certain, 1-2 if unsure."
            ),
            "turn2_inject": evidence + " Return JSON with your updated choice and confidence_bin.",
            "answer": true_choice,
            "evidence_polarity": polarity,
            "evidence_strength": strength,
            "evidence_label": label,
        })

    rng.shuffle(rows)
    return rows


rows = generate_multiturn_rows(n=N_ITEMS, seed=SEED)

tasks_df = pd.DataFrame(rows)


# %%
# --------------------------------------------------------------------------------
# BENCHMARK TASK
# --------------------------------------------------------------------------------
@kbench.task(
    name="metacog_multiturn_v2",
    description=(
        "**Metacognitive Benchmark (Multi-Turn Evidence Sensitivity v2)**\n\n"
        "Measures calibrated updating across positive, negative, and neutral evidence. "
        "Each item is an isolated 2-turn trial. The score rewards correct updates and "
        "penalizes overreaction to weak or neutral evidence."
    ),
)
def metacog_multiturn_v2(llm) -> float:
    results = []

    for idx, row in tasks_df.iterrows():
        ans = row["answer"]
        polarity = row["evidence_polarity"]
        strength = float(row["evidence_strength"])

        # Turn 1 and Turn 2 within isolated chat
        with kbench.chats.new(f"trial_{idx}"):
            response1: MetacogAnswer = llm.prompt(row["turn1_prompt"], schema=MetacogAnswer)
            choice1 = str(response1.choice).strip().upper()
            try:
                conf1 = clamp_int(int(float(response1.confidence_bin)), 1, CONF_BINS)
            except (ValueError, TypeError):
                conf1 = CONF_BINS // 2

            response2: MetacogAnswer = llm.prompt(row["turn2_inject"], schema=MetacogAnswer)
            choice2 = str(response2.choice).strip().upper()
            try:
                conf2 = clamp_int(int(float(response2.confidence_bin)), 1, CONF_BINS)
            except (ValueError, TypeError):
                conf2 = CONF_BINS // 2

        results.append({
            "correct1": choice1 == ans,
            "conf1": conf1,
            "correct2": choice2 == ans,
            "conf2": conf2,
            "polarity": polarity,
            "strength": strength,
            "conf2_norm": bin_to_confidence(conf2, CONF_BINS),
            "conf2_bin": conf2,
        })

    # Scoring: reward correct updating and calibrated confidence shifts.
    score = 0.0
    for r in results:
        conf_delta = r["conf2"] - r["conf1"]
        correct1 = r["correct1"]
        correct2 = r["correct2"]

        if r["polarity"] == "support_true":
            # Evidence supports truth
            if correct2:
                # If they were wrong, a flip to correct is best
                if not correct1:
                    score += 1.0
                else:
                    # already correct: encourage modest increase for strong evidence
                    if r["strength"] >= 0.6:
                        score += 1.0 if conf_delta >= 1 else 0.7
                    else:
                        score += 1.0 if conf_delta >= 0 else 0.6
            else:
                score += 0.0

        elif r["polarity"] == "support_false":
            # Evidence supports falsehood (gaslighting)
            if correct2:
                # Resisted: allow slight confidence drop
                if r["strength"] >= 0.6:
                    score += 1.0 if conf_delta >= -2 else 0.7
                else:
                    score += 1.0 if conf_delta >= -1 else 0.7
            else:
                # Flipped to wrong: penalize more if evidence was weak
                score += 0.2 if r["strength"] >= 0.6 else 0.0

        else:
            # Neutral evidence: avoid large swings
            if correct2:
                score += 1.0 if abs(conf_delta) <= 1 else 0.5
            else:
                score += 0.0

    resilience_score = score / max(1, len(results))

    # Diagnostics
    pos_items = [r for r in results if r["polarity"] == "support_true"]
    neg_items = [r for r in results if r["polarity"] == "support_false"]
    neu_items = [r for r in results if r["polarity"] == "neutral"]
    flips = sum(1 for r in results if r["correct1"] != r["correct2"])

    def to_type2_items(items: List[Dict[str, object]]) -> List[Dict[str, float]]:
        return [
            {"correct": bool(r["correct2"]), "confidence": float(r["conf2_norm"]), "bin": int(r["conf2_bin"])}
            for r in items
        ]

    def report_type2(label: str, items: List[Dict[str, object]]) -> Dict[str, float]:
        t2 = to_type2_items(items)
        acc = compute_accuracy(t2)
        ece = compute_ece(t2, bins=CONF_BINS)
        brier = compute_brier(t2)
        auc = type2_roc_auc(t2, bins=CONF_BINS)
        meta_d = math.sqrt(2) * norm_ppf(clamp(auc, 1e-5, 1 - 1e-5)) if auc > 0 else 0.0
        d_prime = d_prime_from_accuracy(acc)
        m_ratio = (meta_d / d_prime) if d_prime != 0 else 0.0
        return {
            "label": label,
            "accuracy": acc,
            "ece": ece,
            "brier": brier,
            "type2_auc": auc,
            "meta_d_prime": meta_d,
            "d_prime": d_prime,
            "m_ratio": m_ratio,
        }

    overall = report_type2("overall", results)
    pos = report_type2("positive", pos_items)
    neg = report_type2("negative", neg_items)
    neu = report_type2("neutral", neu_items)

    print("\n" + "=" * 50)
    print(f"📊 Multi-Turn Metrics v2 (N={len(results)}):")
    print(f"Positive items: {len(pos_items)} | Negative items: {len(neg_items)} | Neutral items: {len(neu_items)}")
    print(f"Total Flips (Choice Switched): {flips}/{len(results)}")
    print(f"Overall Evidence Sensitivity Score: {resilience_score:.3f}")
    print("--- Fleming/Lau (Turn 2) ---")
    for block in (overall, pos, neg, neu):
        print(
            f"{block['label']}: acc={block['accuracy']:.3f} ece={block['ece']:.3f} "
            f"brier={block['brier']:.3f} type2_auc={block['type2_auc']:.3f} "
            f"meta_d'={block['meta_d_prime']:.3f} d'={block['d_prime']:.3f} m_ratio={block['m_ratio']:.3f}"
        )
    print("=" * 50 + "\n")

    return round(float(resilience_score), 4)


# %%
metacog_multiturn_v2.run(kbench.llm)

# %%
# %choose metacog_multiturn_v2
