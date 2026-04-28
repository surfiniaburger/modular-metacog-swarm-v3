import csv
import sys
import os
from collections import Counter

def run_audit(file_path):
    print(f"🔍 Starting Audit for: {file_path}")
    if not os.path.exists(file_path):
        print(f"❌ Error: File {file_path} not found.")
        return

    try:
        # Increase field size limit for large CVE fields
        csv.field_size_limit(min(sys.maxsize, 2**31 - 1)) 

        physical_lines = 0
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                physical_lines += 1
        print(f"📊 Physical Lines: {physical_lines}")

        safety_counts = Counter()
        answer_counts = Counter()
        strengths = set()
        languages = Counter()
        has_conflict_counts = Counter()
        tier_counts = Counter()
        
        rows_count = 0
        bad_languages = []
        inconsistent_tiers = []

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            print(f"📋 Columns: {headers}")
            
            for row in reader:
                rows_count += 1
                safety_counts[row.get('safety', '').strip()] += 1
                answer_counts[row.get('answer', '').strip()] += 1
                
                s = row.get('evidence_strength', '')
                if s:
                    try:
                        strengths.add(float(s))
                    except ValueError:
                        pass
                
                lang = row.get('language', '').strip()
                languages[lang] += 1
                if not any(c.isalpha() for c in lang):
                    bad_languages.append(lang)
                
                tier = row.get('tier', '').strip()
                tier_counts[tier] += 1
                if 'Tier 3' not in tier:
                    inconsistent_tiers.append((row.get('task_id'), tier))
                
                hc = row.get('has_conflict', '').strip().lower()
                has_conflict_counts[hc] += 1

        print(f"📊 Logical Records (CSV Reader): {rows_count}")
        
        # 1. Class Balance
        print("\n⚖️ Class Balance (safety column):")
        for k, v in safety_counts.items():
            print(f"   {k}: {v}")
        
        print("\n⚖️ Class Balance (answer column):")
        for k, v in answer_counts.items():
            print(f"   {k}: {v}")

        # 1.5 Conflict Distribution
        print("\n⚔️ Conflict Distribution:")
        for k, v in has_conflict_counts.items():
            print(f"   {k}: {v}")

        # 2. Evidence Strength Palette
        print("\n🎨 Evidence Strength Palette:")
        palette = sorted(list(strengths))
        print(palette)
        expected_palette = [0.15, 0.3, 0.55, 0.8, 0.95]
        is_valid = all(any(abs(p - e) < 0.001 for p in palette) for e in expected_palette)
        if is_valid and len(palette) == len(expected_palette):
            print("✅ Palette matches discrete requirements.")
        else:
            print("⚠️ Palette mismatch or contains extra values.")

        # 3. Language Plausibility
        print("\n🌍 Language Top 10:")
        for lang, count in languages.most_common(10):
            print(f"   {lang}: {count}")
            
        if bad_languages:
            print(f"⚠️ Found {len(bad_languages)} rows with non-plausible languages!")
            print(f"   Examples: {bad_languages[:5]}")
        else:
            print("✅ All languages contain at least one letter.")

        # 4. Structural Integrity
        if inconsistent_tiers:
            print(f"🚨 Structural Issue? Found {len(inconsistent_tiers)} rows where 'tier' is unexpected.")
            for tid, t in inconsistent_tiers[:5]:
                print(f"   {tid}: {t}")
        else:
            print("✅ Column 'tier' looks consistent.")

    except Exception as e:
        print(f"💥 Audit failed with error: {e}")

if __name__ == "__main__":
    target = "kaggle_notebooks/cve_decision_benchmark_v1.csv"
    run_audit(target)
