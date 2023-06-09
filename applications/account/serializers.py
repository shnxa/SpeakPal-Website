from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from .models import FriendRequest
from .tasks import *


User = get_user_model()



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, required=True, write_only=True)
    password_confirmation = serializers.CharField(min_length=8, required=True, write_only=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password', 'password_confirmation', 'email', 'mlang',
                  'eng_level', 'gender')

    def validate(self, attrs):
        password2 = attrs.pop('password_confirmation')
        if password2 != attrs['password']:
            raise serializers.ValidationError(
                'Passwords didn\'t match')
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ActivationSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, max_length=255)
    default_error_messages = {
        'bad_code': _('Code is expired or invalid!')
    }

    def validate(self, attrs):
        self.code = attrs['code']
        return attrs

    def save(self, **kwargs):
        try:
            user = User.objects.get(activation_code=self.code)
            user.is_active = True
            user.activation_code = None
            user.save()
            send_welcome_message(user.email,)

        except User.DoesNotExist:
            self.fail('bad_code')


class PasswordResetSerializer(serializers.Serializer):
    password_reset_code = serializers.CharField(required=True, max_length=255)
    password = serializers.CharField(required=True, max_length=30, min_length=8, write_only=True)
    password2 = serializers.CharField(required=True, max_length=30, min_length=8, write_only=True)
    default_error_messages = {
        'bad_code': _('Code is expired or invalid!')
    }

    def validate(self, attrs):
        self.password_reset_code = attrs['password_reset_code']
        password2 = attrs.pop('password2')
        password = attrs['password']
        if password2 != password:
            raise serializers.ValidationError('Passwords didn\'t match!')
        if password == User.password:
            raise serializers.ValidationError('Password cant be previous!')
        user = User.objects.get(activation_code=attrs['password_reset_code'])
        user.set_password(password)
        password_change_notification(user.email,)
        user.save()
        return attrs

    def save(self, **kwargs):
        try:
            user = User.objects.get(activation_code=self.password_reset_code)
            user.activation_code = ''
            user.save()
        except User.DoesNotExist:
            self.fail('bad_code')
            

class FriendListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('friends',)

    def to_representation(self, instance):
        return {'friends': FriendSerializer(instance.related_friends.all(), many=True).data}
    
    
class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password', 'activation_code', 'user_permissions', 'friends',)

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        represent.pop('first_name')
        represent.pop('last_name')
        represent.pop('eng_level')
        return represent
    
    
class FriendRequestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = '__all__'
        
        
class FriendReqInSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        exclude = ('to_user',)

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        user = User.objects.get(id=represent['from_user'])
        req_id = represent.pop('id')
        user_id = represent.pop('from_user')
        represent['user_id'] = user_id
        represent['request_id'] = req_id
        represent['email'] = user.email
        represent['username'] = user.username
        return represent
    
    
class FriendReqOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        exclude = ('from_user',)

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        user = User.objects.get(id=represent['to_user'])
        req_id = represent.pop('id')
        user_id = represent.pop('to_user')
        represent['user_id'] = user_id
        represent['request_id'] = req_id
        represent['email'] = user.email
        represent['username'] = user.username
        return represent
    
    
class FriendHandleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('active',)