from .llm import GroqLLM


class AnswerGenerator:

    def __init__(self):
        self.llm = GroqLLM()

    # ============================================================
    # REGULATORY ANSWER
    # ============================================================

    def generate_regulatory_answer(
        self,
        product_context,
        regulatory_result
    ):

        llm_evidence = []

        # Collect only a small number of relevant chunks.
        # Raw evidence stays internal and is NOT returned to frontend.

        checks = regulatory_result.get("checks", {})

        for category, check in checks.items():

            evidence = check.get("evidence", [])

            for item in evidence[:1]:

                text = item.get("text", "").strip()

                if not text:
                    continue

                llm_evidence.append({
                    "category": category,
                    "document": item.get("document"),
                    "section": item.get("section"),
                    "page": item.get("page"),
                    "text": text[:1000]
                })

        # Add only a couple of general evidence chunks.
        for item in regulatory_result.get(
            "general_evidence", []
        )[:2]:

            text = item.get("text", "").strip()

            if not text:
                continue

            llm_evidence.append({
                "category": "general",
                "document": item.get("document"),
                "section": item.get("section"),
                "page": item.get("page"),
                "text": text[:1000]
            })

        prompt = f"""
You are an Ayurveda regulatory guidance assistant.

Explain the regulatory assessment of the product using ONLY
the evidence provided.

PRODUCT:
{product_context}

REGULATORY EVIDENCE:
{llm_evidence}

Instructions:

1. Explain the main regulatory areas requiring attention.
2. Discuss licensing, labelling, safety, GMP, claims and
   applicable regulations ONLY when supported by the evidence.
3. Do not invent laws, rules, sections, authorities or requirements.
4. Do not make a definitive legal conclusion.
5. If evidence is insufficient, clearly say so.
6. Do not reproduce the retrieved evidence verbatim.
7. Keep the answer concise and practical.
8. Do not mention internal RAG, chunks, scores or retrieval.
9. State that this is informational guidance and not legal advice.

Format the response as:

### Overall assessment

Brief explanation.

### Key areas

- Area: explanation
- Area: explanation

### Next step

Practical next step based only on the evidence.

### Disclaimer

This is informational guidance and not legal advice.
"""

        return self.llm.generate(prompt)

    # ============================================================
    # ABS ANSWER
    # ============================================================

    def generate_abs_answer(
        self,
        product_context,
        abs_result
    ):

        llm_evidence = []

        checks = abs_result.get("checks", {})

        for category, check in checks.items():

            evidence = check.get("evidence", [])

            for item in evidence[:1]:

                text = item.get("text", "").strip()

                if not text:
                    continue

                llm_evidence.append({
                    "category": category,
                    "document": item.get("document"),
                    "section": item.get("section"),
                    "page": item.get("page"),
                    "text": text[:1000]
                })

        for item in abs_result.get(
            "general_evidence", []
        )[:2]:

            text = item.get("text", "").strip()

            if not text:
                continue

            llm_evidence.append({
                "category": "general",
                "document": item.get("document"),
                "section": item.get("section"),
                "page": item.get("page"),
                "text": text[:1000]
            })

        prompt = f"""
You are an Ayurveda biodiversity and Access and Benefit Sharing
(ABS) guidance assistant.

Explain the ABS assessment using ONLY the evidence provided.

PRODUCT:
{product_context}

ABS EVIDENCE:
{llm_evidence}

Instructions:

1. Explain the ABS-related concerns relevant to this product.
2. Discuss biological resources, traditional knowledge, access,
   benefit sharing and commercial use ONLY when supported by evidence.
3. Discuss intellectual property only if directly supported by
   the retrieved ABS evidence.
4. Do not invent laws, rules, sections, authorities or obligations.
5. Do not make a definitive legal conclusion.
6. If evidence is insufficient, clearly say so.
7. Do not reproduce retrieved evidence verbatim.
8. Keep the answer concise and practical.
9. Do not mention internal RAG, chunks, scores or retrieval.
10. State that this is informational guidance and not legal advice.

Format the response as:

### Overall assessment

Brief explanation.

### Key ABS considerations

- Area: explanation
- Area: explanation

### Next step

Practical next step based only on the evidence.

### Disclaimer

This is informational guidance and not legal advice.
"""

        return self.llm.generate(prompt)

    # ============================================================
    # ROADMAP ANSWER
    # ============================================================

    def generate_roadmap_answer(
        self,
        action,
        evidence
    ):

        prompt = f"""
You are an Ayurveda IP and regulatory action-plan assistant.

Generate practical next steps for the following action pathway.

ACTION:
{action["action"]}

ACTION TYPE:
{action["action_type"]}

PROCEDURAL EVIDENCE:
{evidence}

Rules:

1. Use ONLY the provided evidence.
2. Do not invent legal requirements, procedures, fees, timelines,
   forms, authorities or documents.
3. Do not claim that an action is legally mandatory unless the
   evidence explicitly supports that conclusion.
4. Present the action as a recommended pathway or next step.
5. Keep the answer concise and practical.
6. If the evidence is insufficient, say so.
7. Use Markdown formatting.
8. Give 3-5 numbered practical steps.
9. Mention when professional/legal review may be appropriate.
10. Do not reproduce large portions of the evidence.
11. State that this is informational guidance and not legal advice.

Format:

### What to do

1. ...
2. ...
3. ...

### Important

...

### Disclaimer

This is informational guidance and not legal advice.
"""

        return self.llm.generate(prompt)