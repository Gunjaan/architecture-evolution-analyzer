import os
from time import sleep
from typing import cast

from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError
from huggingface_hub.inference._providers import PROVIDER_OR_POLICY_T
from requests import RequestException

from app.core.exceptions import LLMUnavailableError

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class HuggingFaceExplainer:
    def __init__(self) -> None:
        token = os.getenv("HF_TOKEN")
        if not token:
            raise RuntimeError("HF_TOKEN is not configured.")
        self.model = os.getenv("HF_MODEL") or None
        self.provider = os.getenv("HF_PROVIDER", "hf-inference")
        self.max_retries = int(os.getenv("HF_MAX_RETRIES", "2"))
        self.client = InferenceClient(
            provider=cast(PROVIDER_OR_POLICY_T, self.provider),
            api_key=token,
            timeout=60,
        )

    def explain(self, evidence: str) -> str:
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
        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.chat_completion(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Analyze software architecture evolution from evidence."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=900,
                    temperature=0.1,
                )
                return response.choices[0].message.content or ""
            except HfHubHTTPError as exc:
                status_code = exc.response.status_code if exc.response else None
                if status_code not in RETRYABLE_STATUS_CODES:
                    raise LLMUnavailableError(
                        "The configured Hugging Face provider rejected the request."
                    ) from exc
            except RequestException as exc:
                if attempt == self.max_retries:
                    raise LLMUnavailableError(
                        "The Hugging Face provider could not be reached."
                    ) from exc

            if attempt < self.max_retries:
                sleep(2**attempt)

        raise LLMUnavailableError(
            "The Hugging Face provider is temporarily unavailable after retrying."
        )
