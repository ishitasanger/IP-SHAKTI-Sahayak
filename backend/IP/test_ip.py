import json

from Classification.classifier_wizard import (
    ProductContext
)

from IP.ip_checker import (
    IPChecker
)


def print_section(
    title: str
):

    print()

    print("=" * 70)

    print(title)

    print("=" * 70)

    print()


def main():

    print()

    print("#" * 70)

    print(
        "IP AND LEGAL RELEVANCE SCREENING"
    )

    print("#" * 70)

    # ============================================================
    # CREATE PRODUCT CONTEXT
    # ============================================================

    product = ProductContext(

        product_name=
            "Ashwagandha Wellness Capsules",

        product_description=(
            "A herbal capsule containing "
            "Ashwagandha and Guduchi intended "
            "to support general wellness and "
            "stress management."
        ),

        jurisdiction=
            "India",

        product_type=
            "ayurvedic medicine",

        classification=
            "proprietary formulation",

        form=
            "Capsule",

        ingredients=[

            "Ashwagandha",

            "Guduchi"
        ],

        ingredient_count=2,

        intended_use=(
            "Supports general wellness and "
            "stress management"
        ),

        claims=[

            "Supports stress relief",

            "Improves general wellness"
        ],

        innovation_description=(

            "A specific combination of "
            "Ashwagandha and Guduchi in "
            "a capsule formulation intended "
            "for stress management."
        ),

        traditional_knowledge=
            "yes",

        traditional_knowledge_source=(

            "Traditional Ayurvedic knowledge"
        ),

        uses_biological_resources=
            "yes",

        biological_resources=[

            "Ashwagandha",

            "Guduchi"
        ],

        manufacturing_location=
            "India",

        commercial_use=True
    )

    # ============================================================
    # DISPLAY PRODUCT
    # ============================================================

    print_section(
        "PRODUCT CONTEXT"
    )

    print(

        json.dumps(

            product.model_dump(),

            indent=4,

            default=str
        )
    )

    # ============================================================
    # INITIALIZE IP CHECKER
    # ============================================================

    print_section(
        "INITIALIZING RAG-POWERED IP CHECKER"
    )

    ip_checker = IPChecker()

    print(
        "IP Checker initialized successfully."
    )

    # ============================================================
    # RUN SCREENING
    # ============================================================

    print_section(
        "RUNNING IP AND LEGAL SCREENING"
    )

    result = ip_checker.check_ip(

        product=product,

        top_k=3
    )

    result_dict = result.to_dict()

    # ============================================================
    # COMPLETE RESULT
    # ============================================================

    print_section(
        "COMPLETE SCREENING RESULT"
    )

    print(

        json.dumps(

            result_dict,

            indent=4,

            default=str
        )
    )

    # ============================================================
    # RELEVANT IP DOMAINS
    # ============================================================

    print_section(
        "RELEVANT IP DOMAINS"
    )

    for domain in result.relevant_ip_domains:

        print(
            f"- {domain}"
        )

    # ============================================================
    # SEARCH PLAN
    # ============================================================

    print_section(
        "RAG SEARCH PLAN"
    )

    for index, query in enumerate(

        result.search_queries,

        start=1
    ):

        print(
            f"{index}. "
            f"Query type: "
            f"{query['query_type']}"
        )

        print(
            f"   RAG domain: "
            f"{query['rag_domain']}"
        )

        print(
            f"   Query: "
            f"{query['query_text']}"
        )

        print()

    # ============================================================
    # LEGAL EVIDENCE
    # ============================================================

    print_section(
        "RETRIEVED RAG LEGAL EVIDENCE"
    )

    if not result.legal_evidence:

        print(
            "No legal evidence was retrieved."
        )

    else:

        for index, evidence in enumerate(

            result.legal_evidence,

            start=1
        ):

            print(
                "-" * 70
            )

            print(
                f"EVIDENCE {index}"
            )

            print(
                "-" * 70
            )

            print(
                "Query type:"
            )

            print(
                evidence.get(
                    "query_type"
                )
            )

            print()

            print(
                "RAG domain:"
            )

            print(
                evidence.get(
                    "domain"
                )
            )

            print()

            print(
                "Source:"
            )

            print(
                evidence.get(
                    "source"
                )
            )

            print()

            print(
                "Page:"
            )

            print(
                evidence.get(
                    "page"
                )
            )

            print()

            print(
                "Score:"
            )

            print(
                evidence.get(
                    "score"
                )
            )

            print()

            print(
                "Retrieved text:"
            )

            print(
                evidence.get(
                    "text"
                )
            )

            print()

    # ============================================================
    # LEGAL CONSIDERATIONS
    # ============================================================

    print_section(
        "LEGAL CONSIDERATIONS"
    )

    for index, consideration in enumerate(

        result.legal_considerations,

        start=1
    ):

        print(
            f"{index}. {consideration}"
        )

        print()

    # ============================================================
    # SCREENING STATUS
    # ============================================================

    print_section(
        "SCREENING STATUS"
    )

    print(
        result.screening_status
    )

    # ============================================================
    # SUMMARY
    # ============================================================

    print_section(
        "SUMMARY"
    )

    print(
        result.summary
    )

    # ============================================================
    # DISCLAIMER
    # ============================================================

    print_section(
        "DISCLAIMER"
    )

    print(
        result.disclaimer
    )

    print()

    print("#" * 70)

    print(
        "ALL IP AND RAG TESTS COMPLETED"
    )

    print("#" * 70)

    print()


if __name__ == "__main__":

    main()
