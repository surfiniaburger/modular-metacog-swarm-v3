# Kaggle Benchmarks Resource Grant: Application Draft

**Project Name:** Metacognitive Coding Safety Leaderboard (MCSL)
**Primary Contact:** [USER_NAME]
**Organization:** Independent / Kaggle Community

---

### Phase 1: Problem Statement
Current LLM evaluation for Coding (HumanEval, MBPP) focuses on *correctness* but ignores *trustworthiness*. In real-world software engineering, a model that is "wrong but confident" is significantly more dangerous than a model that is "wrong but aware of its uncertainty." 

Most frontier models exhibit **Metacognitive Flatness**—high reasoning capability decoupled from internal monitoring. Our project implements a rigorous multi-turn framework based on Signal Detection Theory (SDT) to measure a model's **M-Ratio** (Metacognitive Efficiency). 

Specifically, we want to solve the "Trustworthiness Gap" in **Coding Safety**: Can a model correctly identify a vulnerability (e.g., SQL Injection) and maintain its belief against misleading feedback, or correctly recalibrate its confidence when presented with expert counter-evidence?

### Phase 2: Benchmark Methodology
Our benchmark uses the `kaggle-benchmarks` SDK to implement a **2-Turn Evidence Probe**:
1. **Turn 1 (Static Probe):** Model identifies if a code snippet is vulnerable and provides a confidence bin (1-6).
2. **Turn 2 (In-Context Evidence):** A simulated user provides high/low quality evidence (Expert verification vs. Senior-dev gaslighting).
3. **Metrics:** We calculate the **M-Ratio (`meta_d' / d'`)** which mathematically isolates a model's self-monitoring ability from its raw code-reasoning ability.

### Phase 3: Alignment with DeepMind Cognitive Framework
This benchmark specifically targets **Section 7.7 (Metacognition)** and **Section 7.8.5 (Conflict Resolution)** of the DeepMind AGI framework. By measuring how models handle contradictory evidence in a safety-critical domain (Coding), we provide a "Cognitive Profile" that traditional accuracy-based leaderboards cannot.

### Phase 4: Resource Request
* **High Compute Quota:** To run 1000+ multi-turn trials across all frontier models (GPT-5, Claude 4, Gemini 3 Ultra) simultaneously to maintain a real-time leaderboard.
* **Managed Infrastructure:** We want Kaggle to host the "Metacognitive Trustworthiness" leaderboard, providing the community with a score that tells them *when* to trust a model's code suggestions.
* **Implementation Support:** Assistance in integrating high-fidelity "Expert Evidence" streams from real CVE (Common Vulnerabilities and Exposures) databases.

### Phase 5: Expected Impact
We aim to establish the **MCSL** as the industry-standard "Trustworthiness Score" for AI coding assistants. This will help developers decide which model tiers are safe for production use and drive model providers to prioritize self-correction and calibration alongside raw performance.
