from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer, SignUpSerializer, UserSerializer


def tokens_for(user):
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}


def auth_response(user, status_code=status.HTTP_200_OK):
    return Response({'user': UserSerializer(user).data, 'tokens': tokens_for(user)}, status=status_code)


class SignUpView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return auth_response(serializer.save(), status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return auth_response(serializer.validated_data['user'])


class LogoutView(APIView):
    def post(self, request):
        token = request.data.get('refresh')
        if not token:
            return Response({'error': 'A refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            RefreshToken(token).blacklist()
        except TokenError:
            return Response({'error': 'Invalid or expired refresh token.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Logged out successfully.'})


class MeView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({'user': UserSerializer(request.user).data})
