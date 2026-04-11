import pandas as pd
import os
import csv
import re

# --- Configuration ---
DIR = 'kaggle_notebooks/'
FILES = {
    "V1: Pilot": f'{DIR}coding_safety_dataset.csv',
    "V2: Core": f'{DIR}coding_safety_dataset_500.csv',
    "V3: CVE": f'{DIR}coding_safety_dataset_v3_cve_500.csv',
    "MASTER": f'{DIR}mcsb_master_v2.csv'
}

def clean_choice_relaxed(x):
    if x is None: return None
    x = str(x).strip().lower()
    if x.startswith("a") or "vulnerable" in x or "unsafe" in x: return "a"
    if x.startswith("b") or "safe" in x or "benign" in x: return "b"
    if "1" in x: return "a"
    if "0" in x: return "b"
    if "true" in x: return "a"
    if "false" in x: return "b"
    return None

def audit_file(name, path):
    if not os.path.exists(path):
        print(f"❌ {name}: File not found at {path}")
        return

    print(f"\n🔍 Auditing {name}: {path}")
    
    # 1. Physical Line Count
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    physical_lines = len(lines)
    
    # 2. Logical Record Count (using standard pandas)
    try:
        df = pd.read_csv(path, on_bad_lines='warn')
        logical_records = len(df)
    except Exception as e:
        print(f"   ⚠️ Pandas load failed: {e}")
        df = pd.DataFrame()
        logical_records = 0

    # 3. Structural Integrity Report
    print(f"   📊 Structure: {physical_lines} physical lines | {logical_records} logical records")
    
    if logical_records == 0:
        return

    # 4. Column Alignment Cross-Check
    # We search EVERY column for the string "Tier" to see if it's shifted.
    alignment_issues = 0
    shifted_tiers = []
    
    # We also check if the 'answer' column (or equivalent) is parseable
    # V3 uses 'is_vulnerable' instead of 'answer' in source? 
    # Let's check columns.
    target_col = 'answer'
    if 'is_vulnerable' in df.columns:
        target_col = 'is_vulnerable'
    elif 'ans' in df.columns:
        target_col = 'ans'
    
    print(f"   🏷️  Target Answer Column: '{target_col}'")
    
    unparseable_answers = 0
    chopped_records = 0
    
    for idx, row in df.iterrows():
        # 1. Check for Tier string in ANY column
        tier_found_at = -1
        for i, col in enumerate(df.columns):
            if "Tier" in str(row[col]):
                tier_found_at = i
                break
        
        # In MASTER, 'tier' is column 10 (0-indexed)
        if name == "MASTER" and tier_found_at != 10 and tier_found_at != -1:
            alignment_issues += 1
            chopped_records += 1
            if len(shifted_tiers) < 3:
                shifted_tiers.append(f"Row {idx}: Tier at column {tier_found_at} (Expected 10). Value: {row[df.columns[tier_found_at]]}")

        # 2. Check parsing
        if target_col in df.columns:
            ans = row[target_col]
            if clean_choice_relaxed(ans) is None:
                unparseable_answers += 1
    
    # 5. Results Summary
    if chopped_records > 0:
        print(f"   🚨 CORRUPTION: {chopped_records} chopped/shifted records detected!")
        for issue in shifted_tiers:
            print(f"      └─ {issue}")
    elif alignment_issues > 0:
        print(f"   ⚠️ ALIGNMENT: {alignment_issues} shifted records detected!")
    else:
        print(f"   ✅ ALIGNMENT: Structural integrity looks good.")

    if unparseable_answers > 0:
        print(f"   ⚠️ PARSING: {unparseable_answers} unparseable labels in '{target_col}' column.")
    else:
        print(f"   ✅ PARSING: All labels in '{target_col}' are parseable.")

def deep_audit_master(path):
    """Deep inspection of the merged master dataset."""
    print(f"\n{'='*60}")
    print(f"🔬 DEEP MASTER AUDIT: {path}")
    print(f"{'='*60}")
    
    df = pd.read_csv(path, on_bad_lines='warn')
    
    # 1. Per-tier breakdown
    print(f"\n📊 PER-TIER RECORD COUNTS:")
    tier_counts = df['tier'].value_counts()
    for tier, count in tier_counts.items():
        print(f"   {tier}: {count}")
    print(f"   TOTAL: {len(df)}")
    
    # 2. Label distribution per tier
    print(f"\n🏷️  LABEL DISTRIBUTION (answer column):")
    for tier in sorted(df['tier'].unique()):
        subset = df[df['tier'] == tier]
        dist = subset['answer'].apply(clean_choice_relaxed).value_counts(dropna=False)
        nans = subset['answer'].apply(clean_choice_relaxed).isna().sum()
        print(f"   {tier}:")
        for label, count in dist.items():
            label_str = label if label is not None else "UNPARSEABLE"
            print(f"      {label_str}: {count}")
        if nans > 0:
            print(f"      ⚠️  {nans} unparseable!")
    
    # 3. Critical column completeness
    critical_cols = ['task_id', 'code', 'prompt1', 'inject2', 'answer', 
                     'has_conflict', 'evidence_strength', 'tier']
    print(f"\n📋 COLUMN COMPLETENESS:")
    for col in critical_cols:
        if col not in df.columns:
            print(f"   ❌ {col}: MISSING FROM SCHEMA")
            continue
        total = len(df)
        non_null = df[col].notna().sum()
        empty_str = (df[col].astype(str).str.strip() == '').sum()
        valid = non_null - empty_str
        pct = valid / total * 100
        status = "✅" if pct == 100 else "⚠️" if pct >= 95 else "❌"
        print(f"   {status} {col}: {valid}/{total} ({pct:.1f}%)")
    
    # 4. Duplicate task_id check
    dupes = df['task_id'].duplicated().sum()
    if dupes > 0:
        print(f"\n   🚨 DUPLICATE task_ids: {dupes}")
    else:
        print(f"\n   ✅ No duplicate task_ids.")
    
    # 5. Sample rows from each tier for visual sanity
    print(f"\n🔍 SAMPLE ROWS (first per tier):")
    for tier in sorted(df['tier'].unique()):
        row = df[df['tier'] == tier].iloc[0]
        print(f"\n   --- {tier} ---")
        print(f"   task_id:  {row['task_id']}")
        print(f"   answer:   {row['answer']}")
        prompt_preview = str(row.get('prompt1', ''))[:80].replace('\n', '\\n')
        inject_preview = str(row.get('inject2', ''))[:80].replace('\n', '\\n')
        print(f"   prompt1:  {prompt_preview}...")
        print(f"   inject2:  {inject_preview}...")

def run_audit():
    print("="*60)
    print("🛡️  MCSB DATASET SECURITY AUDIT (SOURCE-TO-MASTER)")
    print("="*60)
    
    for name, path in FILES.items():
        audit_file(name, path)
    
    # Deep audit on master
    master_path = FILES["MASTER"]
    if os.path.exists(master_path):
        deep_audit_master(master_path)
    
    print("\n" + "="*60)
    print("🏁 Audit Complete.")
    print("="*60)

if __name__ == "__main__":
    run_audit()
