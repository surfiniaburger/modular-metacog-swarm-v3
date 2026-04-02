# sentinel/mcp_server.py
from fastmcp import FastMCP
from sentinel.classifier import IntentClassifier

mcp = FastMCP("sentinel")
classifier = IntentClassifier()

@mcp.tool()
async def classify_intent(text: str) -> dict:
    """
    Main entry point for intent classification.
    """
    result = classifier.classify(text)
    return {
        "category": result.category.name,
        "is_correction": result.is_correction
    }

if __name__ == "__main__":
    mcp.run()
