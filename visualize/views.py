from rest_framework.response import Response
from rest_framework.views import APIView
from visualize.serializers import KeyShowSerializer, KeyDeleteSerializer
from user.utils import Logger
from rest_framework import permissions, status
from visualize.utils import create_key, RE_GENERATE_KEY_LIMIT, delete_key
from visualize.models import Key
from user.models import User

# Create your views here.
class KeyCreateView(APIView):
    def post(self, request):
        key = create_key(request.user, request.data.get('notes'))
        if key == -1:
            action = 'User {} failed to generate a key'.format(request.user.username)
            Logger(user=request.user, action=action).info()

            return Response({'details': 'Maximum allowable key limit {} is reached'.format(RE_GENERATE_KEY_LIMIT)}, status=400)

        action = 'User {} created a key {} with notes: {}'.format(request.user.username, key.key, request.data.get('notes'))
        Logger(user=request.user, action=action).info()

        return Response({
            'key': key.key,
            'notes': key.notes
        }, status=201)

class KeyShowView(APIView):
    def get(self, request):
        key = Key.objects.filter(user=request.user)
        serializer = KeyShowSerializer(key, many=True)
        return Response(serializer.data)

class KeyDeleteView(APIView):
    def delete(self, request):
        serializer = KeyDeleteSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.delete(request.user, request.data)

        action = 'User {} deleted key {}'.format(request.user.username, serializer.initial_data['key'])
        Logger(request.user, action).info()

        return Response(status=status.HTTP_204_NO_CONTENT)

class VisualizeView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        if request.query_params.get('username') and request.query_params.get('key'):
            try:
                user = User.objects.get(username=request.query_params.get('username'))
            except:
                return Response({'details': 'Invalid request'}, status=400)
            else:
                try:
                    key = Key.objects.get(user=user, key=request.query_params.get('key'))
                except:
                    return Response({'details': 'Invalid request'}, status=400)
                else:
                    delete_key(key)
                    # TODO: data visualization

                    action = 'User {} data is visualized using key {} with notes: {}'.format(user.username, key.key, key.notes)
                    Logger(user, action).info()

                    return Response({
                        'key': key.key,
                        'notes': key.notes,
                        'username': user.username,
                    })
        else:
            return Response({'details': 'Invalid request'}, status=400)