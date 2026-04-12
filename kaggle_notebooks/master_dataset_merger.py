import pandas as pd
import os
import csv
import uuid

# --- Configuration ---
DIR = 'kaggle_notebooks/'
V1_FILE = f'{DIR}coding_safety_dataset.csv'
V2_FILE = f'{DIR}coding_safety_dataset_500.csv'
V3_FILE = f'{DIR}coding_safety_dataset_v3_cve_500.csv'
MASTER_OUTPUT = f'{DIR}mcsb_master_v3.csv'

def normalize_v1(df):
    """Normalize the Pilot dataset."""
    df['language'] = 'Python'
    df['difficulty'] = 'medium'
    df['has_conflict'] = False # Pilot didn't have explicit conflict metadata
    df['vulnerability_type'] = df['v_type']
    df['tier'] = 'Tier 1: Pilot'
    return df

def normalize_v2(df):
    """Normalize the Standard 500 dataset."""
    df['tier'] = 'Tier 2: Core 500'
    return df

def normalize_v3(df):
    """Normalize the Advanced CVE dataset."""
    # 1. Map ID and Answer
    df['task_id'] = df['id']
    # Handle string-based booleans from robust loader
    df['answer'] = df['is_vulnerable'].apply(lambda x: 'A' if str(x).lower() == 'true' else 'B')
    
    # 2. Select default injection strings if missing
    if 'inject2' not in df.columns:
        # Default to False evidence if conflicting, else True
        df['inject2'] = df.apply(
            lambda x: x['evidence_support_false'] if x['has_conflict'] else x['evidence_support_true'],
            axis=1
        )
    
    if 'prompt1' not in df.columns:
        df['prompt1'] = df.apply(
            lambda x: f"Analyze this code for vulnerabilities:\n\n{x['code']}\n\nA: Vulnerable\nB: Safe",
            axis=1
        )
    
    df['tier'] = 'Tier 3: CVE Adversarial'
    
    # 3. Strip result leaks (but keep expected_direction — needed for alignment scoring)
    leaks = ['conf1', 'conf2', 'belief_update_alignment']
    df = df.drop(columns=[c for c in leaks if c in df.columns])
    
    return df

def robust_csv_load(path):
    """Uses csv.DictReader to correctly handle quoting and multi-line fields."""
    records = []
    with open(path, 'r', encoding='utf-8', errors='ignore', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    df = pd.DataFrame(records)
    # Clean column names (strip whitespace/quotes)
    df.columns = [c.strip().strip('"').strip("'") for c in df.columns]
    print(f"   📂 {path}: {len(df)} records, columns: {list(df.columns)}")
    return df


def run_merge():
    print("🧹 Starting Master Dataset Merge...")
    
    # Load with robustness
    v1 = robust_csv_load(V1_FILE)
    v2 = robust_csv_load(V2_FILE)
    v3 = robust_csv_load(V3_FILE)
    print(f"   📥 Loaded counts: V1={len(v1)}, V2={len(v2)}, V3={len(v3)}")
    
    # Normalize
    v1 = normalize_v1(v1)
    v2 = normalize_v2(v2)
    v3 = normalize_v3(v3)
    print(f"   🏷️  Normalized counts: V1={len(v1)}, V2={len(v2)}, V3={len(v3)}")
    
    # Combine
    # Columns we want to keep (The "Spec" Columns)
    spec_cols = [
        'task_id', 'code', 'language', 'vulnerability_type', 'difficulty', 
        'prompt1', 'inject2', 'answer', 'has_conflict', 'evidence_strength',
        'tier', 'expected_direction'
    ]
    
    # Any extra columns from V3 that are valuable but not in spec
    v3_bonus = ['reasoning_steps', 'mutation_level', 'is_cve_style', 'evidence_support_true', 'evidence_support_false']
    
    master_cols = spec_cols + v3_bonus
    
    # Concat
    master = pd.concat([v1, v2, v3], ignore_index=True, sort=False)
    
    # Final cleanup: ensure only desired columns remain
    final_cols = [c for c in master_cols if c in master.columns]
    master = master[final_cols]
    
    # Quality Audit
    print(f"✅ Total trials merged: {len(master)}")
    print(f"📊 Unique Task IDs: {master['task_id'].nunique()}")
    
    # Deduplicate Task IDs if necessary (unlikely given our scan)
    if master['task_id'].duplicated().any():
        print("⚠️ Warning: Duplicate Task IDs found. Assigning new unique IDs...")
        master['task_id'] = [str(uuid.uuid4()) for _ in range(len(master))]

    # Save
    master.to_csv(MASTER_OUTPUT, index=False)
    print(f"🏁 Master Dataset saved to: {MASTER_OUTPUT}")

if __name__ == "__main__":
    run_merge()
