from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from support.models import Customer, Ticket, TicketMessage, KnowledgeBaseArticle
class Command(BaseCommand):
    help='Seed safe demo records.'
    def handle(self,*args,**kwargs):
        agent,_=User.objects.get_or_create(username='demo-agent',defaults={'email':'agent@example.com','first_name':'Demo','last_name':'Agent'})
        agent.set_password('DemoPass123!'); agent.save()
        customer,_=Customer.objects.get_or_create(email='sarah@example.com',defaults={'name':'Sarah Khan','company':'Northstar Labs','phone':'+1 555 0100','tags':['priority']})
        if not Ticket.objects.filter(customer=customer,subject='Unable to access billing portal').exists():
            t=Ticket.objects.create(subject='Unable to access billing portal',description='The billing portal keeps returning an access error after login.',customer=customer,assigned_to=agent,priority='high',source='email',category='Billing',tags=['billing','login'])
            TicketMessage.objects.create(ticket=t,author_name=customer.name,body='I have tried two browsers and still see the same access error.')
        KnowledgeBaseArticle.objects.get_or_create(title='Billing portal access troubleshooting',defaults={'slug':'billing-portal-access-troubleshooting','category':'Billing','content':'Ask the customer to confirm the account email, sign out of all sessions, clear cookies for the portal, and retry. Escalate if the account is locked. Never promise an unlock time.','created_by':agent})
        self.stdout.write(self.style.SUCCESS('Demo data ready.'))
