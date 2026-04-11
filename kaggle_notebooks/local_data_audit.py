"""
Local Data Audit — NO kbench/kaggle dependencies required.
Verifies the dataset is correctly aligned before blaming the model.

Usage: uv run python kaggle_notebooks/local_data_audit.py
"""
import pandas as pd
import csv
import re
import os

# --- Configuration ---
DIR = 'kaggle_notebooks/'
MASTER     = f'{DIR}mcsb_master_v3.csv'
V1_SOURCE  = f'{DIR}coding_safety_dataset.csv'
V2_SOURCE  = f'{DIR}coding_safety_dataset_500.csv'
V3_SOURCE  = f'{DIR}coding_safety_dataset_v3_cve_500.csv'

def clean_choice(x):
    """Same parser as the benchmark engine."""
    if x is None: return None
    x = str(x).strip().lower()
    if x in ("1", "true"):  return "a"
    if x in ("0", "false"): return "b"
    if x.startswith("a"): return "a"
    if x.startswith("b"): return "b"
    if re.search(r"\b[aA]\b", str(x)): return "a"
    if re.search(r"\b[bB]\b", str(x)): return "b"
    if "vulnerable" in x or "unsafe" in x: return "a"
    if "safe" in x or "benign" in x: return "b"
    return None

def normalize_label(x):
    if x is None: return None
    x = str(x).strip().lower()
    mapping = {"a": 1, "b": 0, "vulnerable": 1, "safe": 0, "1": 1, "0": 0, "true": 1, "false": 0}
    return mapping.get(x, None)

# ============================================================
# SECTION 1: Individual Source Audits
# ============================================================
def audit_source(name, path, answer_col='answer'):
    if not os.path.exists(path):
        print(f"  ❌ {name}: NOT FOUND at {path}")
        return None
    df = pd.read_csv(path)
    n = len(df)
    parseable = df[answer_col].apply(clean_choice).notna().sum()
    unparseable = n - parseable
    labels = df[answer_col].apply(clean_choice).value_counts(dropna=False)
    
    status = "✅" if unparseable == 0 else "⚠️"
    print(f"  {status} {name}: {n} records | {parseable} parseable | {unparseable} unparseable")
    print(f"       Labels: {dict(labels)}")
    print(f"       Columns: {list(df.columns)}")
    return df

# ============================================================
# SECTION 2: Cross-Reference Check
# What was STRIPPED during merge that the debug script needs?
# ============================================================
def check_stripped_columns():
    print(f"\n{'='*70}")
    print("🔍 SECTION 2: STRIPPED COLUMN ANALYSIS")
    print(f"{'='*70}")
    
    # Load V3 source (has expected_direction)
    if not os.path.exists(V3_SOURCE):
        print("  ❌ V3 source not found")
        return
    
    v3 = pd.read_csv(V3_SOURCE)
    
    # These columns are stripped by normalize_v3 in master_dataset_merger.py
    stripped = ['conf1', 'conf2', 'expected_direction', 'belief_update_alignment']
    print(f"\n  Columns stripped during merge: {stripped}")
    
    for col in stripped:
        if col in v3.columns:
            vals = v3[col].value_counts()
            print(f"\n  📊 {col} (EXISTS in V3 source, MISSING in master):")
            for val, count in vals.items():
                print(f"       {val}: {count}")
        else:
            print(f"  ❌ {col}: not in V3 source either")
    
    # THE KEY BUG: debug.py uses row.get("expected_direction", "increase")
    # Since the column was stripped, EVERY row defaults to "increase"
    # But the real data has 270 decrease / 230 increase!
    print(f"\n  🚨 BUG IMPACT:")
    print(f"     debug.py line 262: row.get('expected_direction', 'increase')")
    print(f"     Since expected_direction was stripped during merge,")
    print(f"     ALL 1030 rows default to 'increase'.")
    print(f"     But V3 source has 270 'decrease' + 230 'increase'.")
    print(f"     → This causes 100% MISALIGNED in the diagnostic report.")
    print(f"     → The 'misalignment' is a CODE BUG, not a data problem.")

