from LLM.llm import GroqLLM


def main():
    llm = GroqLLM()

    prompt = """
You are an AI assistant for an Ayurveda regulatory guidance system.

Explain in 3-4 sentences:
What is the purpose of regulatory compliance for an Ayurvedic product?
"""

    response = llm.generate(prompt)

    print("\n" + "=" * 80)
    print("GROQ LLM TEST")
    print("=" * 80)

    print("\nResponse:")
    print(response)

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()