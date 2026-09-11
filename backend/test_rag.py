from backend.rag.rag_engine import RAGEngine


rag = RAGEngine()


context = {
    "product_name": "Herbal formulation",
    "ingredients": [
        "Ashwagandha",
        "Guduchi"
    ],
    "claims": [
        "supports stress relief",
        "improves general wellness"
    ],
    "classification": "proprietary formulation"
}


results = rag.search(
    context=context,
    filters={"domain": "ip"},
    top_k=5
)


for i, result in enumerate(results, start=1):

    print("\n" + "=" * 80)
    print(f"RESULT {i}")
    print("=" * 80)

    print(f"Document: {result.document}")
    print(f"Page: {result.page}")
    print(f"Score: {result.score}")

    print("\nDomain:")
    print(result.metadata.get("domain"))

    print("\nMetadata:")
    print(result.metadata)

    print("\nText:")
    print(result.text)