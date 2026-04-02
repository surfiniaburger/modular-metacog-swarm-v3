def normalize_model_name(name: str) -> str:
    if not isinstance(name, str):
        return str(name)
    if name.startswith("ollama/"):
        return name.split("/", 1)[1]
    return name
