from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from ..defaults import create_default_payment_providers
from  ..models import User
from .userserializer import UserSerializer

from knox.models import AuthToken

from rest_framework.permissions import IsAuthenticated, AllowAny
from knox.auth import TokenAuthentication

class AdminLogin(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        username = request.data.get("username")
        password = request.data.get("password")

        # Validate input
        if not username or not password:
            return Response(
                {
                    "error": "Username and password are required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Authenticate user
        user = authenticate(
            request=request,
            username=username,
            password=password
        )

        create_default_payment_providers()

        if user is None:
            return Response(
                {
                    "error": "Invalid username or password"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        if user.user_type != "ADMIN":
            return Response(
                {
                    "error": "You are not authorized to access the admin panel"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        token_instance, token = AuthToken.objects.create(user)

        # Successful login
        return Response(
            {
                "message": "Admin login successful",

                "user": {
                            "id": user.id,
                            "username": user.username,
                            "token": token,
                            "email": user.email,
                            "phone_number": user.phoneNumber,
                            "user_type": user.user_type,
                            "first_name": user.first_name,
                            "last_name": user.last_name,
                        }
            },
            status=status.HTTP_200_OK
        )

class UserCreateView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        
        serializer = UserSerializer(data=request.data)

        if not serializer.is_valid():
            print(serializer.errors, "SERIALIZER_ERRORS")

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.save()

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )

class UserUpdateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserSerializer(
            user,
            data=request.data
        )

        if serializer.is_valid():
            user = serializer.save()

            return Response(
                UserSerializer(user).data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class CustomerLogin(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        username = request.data.get("username")
        password = request.data.get("password")

        # Validate input
        if not username or not password:
            return Response(
                {
                    "error": "Username and password are required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Authenticate user
        user = authenticate(request=request,username=username,password=password)

        if user is None:
            return Response(
                {
                    "error": "Invalid username or password"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Successful login
        return Response(
            {
                "message": "Login successful",
                "user": {
                            "id": user.id,
                            "first_name": user.first_name,
                            "last_name": user.last_name,
                            "username": user.username,
                            "email": user.email,
                            "phone_number": user.phoneNumber,
                            "user_type": user.user_type,
                        }
            },
            status=status.HTTP_200_OK
        )


class UserListView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        users = User.objects.all()

        serializer = UserSerializer(users, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)