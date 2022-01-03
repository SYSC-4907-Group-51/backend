from user.models import User, Log
from user.serializers import UserRegisterSerializer, UserUpdateSerializer, UserDeleteSerializer, LogSerializer
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from .utils import get_tokens_for_user, logout_user, Logger

class UserRegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        action = 'User {} registered'.format(serializer.instance.username)
        Logger(user=serializer.instance, action=action).info()

        return Response(serializer.data, status=201)

class UserLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        try:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                token = get_tokens_for_user(user)
                action = 'User {} logged in successfully'.format(username)
                Logger(user=user, action=action).info()
                return Response(
                    {
                        'id': user.id, 
                        'username': user.username, 
                        'first_name': user.first_name, 
                        'last_name': user.last_name, 
                        'email': user.email, 
                        'created_at': user.created_at, 
                        'updated_at': user.updated_at,
                        **token
                    }, 
                    status=200
                )
            else:
                action = 'User {} failed to log in'.format(username)
                # get User from username
                user = User.objects.get(username=username)
                Logger(user=user, action=action).warn()
                return Response({'details': 'Invalid username/password'}, status=400)
        except User.DoesNotExist:
            return Response(status=403)

class UserLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        logout(request)
        status = logout_user(request.data.get('refresh'))
        if status:
            action = 'User {} logged out successfully'.format(request.user.username)
            Logger(user=request.user, action=action).info()
            return Response({'detail': 'Successfully Logged out'}, status=200)
        else:
            action = 'User {} failed to log out'.format(request.user.username)
            Logger(user=request.user, action=action).warn()
            return Response({'detail': 'Invalid refresh token'}, status=400)

class UserStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        return Response(
            {
                'id': request.user.id,
                'username': request.user.username,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'created_at': request.user.created_at,
                'updated_at': request.user.updated_at
            }
        )

class UserUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def put(self, request):
        serializer = UserUpdateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        action = 'User {} updated: {}'.format(request.user.username, ", ".join(request.data.keys()))
        Logger(request.user, action).info()

        serializer.update(request.user, request.data)
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def delete(self, request):
        serializer = UserDeleteSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        # if deletion is successful, the log will be deleted
        # if deletion is unsuccessful, the log will be preserved for warning
        action = 'User {} tried to delete account'.format(request.user.username)
        Logger(request.user, action).warn()

        serializer.delete(request.user, request.data)
        return Response(status=status.HTTP_204_NO_CONTENT)

class LogView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        logs = Log.objects.filter(user=request.user).order_by('-created_at')
        serializer = LogSerializer(logs, many=True)
        return Response(serializer.data)
