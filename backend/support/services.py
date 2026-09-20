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

def _extract_output(data):
    chunks = []
    for item in data.get('output', []):
        for content in item.get('content', []):
            if content.get('type') == 'output_text' and content.get('text'):
                chunks.append(content['text'])
    return '\n'.join(chunks).strip()

def suggest_reply(ticket, articles):
    key = os.getenv('OPENAI_API_KEY', '').strip()
    model = os.getenv('OPENAI_MODEL', 'gpt-5.6-luna')
    recent = list(ticket.messages.all().order_by('-created_at')[:8])
    conversation = '\n'.join(f"{m.author_name or (m.author.username if m.author else 'Customer')}: {m.body}" for m in reversed(recent))
    kb = '\n\n'.join(f"{a.title}: {a.content[:1500]}" for a in articles[:5])
    prompt = f"""Draft a helpful customer support reply for this ticket.
Ticket: {ticket.ticket_number}\nSubject: {ticket.subject}\nDescription: {ticket.description}
Recent conversation:\n{conversation or 'No messages yet.'}
Knowledge base:\n{kb or 'No matching knowledge-base content.'}
Rules: be concise, empathetic, practical, do not invent refunds, timelines, policies, or facts. Return only the reply text."""
    if not key:
        return {
            'reply': f"Hi {ticket.customer.name},\n\nThanks for reaching out about \"{ticket.subject}\". I’ve reviewed the details you shared. We’re looking into this and will help you with the next appropriate step. If there’s any additional information or a screenshot that could help us reproduce the issue, please send it here.\n\nBest regards,\nSupport Team",
            'provider': 'fallback', 'model': None,
        }
    try:
        response = httpx.post(
            'https://api.openai.com/v1/responses',
            headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
            json={'model': model, 'input': prompt, 'max_output_tokens': 500},
            timeout=45.0,
        )
        response.raise_for_status()
        text = _extract_output(response.json())
        if not text: raise ValueError('AI response contained no text')
        return {'reply': text, 'provider': 'openai', 'model': model}
    except Exception as exc:
        return {'reply': 'AI suggestion is temporarily unavailable. Please write a manual reply.', 'provider': 'error', 'model': model, 'error': str(exc)[:180]}
