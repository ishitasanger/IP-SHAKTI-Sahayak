from Regulatory.regulatory_fitcheck import (
    regulatory_fitcheck
)


product_context = {
    "product_name": "Herbal formulation",

    "ingredients": [
        "Ashwagandha",
        "Guduchi"
    ],

    "claims": [
        "supports stress relief",
        "improves general wellness"
    ],

    "classification": "proprietary formulation",

    "intended_use": "medicinal",

    "jurisdiction": "India"
}


result = regulatory_fitcheck(
    product_context
)


print("\n")
print("=" * 80)
print("REGULATORY FITCHECK")
print("=" * 80)

print("\nOverall Status:")
print(result["overall_status"])


for category, check in result["checks"].items():

    print("\n" + "-" * 80)

    print(
        f"{category.upper()}: "
        f"{check['status']}"
    )

    print("\nEvidence:")

    for evidence in check["evidence"]:

        print(
            f"\nDocument: "
            f"{evidence['document']}"
        )

        print(
            f"Section: "
            f"{evidence['section']}"
        )

        print(
            f"Page: "
            f"{evidence['page']}"
        )

        print(
            f"Source File: "
            f"{evidence['source_file']}"
        )

        print(
            f"Source URL: "
            f"{evidence['source_url']}"
        )

        print(
            f"Text: "
            f"{evidence['text'][:500]}"
        )


print("\n")
print("=" * 80)
print("DISCLAIMER")
print("=" * 80)

print(result["disclaimer"])
print("\n")
print("=" * 80)
print("LLM REGULATORY EXPLANATION")
print("=" * 80)

print(result["llm_answer"])