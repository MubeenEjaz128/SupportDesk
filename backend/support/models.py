import uuid
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class AgentProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('supervisor', 'Supervisor'),
        ('agent', 'Agent'),
        ('customer', 'Customer'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='agent')
    display_name = models.CharField(max_length=120, blank=True)
    customer = models.OneToOneField(
        'Customer',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='portal_profile',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name or self.user.username


class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=160)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    company = models.CharField(max_length=160, blank=True)
    notes = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Ticket(models.Model):
    STATUS = [
        ('open', 'Open'),
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    PRIORITY = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    SOURCE = [
        ('email', 'Email'),
        ('web', 'Web'),
        ('phone', 'Phone'),
        ('chat', 'Chat'),
        ('social', 'Social'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_number = models.CharField(max_length=32, unique=True, editable=False)
    subject = models.CharField(max_length=220)
    description = models.TextField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='tickets')
    assigned_to = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_tickets',
    )
    status = models.CharField(max_length=20, choices=STATUS, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY, default='medium')
    source = models.CharField(max_length=20, choices=SOURCE, default='web')
    category = models.CharField(max_length=100, blank=True)
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    first_response_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-updated_at']

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = f"TCK-{timezone.now():%y%m%d}-{uuid.uuid4().hex[:6].upper()}"
        if self.status in ('resolved', 'closed') and not self.resolved_at:
            self.resolved_at = timezone.now()
        if self.status in ('open', 'pending') and self.resolved_at:
            self.resolved_at = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.ticket_number} - {self.subject}'


class TicketMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='ticket_messages',
    )
    author_name = models.CharField(max_length=160, blank=True)
    body = models.TextField()
    is_internal = models.BooleanField(default=False)
    is_ai_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class KnowledgeBaseArticle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True)
    category = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    is_published = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']


class ActivityLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=120)
    entity_type = models.CharField(max_length=80)
    entity_id = models.CharField(max_length=120, blank=True)
    summary = models.CharField(max_length=280)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
