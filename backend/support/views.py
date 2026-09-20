from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Customer, Ticket, TicketMessage, KnowledgeBaseArticle, ActivityLog
from .permissions import IsSupervisorOrAdmin, IsAdmin
from .serializers import (
    CustomTokenObtainPairSerializer, UserSerializer, CustomerSerializer,
    TicketSerializer, TicketDetailSerializer, TicketMessageSerializer,
    KnowledgeBaseArticleSerializer, ActivityLogSerializer, TeamMemberSerializer,
)
from .services import log_activity, suggest_reply, send_ticket_reply_email

class HealthView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({'status': 'ok', 'service': 'supportdesk-api'})

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)

class DashboardStatsView(APIView):
    def get(self, request):
        tickets = Ticket.objects.all()
        total = tickets.count()
        by_status = {key: tickets.filter(status=key).count() for key, _ in Ticket.STATUS}
        by_priority = {key: tickets.filter(priority=key).count() for key, _ in Ticket.PRIORITY}
        my_open = tickets.filter(assigned_to=request.user).exclude(status__in=['resolved','closed']).count()
        customers = Customer.objects.count()
        recent = TicketSerializer(tickets.order_by('-updated_at')[:5], many=True).data
        return Response({
            'total_tickets': total,
            'open_tickets': by_status['open'],
            'pending_tickets': by_status['pending'],
            'resolved_tickets': by_status['resolved'],
            'my_open_tickets': my_open,
            'customers': customers,
            'by_status': by_status,
            'by_priority': by_priority,
            'recent_tickets': recent,
        })

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name','email','phone','company']
    ordering_fields = ['name','created_at','updated_at']

    def perform_create(self, serializer):
        obj = serializer.save()
        log_activity(self.request.user, 'customer.created', obj, f'Created customer {obj.name}')

    def perform_update(self, serializer):
        obj = serializer.save()
        log_activity(self.request.user, 'customer.updated', obj, f'Updated customer {obj.name}')

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['ticket_number','subject','description','customer__name','customer__email']
    ordering_fields = ['created_at','updated_at','priority','status']

    def get_serializer_class(self):
        return TicketDetailSerializer if self.action == 'retrieve' else TicketSerializer

    def get_queryset(self):
        qs = Ticket.objects.all()
        for key in ('status','priority','source'):
            value = self.request.query_params.get(key)
            if value:
                qs = qs.filter(**{key: value})
        assigned = self.request.query_params.get('assigned')
        if assigned == 'me':
            qs = qs.filter(assigned_to=self.request.user)
        elif assigned == 'unassigned':
            qs = qs.filter(assigned_to__isnull=True)
        return qs

    def perform_create(self, serializer):
        obj = serializer.save()
        log_activity(self.request.user, 'ticket.created', obj, f'Created {obj.ticket_number}')

    def perform_update(self, serializer):
        obj = serializer.save()
        log_activity(self.request.user, 'ticket.updated', obj, f'Updated {obj.ticket_number}')

    @action(detail=True, methods=['post'], url_path='messages')
    def add_message(self, request, pk=None):
        ticket = self.get_object()
        body = (request.data.get('body') or '').strip()
        if not body:
            return Response({'detail': 'Message body is required.'}, status=400)

        internal = bool(request.data.get('is_internal', False))
        msg = TicketMessage.objects.create(
            ticket=ticket,
            author=request.user,
            author_name=request.user.get_full_name() or request.user.username,
            body=body,
            is_internal=internal,
            is_ai_generated=bool(request.data.get('is_ai_generated', False)),
        )

        if not internal and not ticket.first_response_at:
            ticket.first_response_at = timezone.now()
            ticket.save(update_fields=['first_response_at','updated_at'])
        else:
            ticket.save(update_fields=['updated_at'])

        email_result = {'sent': False, 'reason': 'internal_note'}
        if not internal:
            try:
                email_result = send_ticket_reply_email(ticket, body)
            except Exception as exc:
                email_result = {'sent': False, 'reason': 'smtp_error', 'error': str(exc)[:180]}

        log_activity(
            request.user,
            'ticket.message',
            ticket,
            f'Added {"internal note" if internal else "reply"} to {ticket.ticket_number}',
            {'email': email_result},
        )

        payload = TicketMessageSerializer(msg).data
        payload['email'] = email_result
        return Response(payload, status=201)

    @action(detail=True, methods=['post'], url_path='ai-suggest')
    def ai_suggest(self, request, pk=None):
        ticket = self.get_object()
        terms = [x for x in [ticket.category, *ticket.tags] if x]
        qs = KnowledgeBaseArticle.objects.filter(is_published=True)

        if terms:
            query = Q()
            for term in terms:
                query |= (
                    Q(title__icontains=term)
                    | Q(content__icontains=term)
                    | Q(category__icontains=term)
                )
            matched = list(qs.filter(query)[:5])
        else:
            matched = list(qs[:5])

        result = suggest_reply(ticket, matched)
        log_activity(
            request.user,
            'ticket.ai_suggested',
            ticket,
            f'Generated AI reply suggestion for {ticket.ticket_number}',
            {'provider': result.get('provider')},
        )
        return Response(result)

    @action(detail=True, methods=['post'], url_path='assign-to-me')
    def assign_to_me(self, request, pk=None):
        ticket = self.get_object()
        ticket.assigned_to = request.user
        ticket.save(update_fields=['assigned_to','updated_at'])
        log_activity(request.user, 'ticket.assigned', ticket, f'Assigned {ticket.ticket_number} to self')
        return Response(TicketSerializer(ticket).data)

    @action(detail=True, methods=['post'], url_path='close')
    def close_ticket(self, request, pk=None):
        ticket = self.get_object()
        ticket.status = 'closed'
        ticket.save()
        log_activity(request.user, 'ticket.closed', ticket, f'Closed {ticket.ticket_number}')
        return Response(TicketSerializer(ticket).data)

class KnowledgeViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeBaseArticle.objects.all()
    serializer_class = KnowledgeBaseArticleSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title','content','category']
    ordering_fields = ['title','created_at','updated_at']

    def perform_create(self, serializer):
        obj = serializer.save()
        log_activity(self.request.user, 'knowledge.created', obj, f'Created knowledge article {obj.title}')

    def perform_update(self, serializer):
        obj = serializer.save()
        log_activity(self.request.user, 'knowledge.updated', obj, f'Updated knowledge article {obj.title}')

class ActivityListView(APIView):
    def get(self, request):
        qs = ActivityLog.objects.all()[:100]
        return Response(ActivityLogSerializer(qs, many=True).data)

class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('username')
    serializer_class = TeamMemberSerializer
    lookup_field = 'username'
    permission_classes = [IsAuthenticated, IsSupervisorOrAdmin]

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsAdmin], url_path='role')
    def set_role(self, request, username=None):
        user = self.get_object()
        role = request.data.get('role')
        if role not in {'admin','supervisor','agent'}:
            return Response({'detail': 'Invalid role.'}, status=400)
        profile = user.agent_profile
        profile.role = role
        profile.save(update_fields=['role'])
        log_activity(request.user, 'team.role_changed', profile, f'Changed {user.username} role to {role}')
        return Response(TeamMemberSerializer(user).data)
