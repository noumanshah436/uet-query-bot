import ollama


class LLMService:
    def __init__(self, model: str = "llama3.2"):
        # "gemma3:4b" or "llama3.2"
        self.model = model

    def generate(self, prompt: str) -> str:
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response["message"]["content"]