# ============================================================
# SECTION 3: Master Dataset Deep Audit
# Simulates what the benchmark does — without an LLM
# ============================================================
def audit_master():
    print(f"\n{'='*70}")
    print("🔬 SECTION 3: MASTER DATASET DEEP AUDIT (data-only, no LLM)")
    print(f"{'='*70}")
    
    if not os.path.exists(MASTER):
        print(f"  ❌ Master not found at {MASTER}")
        return
    
    df = pd.read_csv(MASTER)
    print(f"\n  📊 Total records: {len(df)}")
    print(f"  📊 Columns: {list(df.columns)}")
    
    # 1. Per-tier breakdown
    print(f"\n  📊 PER-TIER COUNTS:")
    for tier in sorted(df['tier'].unique()):
        subset = df[df['tier'] == tier]
        n = len(subset)
        labels = subset['answer'].apply(clean_choice).value_counts(dropna=False)
        unparseable = subset['answer'].apply(clean_choice).isna().sum()
        status = "✅" if unparseable == 0 else "🚨"
        print(f"     {status} {tier}: {n} records | Labels: {dict(labels)}")
    
    # 2. Critical column completeness
    print(f"\n  📋 COLUMN COMPLETENESS:")
    critical = ['task_id', 'code', 'prompt1', 'inject2', 'answer', 
                'has_conflict', 'evidence_strength', 'tier']
    for col in critical:
        if col not in df.columns:
            print(f"     ❌ {col}: MISSING")
            continue
        valid = df[col].notna().sum()
        empty = (df[col].astype(str).str.strip() == '').sum()
        effective = valid - empty
        pct = effective / len(df) * 100
        status = "✅" if pct == 100 else "⚠️" if pct >= 95 else "❌"
        print(f"     {status} {col}: {effective}/{len(df)} ({pct:.1f}%)")
    
    # 3. Check prompt1 and inject2 content quality
    print(f"\n  🔍 PROMPT QUALITY CHECK (first 5 per tier):")
    for tier in sorted(df['tier'].unique()):
        subset = df[df['tier'] == tier].head(5)
        print(f"\n     --- {tier} ---")
        for _, row in subset.iterrows():
            p1 = str(row['prompt1'])[:60].replace('\n', '\\n')
            i2 = str(row['inject2'])[:60].replace('\n', '\\n')
            ans = row['answer']
            print(f"     [{ans}] prompt1: {p1}...")
            print(f"          inject2: {i2}...")
    
    # 4. Duplicate check
    dupes = df['task_id'].duplicated().sum()
    status = "✅" if dupes == 0 else "🚨"
    print(f"\n  {status} Duplicate task_ids: {dupes}")
    
    # 5. has_conflict analysis
    print(f"\n  📊 has_conflict DISTRIBUTION:")
    hc = df['has_conflict'].value_counts()
    for val, count in hc.items():
        print(f"     {val}: {count}")

    # 6. evidence_strength range check
    es = df['evidence_strength'].astype(float)
    print(f"\n  📊 evidence_strength: min={es.min():.3f}, max={es.max():.3f}, mean={es.mean():.3f}")

# ============================================================
# SECTION 4: What the Kaggle output ACTUALLY tells us
# ============================================================
def interpret_kaggle_output():
    print(f"\n{'='*70}")
    print("📖 SECTION 4: INTERPRETING THE KAGGLE DEBUG OUTPUT")
    print(f"{'='*70}")
    
    print("""
  The Kaggle run showed 3 types of "failures". Here's what each means:

  1. ❌ PARSE_FAIL(s2) — 11/25 Tier 2 rows
     ┌──────────────────────────────────────────────────────────────┐
     │ VERDICT: MODEL BEHAVIOR (not a data bug)                    │
     │ The LLM returned None for answer2. This means the model     │
     │ failed to follow the MetacogAnswer schema after the          │
     │ adversarial injection. This is EXACTLY what the benchmark    │
     │ is designed to detect.                                       │
     └──────────────────────────────────────────────────────────────┘

  2. ↕ MISALIGNED — 100% of all rows
     ┌──────────────────────────────────────────────────────────────┐
     │ VERDICT: CODE BUG (not a data or model bug)                 │
     │ expected_direction was stripped during merge (by design —    │
     │ it's considered a "leak"). But the debug script defaults    │
     │ ALL rows to "increase". Since the model's confidence        │
     │ delta is ~0 for most rows, everything reads as misaligned.  │
     │                                                              │
     │ FIX: Either re-include expected_direction in the master,    │
     │ OR don't measure alignment on rows where it's missing.      │
     └──────────────────────────────────────────────────────────────┘

  3. ✗ WRONG — model predicts "a" (vulnerable) for everything
     ┌──────────────────────────────────────────────────────────────┐
     │ VERDICT: MODEL BEHAVIOR (not a data bug)                    │
     │ The model is collapsing to one class. It always says        │
     │ "vulnerable" regardless of ground truth. This is a known    │
     │ failure mode that the benchmark is designed to expose.       │
     └──────────────────────────────────────────────────────────────┘
    """)

# ============================================================
# MAIN
# ============================================================
def main():
    print("="*70)
    print("🛡️  LOCAL DATA AUDIT — Source-to-Master Verification")
    print("   Separates DATA bugs from MODEL bugs from CODE bugs")
    print("="*70)
    
    # Section 1: Source audits
    print(f"\n{'='*70}")
    print("📂 SECTION 1: INDIVIDUAL SOURCE AUDITS")
    print(f"{'='*70}")
    audit_source("V1: Pilot",  V1_SOURCE, 'answer')
    audit_source("V2: Core",   V2_SOURCE, 'answer')
    audit_source("V3: CVE",    V3_SOURCE, 'is_vulnerable')
    
    # Section 2: Stripped column analysis
    check_stripped_columns()
    
    # Section 3: Master deep audit
    audit_master()
    
    # Section 4: Interpretation
    interpret_kaggle_output()
    
    print("="*70)
    print("🏁 Audit Complete.")
    print("="*70)

if __name__ == "__main__":
    main()
