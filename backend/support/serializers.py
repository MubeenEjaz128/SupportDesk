from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.utils.text import slugify
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Customer, Ticket, TicketMessage, KnowledgeBaseArticle, ActivityLog
from .permissions import user_role, customer_for_user


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    customer_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'is_active', 'role', 'display_name', 'customer_id',
        ]

    def get_role(self, obj):
        return user_role(obj)

    def get_display_name(self, obj):
        try:
            return obj.agent_profile.display_name or obj.get_full_name() or obj.username
        except Exception:
            return obj.get_full_name() or obj.username

    def get_customer_id(self, obj):
        customer = customer_for_user(obj)
        return str(customer.id) if customer else None


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user_role(user)
        token['name'] = user.get_full_name() or user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data


class CustomerRegistrationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=160)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=40, required=False, allow_blank=True)
    company = serializers.CharField(max_length=160, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(username=value).exists() or User.objects.filter(email=value).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        email = validated_data['email']
        name = validated_data['name'].strip()
        customer = Customer.objects.create(
            name=name,
            email=email,
            phone=validated_data.get('phone', '').strip(),
            company=validated_data.get('company', '').strip(),
        )
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=validated_data['password'],
                first_name=name.split(' ', 1)[0],
                last_name=name.split(' ', 1)[1] if ' ' in name else '',
            )
        except Exception:
            customer.delete()
            raise

        profile = user.agent_profile
        profile.role = 'customer'
        profile.customer = customer
        profile.display_name = name
        profile.save(update_fields=['role', 'customer', 'display_name'])
        return user


class CustomerSerializer(serializers.ModelSerializer):
    ticket_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'email', 'phone', 'company', 'notes',
            'tags', 'ticket_count', 'created_at', 'updated_at',
        ]

    def get_ticket_count(self, obj):
        return obj.tickets.count()


class CustomerSelfSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'phone', 'company', 'created_at', 'updated_at']
        read_only_fields = ['id', 'email', 'created_at', 'updated_at']


class TicketMessageSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_role = serializers.SerializerMethodField()

    class Meta:
        model = TicketMessage
        fields = [
            'id', 'author_username', 'author_name', 'author_role',
            'body', 'is_internal', 'is_ai_generated', 'created_at',
        ]
        read_only_fields = ['id', 'author_username', 'author_role', 'created_at']

    def get_author_role(self, obj):
        return user_role(obj.author) if obj.author else 'customer'


class TicketSerializer(serializers.ModelSerializer):
    customer_id = serializers.PrimaryKeyRelatedField(
        source='customer',
        queryset=Customer.objects.all(),
        write_only=True,
        required=False,
    )
    customer = CustomerSerializer(read_only=True)
    assigned_to_username = serializers.SlugRelatedField(
        source='assigned_to',
        slug_field='username',
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )
    message_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_number', 'subject', 'description',
            'customer_id', 'customer', 'assigned_to_username',
            'status', 'priority', 'source', 'category', 'tags',
            'message_count', 'created_at', 'updated_at',
            'first_response_at', 'resolved_at',
        ]
        read_only_fields = [
            'id', 'ticket_number', 'created_at', 'updated_at',
            'first_response_at', 'resolved_at',
        ]

    def get_message_count(self, obj):
        request = self.context.get('request')
        if request and user_role(request.user) == 'customer':
            return obj.messages.filter(is_internal=False).count()
        return obj.messages.count()


class CustomerTicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'ticket_number', 'subject', 'description', 'category', 'created_at']
        read_only_fields = ['id', 'ticket_number', 'created_at']


class TicketDetailSerializer(TicketSerializer):
    messages = serializers.SerializerMethodField()

    class Meta(TicketSerializer.Meta):
        fields = TicketSerializer.Meta.fields + ['messages']

    def get_messages(self, obj):
        request = self.context.get('request')
        qs = obj.messages.all()
        if request and user_role(request.user) == 'customer':
            qs = qs.filter(is_internal=False)
        return TicketMessageSerializer(qs, many=True, context=self.context).data


class KnowledgeBaseArticleSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = KnowledgeBaseArticle
        fields = [
            'id', 'title', 'slug', 'category', 'content',
            'is_published', 'created_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['slug'] = self._unique_slug(validated_data['title'])
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

    def _unique_slug(self, title):
        base = slugify(title)[:210] or 'article'
        slug = base
        n = 2
        while KnowledgeBaseArticle.objects.filter(slug=slug).exists():
            slug = f'{base}-{n}'
            n += 1
        return slug


class ActivityLogSerializer(serializers.ModelSerializer):
    actor = serializers.CharField(source='actor.username', read_only=True)

    class Meta:
        model = ActivityLog
        fields = [
            'id', 'actor', 'action', 'entity_type',
            'entity_id', 'summary', 'metadata', 'created_at',
        ]


class TeamMemberSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'is_active', 'role', 'display_name', 'date_joined',
        ]

    def get_role(self, obj):
        return user_role(obj)

    def get_display_name(self, obj):
        try:
            return obj.agent_profile.display_name or obj.get_full_name() or obj.username
        except Exception:
            return obj.get_full_name() or obj.username


class TeamMemberCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    display_name = serializers.CharField(max_length=120, required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=['agent', 'supervisor'])
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_username(self, value):
        value = value.strip()
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('This username is already in use.')
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        display_name = validated_data.pop('display_name', '')
        role = validated_data.pop('role')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        profile = user.agent_profile
        profile.role = role
        profile.display_name = display_name or user.get_full_name() or user.username
        profile.save(update_fields=['role', 'display_name'])
        return user
