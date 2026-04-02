# Generates a procedural metacognition dataset with difficulty + trap labels.
import json
from shared.metacog_dataset import generate_metacog_rows


def write_jsonl(path: str, rows: List[Dict[str, object]]) -> None:
    with open(path, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    data = generate_metacog_rows(n=200, seed=42)
    write_jsonl("tasks_metacog_v1.jsonl", data)
    print("Wrote tasks_metacog_v1.jsonl")
