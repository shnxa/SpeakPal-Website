import uuid

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, ListAPIView
import django.db.utils
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from .models import FriendRequest
from .tasks import send_confirmation_mail, send_password_reset_mail
from applications.account import serializers

User = get_user_model()


class RegistrationView(APIView):
    permission_classes = (permissions.AllowAny,)

    @staticmethod
    @swagger_auto_schema(request_body=serializers.RegistrationSerializer)
    def post(request):
        try:
            serializer = serializers.RegistrationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
        except django.db.utils.IntegrityError:
            return Response({'msg': 'Something went wrong, check input please'}, status=400)
        if user:
            try:
                send_confirmation_mail.delay(user.email, user.activation_code)
                return Response({'msg': "Check your email for confirmation!"})
            except:
                return Response({'msg': 'Registered but could not send email.',
                                 'data': serializer.data}, status=201)
        return Response(serializer.data, status=201)


class ActivationView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.ActivationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"msg": "Successfully activated!"}, status=200)


class UserListApiView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = permissions.IsAuthenticated,


class LoginView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    permission_classes = (permissions.AllowAny,)

    @staticmethod
    @swagger_auto_schema(operation_description='Принимает email в виде: "email: example@example.com,'
                                               'и отправляет письмо, если email найден')
    def post(request):
        try:
            email = request.data['email']
            user = User.objects.get(email=email)
            if user.activation_code is not None and user.activation_code != '':
                return Response({'msg': 'Code already sent, please check your inbox!'}, status=200)
            user.activation_code = uuid.uuid4()
            user.save()
        except User.DoesNotExist:
            return Response({'msg': 'Invalid email or not found!'}, status=400)
        send_password_reset_mail.delay(user.email, user.activation_code)
        return Response({'msg': 'Confirmation code sent!'}, status=200)

    @staticmethod
    @swagger_auto_schema(request_body=serializers.PasswordResetSerializer)
    def put(request):
        try:
            serializer = serializers.PasswordResetSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except User.DoesNotExist:
            return Response({'msg': 'Code expired or invalid!'}, status=400)
        return Response({'msg': 'Successfully changed password!'}, status=200)


class LoginSuccess(APIView):
    @staticmethod
    def get(request):
        return Response({'msg': 'Login success'}, status=200)


class SendFriendRequestView(APIView):
    def post(self, request, pk):
        from_user = request.user
        try:
            to_user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response({'msg': 'User not found'}, status=404)
        if to_user in from_user.blocked_list.all():
            return Response({"msg": "This person is in your blocked list, can't send friend request!"}, status=400)
        if from_user in to_user.related_friends.all():
            return Response({'msg': 'You are already friends!'}, status=400)
        friend_request, created = FriendRequest.objects.get_or_create(from_user=from_user, to_user=to_user)
        if created:
            return Response({'msg': 'Friend request sent!'}, status=201)
        else:
            return Response({'msg': 'Friend request was already sent!'}, status=200)


class HandleFriendRequestView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        try:
            friend_request = FriendRequest.objects.get(id=pk)
        except FriendRequest.DoesNotExist:
            return Response({'msg': 'Friend request not found!'}, status=404)
        if friend_request.to_user == request.user:
            friend_request.to_user.friends.add(friend_request.from_user)
            friend_request.from_user.friends.add(friend_request.to_user)
            friend_request.delete()
            return Response({'msg': 'Friend request accepted!'}, status=200)
        else:
            return Response({'msg': 'Friend request not accepted! You cannot accept own request!'}, status=200)

    def delete(self, request, pk):
        friend_req = FriendRequest.objects.get(id=pk)
        friend_req.delete()
        return Response({'msg': 'Successfully deleted!'}, status=204)

class FriendRequestsListView(APIView):
    permission_classes = permissions.IsAuthenticated,

    def get(self, request):
        user_in = FriendRequest.objects.filter(to_user_id=request.user.id)
        user_out = FriendRequest.objects.filter(from_user_id=request.user.id)
        seri1 = serializers.FriendReqInSerializer(instance=user_in, many=True).data
        seri2 = serializers.FriendReqOutSerializer(instance=user_out, many=True).data
        print(seri1)
        return Response({'incoming': seri1, 'outgoing': seri2})

class FriendsDeleteView(APIView):
    permission_classes = permissions.IsAuthenticated,

    def delete(self, request, pk):
        try:
            many_to_many_field = User.objects.get(id=request.user.id).related_friends
            many_to_many_field_2 = User.objects.get(id=pk).related_friends
            friend = User.objects.get(id=request.user.id).related_friends.get(id=pk)
            friend_2 = User.objects.get(id=pk).related_friends.get(id=request.user.id)
            many_to_many_field.remove(friend)
            many_to_many_field_2.remove(friend_2)
        except User.DoesNotExist:
            return Response({'msg': 'Friend not found!'}, status=404)
        return Response({'msg': 'Friend deleted!'}, status=200)

class FriendsListView(APIView):
    permission_classes = permissions.IsAuthenticated,

    def get(self, request):
        user = User.objects.get(id=request.user.id)
        serializer = serializers.FriendListSerializer(instance=user)
        return Response(serializer.data, status=200)


class BlockUserView(APIView):
    permission_classes = permissions.IsAuthenticated,

    def post(self, request, pk):
        user = request.user
        try:
            b_user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response({'msg': 'User not found'}, status=404)
        if b_user in user.blocked_list.all():
            return Response({"msg": "You\'ve already blocked this person!"}, status=400)
        else:
            user.blocked_list.add(b_user)
            if b_user in user.related_friends.all():
                user.related_friends.delete(b_user)
            return Response({"msg": "Successfully blocked!"}, status=200)