from django.contrib.auth.models import User
from django.utils.text import slugify
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import AgentProfile, Customer, Ticket, TicketMessage, KnowledgeBaseArticle, ActivityLog
from .permissions import user_role

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['username','email','first_name','last_name','is_active','role','display_name']
    def get_role(self, obj): return user_role(obj)
    def get_display_name(self, obj):
        try: return obj.agent_profile.display_name or obj.get_full_name() or obj.username
        except Exception: return obj.get_full_name() or obj.username

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

class CustomerSerializer(serializers.ModelSerializer):
    ticket_count = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Customer
        fields = ['id','name','email','phone','company','notes','tags','ticket_count','created_at','updated_at']
    def get_ticket_count(self, obj): return obj.tickets.count()

class TicketMessageSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    class Meta:
        model = TicketMessage
        fields = ['id','author_username','author_name','body','is_internal','is_ai_generated','created_at']
        read_only_fields = ['id','author_username','created_at']

class TicketSerializer(serializers.ModelSerializer):
    customer_id = serializers.PrimaryKeyRelatedField(source='customer', queryset=Customer.objects.all(), write_only=True)
    customer = CustomerSerializer(read_only=True)
    assigned_to_username = serializers.SlugRelatedField(source='assigned_to', slug_field='username', queryset=User.objects.all(), required=False, allow_null=True)
    message_count = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Ticket
        fields = ['id','ticket_number','subject','description','customer_id','customer','assigned_to_username','status','priority','source','category','tags','message_count','created_at','updated_at','first_response_at','resolved_at']
        read_only_fields = ['id','ticket_number','created_at','updated_at','first_response_at','resolved_at']
    def get_message_count(self, obj): return obj.messages.count()

class TicketDetailSerializer(TicketSerializer):
    messages = TicketMessageSerializer(many=True, read_only=True)
    class Meta(TicketSerializer.Meta):
        fields = TicketSerializer.Meta.fields + ['messages']

class KnowledgeBaseArticleSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    class Meta:
        model = KnowledgeBaseArticle
        fields = ['id','title','slug','category','content','is_published','created_by','created_at','updated_at']
        read_only_fields = ['id','slug','created_by','created_at','updated_at']
    def create(self, validated_data):
        validated_data['slug'] = self._unique_slug(validated_data['title'])
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
    def _unique_slug(self, title):
        base = slugify(title)[:210] or 'article'; slug = base; n = 2
        while KnowledgeBaseArticle.objects.filter(slug=slug).exists():
            slug = f'{base}-{n}'; n += 1
        return slug

class ActivityLogSerializer(serializers.ModelSerializer):
    actor = serializers.CharField(source='actor.username', read_only=True)
    class Meta:
        model = ActivityLog
        fields = ['id','actor','action','entity_type','entity_id','summary','metadata','created_at']

class TeamMemberSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['username','email','first_name','last_name','is_active','role','display_name','date_joined']
    def get_role(self, obj): return user_role(obj)
    def get_display_name(self, obj):
        try: return obj.agent_profile.display_name
        except Exception: return obj.get_full_name() or obj.username
