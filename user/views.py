from user.models import User, Log
from user.serializers import *
from tracker.serializers import *
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from .utils import get_tokens_for_user, logout_user, Logger
from tracker.models import *
from datetime import date

class UserRegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        """
            Patient Registeration API
            See: README.md -> /register

            Args:
                request: user request data

            Return:
                dict: response
        """
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        action = 'User {} registered'.format(serializer.instance.username)
        Logger(user=serializer.instance, action=action).info()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        """
            Patient Login API
            See: README.md -> /login

            Args:
                request: user request data

            Return:
                dict: response
        """
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            token = get_tokens_for_user(user)
            action = 'User {} logged in successfully'.format(username)
            Logger(user=user, action=action).info()
            serializer = UserSerializer(user)
            return Response(
                {
                    **serializer.data,
                    **token
                }, 
                status=status.HTTP_200_OK
            )
        else:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({'detail': 'No such user'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                action = 'User {} failed to log in'.format(username)
                Logger(user=user, action=action).warn()
                return Response({'detail': 'Invalid username/password'}, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(APIView):
    def post(self, request):
        """
            Patient Logout API
            See: README.md -> /logout

            Args:
                request: user request data

            Return:
                dict: response
        """
        request_user = request.user
        is_logout = logout_user(request.user)
        logout(request)
        if is_logout:
            action = 'User {} logged out successfully'.format(request_user.username)
            Logger(user=request_user, action=action).info()
            return Response({'detail': 'Successfully Logged out'}, status=status.HTTP_200_OK)
        else:
            action = 'User {} failed to log out'.format(request_user.username)
            Logger(user=request_user, action=action).warn()
            return Response({'detail': 'Unable to logout'}, status=status.HTTP_400_BAD_REQUEST)

class UserStatusView(APIView):
    def get(self, request):
        """
            Patient Status API
            See: README.md -> /status

            Args:
                request: user request data

            Return:
                dict: response
        """
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except:
            is_authorized = False
            profile_not_found = True
        else:
            is_authorized = user_profile.is_authorized
            profile_not_found = False

        try:
            user_device = UserDevice.objects.get(user_profile=user_profile)
        except:
            devices = []
            last_sync_time = 0
        else:
            devices = user_device.devices
            last_sync_time = user_device.last_sync_time

        return Response(
            {
                'username': request.user.username,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'is_authorized': is_authorized,
                'devices': devices,
                'last_sync_time': last_sync_time,
                'profile_not_found': profile_not_found
            },
            status=status.HTTP_200_OK
        )

class UserSyncStatusView(APIView):
    def get(self, request):
        """
            Patient Synchronization Status API
            See: README.md -> /sync-status

            Args:
                request: user request data

            Return:
                dict: response
        """
        date_time = None
        if request.query_params.get('date') is not None:
            try:
                date_time = date.fromisoformat(request.query_params.get('date'))
            except:
                return Response(
                    {
                        'detail': 'Invalid date format',
                        'format': 'YYYY-MM-DD'
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except:
            return Response(
                {
                    'detail': 'User has not yet authorized'
                }, 
                status=status.HTTP_400_BAD_REQUEST
            ) 
        
        if date_time is not None:
            user_sync_status = UserSyncStatus.objects.filter(user_profile=user_profile, date_time=date_time)
        else:
            user_sync_status = UserSyncStatus.objects.filter(user_profile=user_profile)
        serializer = UserSyncStatusSerializer(user_sync_status, many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

class UserUpdateView(APIView):
    def put(self, request):
        """
            Patient Update Account API
            See: README.md -> /update

            Args:
                request: user request data

            Return:
                dict: response
        """
        serializer = UserUpdateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        action = 'User {} updated: {}'.format(request.user.username, ", ".join(request.data.keys()))
        Logger(request.user, action).info()

        serializer.update(request.user, request.data)
        user_seriealizer = UserSerializer(request.user)
        return Response(
            {
                'detail': 'Successfully updated',
                **user_seriealizer.data
            },
            status=status.HTTP_200_OK
        )

class UserDeleteView(APIView):
    def delete(self, request):
        """
            Patient Delete Account API
            See: README.md -> /delete

            Args:
                request: user request data

            Return:
                dict: response
        """
        serializer = UserDeleteSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        # if deletion is successful, the log will be deleted
        # if deletion is unsuccessful, the log will be preserved for warning
        action = 'User {} tried to delete account'.format(request.user.username)
        Logger(request.user, action).warn()

        serializer.delete(request.user, request.data)
        return Response(
            {
                'detail': 'Successfully deleted',
            },
            status=status.HTTP_200_OK
        )

class LogView(APIView):
    def get(self, request):
        """
            Patient Logs API
            See: README.md -> /logs

            Args:
                request: user request data

            Return:
                dict: response
        """
        logs = Log.objects.filter(user=request.user).order_by('-created_at')
        serializer = LogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
