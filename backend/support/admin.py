from django.contrib import admin
from .models import AgentProfile, Customer, Ticket, TicketMessage, KnowledgeBaseArticle, ActivityLog

@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin): list_display=('user','role','display_name')
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin): list_display=('name','email','company','created_at'); search_fields=('name','email','phone','company')
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin): list_display=('ticket_number','subject','customer','status','priority','assigned_to','updated_at'); list_filter=('status','priority','source'); search_fields=('ticket_number','subject','customer__name')
@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin): list_display=('ticket','author_name','is_internal','created_at')
@admin.register(KnowledgeBaseArticle)
class KnowledgeBaseArticleAdmin(admin.ModelAdmin): list_display=('title','category','is_published','updated_at')
@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin): list_display=('action','entity_type','summary','actor','created_at')
