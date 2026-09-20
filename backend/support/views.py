from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Customer, Ticket, TicketMessage, KnowledgeBaseArticle, ActivityLog
from .permissions import (
    IsSupervisorOrAdmin,
    IsAdmin,
    user_role,
    customer_for_user,
)
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    CustomerRegistrationSerializer,
    CustomerSerializer,
    CustomerSelfSerializer,
    TicketSerializer,
    CustomerTicketCreateSerializer,
    TicketDetailSerializer,
    TicketMessageSerializer,
    KnowledgeBaseArticleSerializer,
    ActivityLogSerializer,
    TeamMemberSerializer,
    TeamMemberCreateSerializer,
)
from .services import log_activity, suggest_reply, send_ticket_reply_email


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'status': 'ok', 'service': 'supportdesk-api'})


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomerRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        log_activity(user, 'customer.registered', user.agent_profile.customer, 'Customer account created')
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class CustomerProfileView(APIView):
    def get_customer(self, request):
        customer = customer_for_user(request.user)
        if not customer:
            raise PermissionDenied('Customer account required.')
        return customer

    def get(self, request):
        return Response(CustomerSelfSerializer(self.get_customer(request)).data)

    def patch(self, request):
        customer = self.get_customer(request)
        serializer = CustomerSelfSerializer(customer, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        customer = serializer.save()
        log_activity(request.user, 'customer.profile_updated', customer, 'Customer updated portal profile')
        return Response(serializer.data)


class DashboardStatsView(APIView):
    def get(self, request):
        role = user_role(request.user)

        if role == 'customer':
            customer = customer_for_user(request.user)
            tickets = Ticket.objects.filter(customer=customer) if customer else Ticket.objects.none()
            customer_count = 1 if customer else 0
        elif role == 'agent':
            tickets = Ticket.objects.filter(
                Q(assigned_to=request.user) | Q(assigned_to__isnull=True)
            )
            customer_count = Customer.objects.count()
        else:
            tickets = Ticket.objects.all()
            customer_count = Customer.objects.count()

        total = tickets.count()
        by_status = {key: tickets.filter(status=key).count() for key, _ in Ticket.STATUS}
        by_priority = {key: tickets.filter(priority=key).count() for key, _ in Ticket.PRIORITY}
        my_open = (
            tickets.filter(assigned_to=request.user)
            .exclude(status__in=['resolved', 'closed'])
            .count()
            if role != 'customer'
            else tickets.exclude(status__in=['resolved', 'closed']).count()
        )
        recent = TicketSerializer(
            tickets.order_by('-updated_at')[:5],
            many=True,
            context={'request': request},
        ).data

        return Response({
            'role': role,
            'total_tickets': total,
            'open_tickets': by_status['open'],
            'pending_tickets': by_status['pending'],
            'resolved_tickets': by_status['resolved'],
            'my_open_tickets': my_open,
            'customers': customer_count,
            'by_status': by_status,
            'by_priority': by_priority,
            'recent_tickets': recent,
        })


class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'email', 'phone', 'company']
    ordering_fields = ['name', 'created_at', 'updated_at']

    def get_queryset(self):
        if user_role(self.request.user) == 'customer':
            customer = customer_for_user(self.request.user)
            return Customer.objects.filter(pk=customer.pk) if customer else Customer.objects.none()
        return Customer.objects.all()

    def get_permissions(self):
        if self.action in {'create', 'update', 'partial_update', 'destroy'}:
            return [IsSupervisorOrAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        obj = serializer.save()
        log_activity(self.request.user, 'customer.created', obj, f'Created customer {obj.name}')

    def perform_update(self, serializer):
        obj = serializer.save()
        log_activity(self.request.user, 'customer.updated', obj, f'Updated customer {obj.name}')

    def perform_destroy(self, instance):
        log_activity(self.request.user, 'customer.deleted', instance, f'Deleted customer {instance.name}')
        instance.delete()


class TicketViewSet(viewsets.ModelViewSet):
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['ticket_number', 'subject', 'description', 'customer__name', 'customer__email']
    ordering_fields = ['created_at', 'updated_at', 'priority', 'status']

    def get_queryset(self):
        role = user_role(self.request.user)
        qs = Ticket.objects.all()

        if role == 'customer':
            customer = customer_for_user(self.request.user)
            qs = qs.filter(customer=customer) if customer else Ticket.objects.none()
        elif role == 'agent':
            qs = qs.filter(Q(assigned_to=self.request.user) | Q(assigned_to__isnull=True))

        for key in ('status', 'priority', 'source'):
            value = self.request.query_params.get(key)
            if value:
                qs = qs.filter(**{key: value})

        assigned = self.request.query_params.get('assigned')
        if role != 'customer':
            if assigned == 'me':
                qs = qs.filter(assigned_to=self.request.user)
            elif assigned == 'unassigned':
                qs = qs.filter(assigned_to__isnull=True)

        return qs

    def get_serializer_class(self):
        role = user_role(self.request.user)
        if self.action == 'create' and role == 'customer':
            return CustomerTicketCreateSerializer
        if self.action == 'retrieve':
            return TicketDetailSerializer
        return TicketSerializer

    def perform_create(self, serializer):
        role = user_role(self.request.user)

        if role == 'customer':
            customer = customer_for_user(self.request.user)
            if not customer:
                raise PermissionDenied('Customer profile is not linked.')
            obj = serializer.save(
                customer=customer,
                status='open',
                priority='medium',
                source='web',
                assigned_to=None,
                tags=[],
            )
        else:
            if not serializer.validated_data.get('customer'):
                raise ValidationError({'customer_id': 'Customer is required.'})
            obj = serializer.save()

        log_activity(self.request.user, 'ticket.created', obj, f'Created {obj.ticket_number}')

    def update(self, request, *args, **kwargs):
        role = user_role(request.user)
        if role == 'customer':
            raise PermissionDenied('Customers cannot edit ticket properties.')

        if role == 'agent':
            allowed = {'status', 'priority', 'category', 'tags'}
            invalid = set(request.data.keys()) - allowed
            if invalid:
                raise PermissionDenied(
                    'Agents can update only status, priority, category and tags.'
                )

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if user_role(request.user) not in {'admin', 'supervisor'}:
            raise PermissionDenied('Only management can delete tickets.')
        ticket = self.get_object()
        log_activity(request.user, 'ticket.deleted', ticket, f'Deleted {ticket.ticket_number}')
        return super().destroy(request, *args, **kwargs)

    def perform_update(self, serializer):
        obj = serializer.save()
        log_activity(self.request.user, 'ticket.updated', obj, f'Updated {obj.ticket_number}')

    @action(detail=True, methods=['post'], url_path='messages')
    def add_message(self, request, pk=None):
        ticket = self.get_object()
        role = user_role(request.user)
        body = (request.data.get('body') or '').strip()

        if not body:
            return Response({'detail': 'Message body is required.'}, status=400)

        internal = bool(request.data.get('is_internal', False))
        if role == 'customer' and internal:
            raise PermissionDenied('Customers cannot add internal notes.')

        if role == 'customer':
            customer = customer_for_user(request.user)
            author_name = customer.name if customer else request.user.get_full_name() or request.user.username
            ai_generated = False
        else:
            author_name = request.user.get_full_name() or request.user.username
            ai_generated = bool(request.data.get('is_ai_generated', False))

        msg = TicketMessage.objects.create(
            ticket=ticket,
            author=request.user,
            author_name=author_name,
            body=body,
            is_internal=internal,
            is_ai_generated=ai_generated,
        )

        if role == 'customer':
            if ticket.status in {'pending', 'resolved'}:
                ticket.status = 'open'
                ticket.resolved_at = None
            ticket.save(update_fields=['status', 'resolved_at', 'updated_at'])
        elif not internal and not ticket.first_response_at:
            ticket.first_response_at = timezone.now()
            ticket.save(update_fields=['first_response_at', 'updated_at'])
        else:
            ticket.save(update_fields=['updated_at'])

        email_result = {'sent': False, 'reason': 'not_applicable'}
        if role != 'customer' and not internal:
            try:
                email_result = send_ticket_reply_email(ticket, body)
            except Exception as exc:
                email_result = {
                    'sent': False,
                    'reason': 'smtp_error',
                    'error': str(exc)[:180],
                }

        log_activity(
            request.user,
            'ticket.message',
            ticket,
            f'Added {"internal note" if internal else "reply"} to {ticket.ticket_number}',
            {'email': email_result, 'role': role},
        )

        payload = TicketMessageSerializer(msg, context={'request': request}).data
        payload['email'] = email_result
        return Response(payload, status=201)

    @action(detail=True, methods=['post'], url_path='ai-suggest')
    def ai_suggest(self, request, pk=None):
        if user_role(request.user) == 'customer':
            raise PermissionDenied('AI reply suggestions are available to support staff only.')

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
            f'Generated reply suggestion for {ticket.ticket_number}',
            {'provider': result.get('provider')},
        )
        return Response(result)

    @action(detail=True, methods=['post'], url_path='assign-to-me')
    def assign_to_me(self, request, pk=None):
        if user_role(request.user) == 'customer':
            raise PermissionDenied('Customers cannot assign tickets.')

        ticket = self.get_object()
        ticket.assigned_to = request.user
        ticket.save(update_fields=['assigned_to', 'updated_at'])
        log_activity(
            request.user,
            'ticket.assigned',
            ticket,
            f'Assigned {ticket.ticket_number} to self',
        )
        return Response(TicketSerializer(ticket, context={'request': request}).data)

    @action(detail=True, methods=['post'], url_path='close')
    def close_ticket(self, request, pk=None):
        if user_role(request.user) == 'customer':
            raise PermissionDenied('Customers cannot close tickets.')

        ticket = self.get_object()
        ticket.status = 'closed'
        ticket.save()
        log_activity(request.user, 'ticket.closed', ticket, f'Closed {ticket.ticket_number}')
        return Response(TicketSerializer(ticket, context={'request': request}).data)


