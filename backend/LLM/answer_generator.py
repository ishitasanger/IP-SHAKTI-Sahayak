from .llm import GroqLLM


class AnswerGenerator:

    def __init__(self):
        self.llm = GroqLLM()

    def generate_regulatory_answer(self, product_context, regulatory_result):

        prompt = f"""
You are an Ayurveda regulatory guidance assistant.

Your task is to explain the regulatory assessment of an Ayurvedic
product using ONLY the evidence provided below.

PRODUCT CONTEXT:
{product_context}

REGULATORY EVIDENCE:
{regulatory_result}

Instructions:

1. Explain which regulatory areas require attention.
2. Explain licensing, labelling, safety, GMP, claims and applicable
   regulations using the retrieved evidence.
3. Do not invent laws, rules, sections or requirements.
4. Do not make a definitive legal conclusion.
5. If the evidence is insufficient, clearly say so.
6. Mention the relevant source documents where appropriate.
7. Keep the answer concise and practical.
8. State that this is informational guidance and not legal advice.

Give the answer in clear sections.
"""

        return self.llm.generate(prompt)