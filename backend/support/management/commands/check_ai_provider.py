import os
import httpx
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Check the configured AI provider without exposing secrets."

    def handle(self, *args, **kwargs):
        key = os.getenv("AI_API_KEY", "").strip()
        base = os.getenv("AI_BASE_URL", "").strip().rstrip("/")
        if not key or not base:
            self.stdout.write("AI provider check skipped: AI_API_KEY or AI_BASE_URL missing.")
            return

        try:
            response = httpx.get(
                f"{base}/models",
                headers={"Authorization": f"Bearer {key}", "Accept": "application/json"},
                timeout=20.0,
            )
            if response.status_code != 200:
                self.stderr.write(
                    f"AI provider check failed: HTTP {response.status_code}. "
                    "Key or provider configuration may be invalid."
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
        except Exception as exc:
            self.stderr.write(f"AI provider check error: {type(exc).__name__}: {str(exc)[:180]}")
