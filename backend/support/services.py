import os
import httpx
from .models import ActivityLog

def log_activity(actor, action, entity, summary, metadata=None):
    ActivityLog.objects.create(
        actor=actor if getattr(actor, 'is_authenticated', False) else None,
        action=action,
        entity_type=entity.__class__.__name__,
        entity_id=str(getattr(entity, 'pk', '')),
        summary=summary,
        metadata=metadata or {},
    )

def suggest_reply(ticket, articles):
    key = os.getenv('AI_API_KEY', '').strip()
    base = os.getenv('AI_BASE_URL', 'https://codecraftapi.com/v1').strip().rstrip('/')
    model = os.getenv('AI_MODEL', 'gpt-5.6-sol').strip()

    recent = list(ticket.messages.all().order_by('-created_at')[:8])
    conversation = '\n'.join(
        f"{m.author_name or (m.author.username if m.author else 'Customer')}: {m.body}"
        for m in reversed(recent)
    )
    kb = '\n\n'.join(f"{a.title}: {a.content[:1500]}" for a in articles[:5])

    system = (
        "You are a customer support writing assistant. "
        "Draft a concise, empathetic and practical reply. "
        "Do not invent refunds, timelines, policies, account actions, or facts. "
        "Return only the reply text."
    )
    prompt = f"""Ticket: {ticket.ticket_number}
Subject: {ticket.subject}
Description: {ticket.description}

Recent conversation:
{conversation or 'No messages yet.'}

Knowledge base:
{kb or 'No matching knowledge-base content.'}"""

    if not key:
        return {
            'reply': (
                f"Hi {ticket.customer.name},\n\n"
                f"Thanks for reaching out about \"{ticket.subject}\". "
                "I’ve reviewed the details you shared. We’re looking into this and will help "
                "with the next appropriate step. If you have any additional information or a "
                "screenshot that could help us reproduce the issue, please send it here.\n\n"
                "Best regards,\nSupport Team"
            ),
            'provider': 'fallback',
            'model': None,
        }

    try:
        response = httpx.post(
            f"{base}/chat/completions",
            headers={
                'Authorization': f'Bearer {key}',
                'Content-Type': 'application/json',
            },
            json={
                'model': model,
                'messages': [
                    {'role': 'system', 'content': system},
                    {'role': 'user', 'content': prompt},
                ],
                'temperature': 0.3,
                'max_tokens': 700,
            },
            timeout=60.0,
        )
        response.raise_for_status()
        payload = response.json()
        text = (
            payload.get('choices', [{}])[0]
            .get('message', {})
            .get('content', '')
            .strip()
        )
        if not text:
            raise ValueError('Provider response contained no reply text')
        return {
            'reply': text,
            'provider': 'codecraft',
            'model': payload.get('model') or model,
            'usage': payload.get('usage', {}),
        }
    except Exception as exc:
        return {
            'reply': 'AI suggestion is temporarily unavailable. Please write a manual reply.',
            'provider': 'error',
            'model': model,
            'error': str(exc)[:180],
        }
