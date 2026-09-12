from chatbot import IPShaktiChatbot


def main():

    chatbot = IPShaktiChatbot()

    product_context = {
        "product_name": "Ashwagandha Herbal Formulation",
        "product_type": "ayurvedic medicine",
        "classification": "proprietary formulation",
        "ingredients": ["Ashwagandha", "Brahmi"],
        "intended_use": "General wellness and stress support",
        "traditional_knowledge": "yes",
        "uses_biological_resources": "yes",
        "biological_resources": ["Ashwagandha", "Brahmi"],
        "jurisdiction": "India"
    }

    legal_report = {
        "ip_assessment": {
            "relevant_ip_domains": [
                "patent",
                "trademark",
                "traditional knowledge",
                "biological resources"
            ]
        },
        "regulatory_assessment": {
            "overall_status": "Review"
        },
        "tkdl_assessment": {
            "overall_status": "TKDL review required"
        },
        "abs_assessment": {
            "overall_status": "ABS review required"
        }
    }

    roadmap = {
        "status": "Action plan generated",
        "actions": [
            {
                "action": "Patent filing",
                "action_type": "patent_filing"
            },
            {
                "action": "ABS compliance",
                "action_type": "abs_compliance"
            }
        ]
    }

    chat_history = []

    question = "Why is ABS compliance relevant to my product?"

    print("\n" + "=" * 70)
    print("USER QUESTION")
    print("=" * 70)
    print(question)

    result = chatbot.answer(
        question=question,
        product_context=product_context,
        legal_report=legal_report,
        roadmap=roadmap,
        chat_history=chat_history
    )

    print("\n" + "=" * 70)
    print("CHATBOT ANSWER")
    print("=" * 70)
    print(result["answer"])

    print("\n" + "=" * 70)
    print("SOURCES")
    print("=" * 70)

    for source in result["sources"]:
        print(source)


if __name__ == "__main__":
    main()