class KnowledgeViewSet(viewsets.ModelViewSet):
    serializer_class = KnowledgeBaseArticleSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'content', 'category']
    ordering_fields = ['title', 'created_at', 'updated_at']

    def get_queryset(self):
        qs = KnowledgeBaseArticle.objects.all()
        if user_role(self.request.user) == 'customer':
            qs = qs.filter(is_published=True)
        return qs

    def get_permissions(self):
        if self.action in {'create', 'update', 'partial_update', 'destroy'}:
            return [IsSupervisorOrAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        obj = serializer.save()
        log_activity(
            self.request.user,
            'knowledge.created',
            obj,
            f'Created knowledge article {obj.title}',
        )

    def perform_update(self, serializer):
        obj = serializer.save()
        log_activity(
            self.request.user,
            'knowledge.updated',
            obj,
            f'Updated knowledge article {obj.title}',
        )


class ActivityListView(APIView):
    permission_classes = [IsSupervisorOrAdmin]

    def get(self, request):
        qs = ActivityLog.objects.all()[:100]
        return Response(ActivityLogSerializer(qs, many=True).data)


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.exclude(agent_profile__role='customer').order_by('username')
    serializer_class = TeamMemberSerializer
    lookup_field = 'username'
    permission_classes = [IsAuthenticated, IsSupervisorOrAdmin]

    def create(self, request):
        if user_role(request.user) != 'admin':
            raise PermissionDenied('Only admins can create team members.')

        serializer = TeamMemberCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        log_activity(
            request.user,
            'team.created',
            user.agent_profile,
            f'Created {user.agent_profile.role} account {user.username}',
        )
        return Response(TeamMemberSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=['patch'],
        permission_classes=[IsAuthenticated, IsAdmin],
        url_path='role',
    )
    def set_role(self, request, username=None):
        user = self.get_object()
        role = request.data.get('role')

        if user == request.user:
            raise ValidationError({'role': 'You cannot change your own role.'})
        if role not in {'admin', 'supervisor', 'agent'}:
            return Response({'detail': 'Invalid role.'}, status=400)

        profile = user.agent_profile
        profile.role = role
        profile.save(update_fields=['role'])
        log_activity(
            request.user,
            'team.role_changed',
            profile,
            f'Changed {user.username} role to {role}',
        )
        return Response(TeamMemberSerializer(user).data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated, IsAdmin],
        url_path='deactivate',
    )
    def deactivate(self, request, username=None):
        user = self.get_object()
        if user == request.user:
            raise ValidationError({'detail': 'You cannot deactivate your own account.'})
        user.is_active = False
        user.save(update_fields=['is_active'])
        log_activity(request.user, 'team.deactivated', user.agent_profile, f'Deactivated {user.username}')
        return Response(TeamMemberSerializer(user).data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated, IsAdmin],
        url_path='activate',
    )
    def activate(self, request, username=None):
        user = self.get_object()
        user.is_active = True
        user.save(update_fields=['is_active'])
        log_activity(request.user, 'team.activated', user.agent_profile, f'Activated {user.username}')
        return Response(TeamMemberSerializer(user).data)
