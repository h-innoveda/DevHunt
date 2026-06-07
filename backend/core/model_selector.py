def classify_query(user_message: str, has_rag_docs: bool = False) -> str:
    """
    Model selection optimized for SPEED on free tier.

    Confirmed available models (from ListModels):
      gemini-3.1-flash-lite  : FASTEST — 15 RPM, 250K TPM, 500 RPD  <- default
      gemini-2.5-flash       : Smarter  — 5 RPM,  250K TPM,  20 RPD  <- RAG only
      gemma-4-26b-a4b-it     : Powerful — 15 RPM, Unlimited, 1500 RPD <- too slow
    """
    # RAG needs better reasoning for citing sources
    if has_rag_docs:
        return "gemini-2.5-flash"

    # Fast by default — gemini-3.1-flash-lite is the quickest free model
    return "gemini-3.1-flash-lite"
