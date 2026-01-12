class PromptService:
    @staticmethod
    def build(question: str, context_chunks: list[str]) -> str:
        context = "\n\n".join(context_chunks)
        
        prompt = (
            "You are an expert academic advisor. Answer the question using only the context below.\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{question}\n\n"
            "Instructions:\n"
            "- Give a clear, complete answer in natural language.\n"
            "- Check eligibility lists carefully if present.\n"
            "- Reference context sections if helpful.\n"
            "- Combine info from multiple chunks if needed.\n"
            "- Say 'The information is not provided in the context.' if unknown.\n"
            "- Do NOT output JSON, braces, lists, or code.\n\n"
            "Answer:"
        )
        return prompt


# def build_rag_prompt(question: str, top_chunks: list[str]) -> str:
#     """
#     Build a prompt for RAG using the retrieved chunks as context.
#     """
#     context = "\n\n".join(top_chunks)
#     prompt = (
#         f"You are a helpful assistant. Use the following context to answer the question.\n\n"
#         f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
#     )
#     return prompt
