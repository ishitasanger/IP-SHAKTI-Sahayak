from rag.rag_engine import RAGEngine


def main():

    rag = RAGEngine()

    query = input(
        "Enter your query: "
    )

    results = rag.search(
        query=query,
        top_k=5
    )

    print("\nRetrieved Evidence:\n")

    for index, result in enumerate(
        results,
        start=1
    ):

        print(
            f"\n--- Result {index} ---"
        )

        print(
            f"Document: {result.document}"
        )

        print(
            f"Section: {result.section}"
        )

        print(
            f"Page: {result.page}"
        )

        print(
            f"Source: {result.source_file}"
        )

        print(
            f"Score: {result.score:.4f}"
        )

        print(
            f"\n{result.text}"
        )


if __name__ == "__main__":
    main()