import os
import re
import json
import ast

def safe_float(match):
    return float(match.group(1)) if match else None

def extract_metrics(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    data = {
        "static": {},
        "multiturn_v1": {},
        "multiturn_v2": {
            "overall": {},
            "positive": {},
            "negative": {},
            "neutral": {}
        },
        "bootstrap": {}
    }

    # --- Static Monitoring (metacog_single_item) ---
    static_match = re.search(r"Full Metrics: ({.*?})", content)
    if static_match:
        try:
            data["static"] = ast.literal_eval(static_match.group(1))
        except: pass

    # --- Multi-Turn V1: Bayesian Sycophancy (metacog_multiturn) ---
    # Look for section without 'v2'
    v1_section = re.search(r"📊 Multi-Turn Metrics \(N=\d+\):(.*?)====", content, re.DOTALL)
    if v1_section:
        sec_text = v1_section.group(1)
        data["multiturn_v1"]["positive_update_rate"] = safe_float(re.search(r"Positive Evidence Update Rate: ([\d.]+)", sec_text))
        data["multiturn_v1"]["negative_resistance_rate"] = safe_float(re.search(r"Negative Evidence Resistance Rate: ([\d.]+)", sec_text))
        data["multiturn_v1"]["bayesian_resilience"] = safe_float(re.search(r"Overall Bayesian Resilience: ([\d.]+)", sec_text))
        
        flips = re.search(r"Total Flips \(Choice Switched\): (\d+)/(\d+)", sec_text)
        if flips:
            data["multiturn_v1"]["total_flips"] = int(flips.group(1))
            data["multiturn_v1"]["total_trials"] = int(flips.group(2))
            
        gas = re.search(r"Succumbed to Gaslighting: (\d+)/(\d+)", sec_text)
        if gas:
            data["multiturn_v1"]["gaslighting_flips"] = int(gas.group(1))
            data["multiturn_v1"]["gaslighting_trials"] = int(gas.group(2))

    # --- Multi-Turn V2: Nuanced M-Ratio (metacog_multiturn_v2) ---
    v2_section = re.search(r"📊 Multi-Turn Metrics v2 \(N=\d+\):(.*?)====", content, re.DOTALL)
    if v2_section:
        sec_text = v2_section.group(1)
        data["multiturn_v2"]["sensitivity_score"] = safe_float(re.search(r"Overall Evidence Sensitivity Score: ([\d.]+)", sec_text))
        
        flips = re.search(r"Total Flips \(Choice Switched\): (\d+)/(\d+)", sec_text)
        if flips:
            data["multiturn_v2"]["total_flips"] = int(flips.group(1))
            data["multiturn_v2"]["total_trials"] = int(flips.group(2))

        # Nested Fleming/Lau Metrics
        for cond in ["overall", "positive", "negative", "neutral"]:
            pattern = rf"{cond}: acc=([\d.]+) ece=([\d.]+) brier=([\d.]+) type2_auc=([\d.]+) meta_d'?=([\d.]+) d'=([\d.]+) m_ratio=([\d.]+)"
            m = re.search(pattern, sec_text)
            if m:
                data["multiturn_v2"][cond] = {
                    "acc": float(m.group(1)),
                    "ece": float(m.group(2)),
                    "brier": float(m.group(3)),
                    "type2_auc": float(m.group(4)),
                    "meta_d_prime": float(m.group(5)),
                    "d_prime": float(m.group(6)),
                    "m_ratio": float(m.group(7))
                }

    # --- Bootstrap (metacog_v4) ---
    boot_match = re.search(r"Bootstrap M-Ratio: ([\d.]+) ± ([\d.]+)", content)
    if boot_match:
        data["bootstrap"]["mean"] = float(boot_match.group(1))
        data["bootstrap"]["ci_95"] = float(boot_match.group(2))

    seeds = re.search(r"Per-seed: \[(.*?)\]", content)
    if seeds:
        try: data["bootstrap"]["per_seed"] = [float(x.strip()) for x in seeds.group(1).split(",")]
        except: pass

    return data

def main():
    results_dir = "results"
    output_file = "results_aggregated.json"
    
    model_name_map = {
        "claude_opus": "Claude Opus 4.6",
        "claude_sonnet": "Claude Sonnet 4.6",
        "deepseek-v3.1": "DeepSeek V3.1",
        "deepseek-v3.2": "DeepSeek V3.2",
        "gemini-2.5-flash": "Gemini 2.5 Flash",
        "gemini-3-flash-preview": "Gemini 3 Flash Preview",
        "gemini-3.1-flash-lite-preview": "Gemini 3.1 Flash-Lite",
        "gemini-3.1-pro-preview": "Gemini 3.1 Pro",
        "gpt-oss-20b": "GPT-OSS-20B",
        "glm5": "GLM-5",
        "gpt5.4": "GPT-5.4",
        "gpt5.4_mini": "GPT-5.4 Mini"
    }

    aggregated_data = {}

    for filename in os.listdir(results_dir):
        if filename.endswith(".md"):
            base_name = filename.replace(".md", "")
            formal_name = model_name_map.get(base_name, base_name)
            
            file_path = os.path.join(results_dir, filename)
            
            # Skip empty files
            if os.path.getsize(file_path) == 0:
                print(f"Skipping empty file: {filename}")
                continue
                
            print(f"Processing {filename} as {formal_name}...")
            metrics = extract_metrics(file_path)
            aggregated_data[formal_name] = metrics

    with open(output_file, 'w') as f:
        json.dump(aggregated_data, f, indent=4)
    
    print(f"Saved aggregated results to {output_file}")

if __name__ == "__main__":
    main()
