import os
import httpx
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Check the configured AI provider without exposing secrets."

    def handle(self, *args, **kwargs):
        key = os.getenv("AI_API_KEY", "").strip()
        base = os.getenv("AI_BASE_URL", "").strip().rstrip("/")
        model = os.getenv("AI_MODEL", "").strip()
        if not key or not base:
            self.stdout.write("AI provider check skipped: AI_API_KEY or AI_BASE_URL missing.")
            return

        headers = {"Authorization": f"Bearer {key}", "Accept": "application/json"}
        try:
            response = httpx.get(f"{base}/models", headers=headers, timeout=20.0)
            if response.status_code != 200:
                self.stderr.write(
                    f"AI provider model check failed: HTTP {response.status_code}."
                )
                return

            data = response.json()
            models = data.get("data", [])
            ids = [m.get("id") for m in models if m.get("id")]
            sample = ", ".join(ids[:5])
            self.stdout.write(
                self.style.SUCCESS(
                    f"AI provider OK: {len(ids)} models available"
                    + (f" | sample: {sample}" if sample else "")
                )
            )

            if not model:
                self.stdout.write("Inference check skipped: AI_MODEL not set.")
                return

            if model not in ids:
                self.stderr.write(f"Inference check skipped: configured model '{model}' is not listed.")
                return

            chat = httpx.post(
                f"{base}/chat/completions",
                headers={**headers, "Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": [
                        {"role": "user", "content": "Reply with exactly: OK"}
                    ],
                    "max_tokens": 8,
                    "temperature": 0,
                },
                timeout=45.0,
            )
            if chat.status_code != 200:
                self.stderr.write(f"AI inference check failed: HTTP {chat.status_code}.")
                return

            payload = chat.json()
            text = (
                payload.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
            usage = payload.get("usage", {})
            self.stdout.write(
                self.style.SUCCESS(
                    f"AI inference OK: model={model} | response={text[:40]!r} "
                    f"| total_tokens={usage.get('total_tokens', 'n/a')}"
                )
            )
        except Exception as exc:
            self.stderr.write(f"AI provider check error: {type(exc).__name__}: {str(exc)[:180]}")
