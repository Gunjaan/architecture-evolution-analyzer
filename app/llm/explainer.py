import os
from huggingface_hub import InferenceClient

class HuggingFaceExplainer:
    def __init__(self):
        token = os.getenv("HF_TOKEN")
        if not token:
            raise RuntimeError("HF_TOKEN is not configured.")
        self.model = os.getenv("HF_MODEL", "Qwen/Qwen3-8B")
        self.client = InferenceClient(provider="auto", api_key=token)

    def explain(self, evidence):
        prompt = f"""You are a senior software architect reviewing software evolution.

Return a concise architectural report:

## Strongest Architectural Changes
Identify the 3 most important changes.

## Top Hotspots
Identify the 5 most concerning files.

## Evidence
Use concrete numbers from the supplied data.

## Hypotheses
Explain plausible architectural causes.
Clearly label these as hypotheses.

## Recommended Investigation
Give 3 concrete things an engineer should inspect next.

Keep the response under 300 words.
Do not repeat the entire evidence.

Evidence:
{evidence}
"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Analyze software architecture evolution from evidence."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=900,
            temperature=0.1,
        )
        return response.choices[0].message.content or ""
