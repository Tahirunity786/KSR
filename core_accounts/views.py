import os
import random
import string
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import Response
from rest_framework import status

from core_accounts.serializers import CreateUserSerializer

from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

from django.conf import settings
from django.core.files.base import ContentFile
from core_accounts.renderers import UserRenderer
from core_accounts.token import get_tokens_for_user

# Third party APIs
from google.auth.transport import requests
from google.oauth2.id_token import verify_oauth2_token
import requests as efwe
from urllib.parse import urlparse
User = get_user_model()

# Create your views here.

class Register(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [UserRenderer]

    def post(self, request, user_type):
        if user_type not in ['tutee', 'tutor']:
            return Response({"Success": False, "Error": "Invalid user type"}, status=status.HTTP_400_BAD_REQUEST)
        
        user_serializer = CreateUserSerializer(data=request.data)
    
        if user_serializer.is_valid():
            current_user = user_serializer.save()
            current_user.user_type = user_type
            current_user.save()
            return Response({"Success": True, "Info": "You can start using our services by login."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"Success": False, "Error": user_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class UserLogin(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [UserRenderer]


    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Email for this user not found"}, status=status.HTTP_400_BAD_REQUEST)

        authenticated_user = authenticate(request, username=user.email, password=password)

        if authenticated_user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if authenticated_user.is_blocked:
            return Response({"error": "Account banned"}, status=status.HTTP_400_BAD_REQUEST)

        profile_url = settings.BACKEND + authenticated_user.profile.url if authenticated_user.profile else None
        token = get_tokens_for_user(authenticated_user)

       

        user_data = {
            "user_id": authenticated_user.id,
            "username": authenticated_user.username,
           
            "profile": profile_url,
            
            "token": token,
        }

        return Response({"message": "Logged in", "user": user_data}, status=status.HTTP_202_ACCEPTED)


class GoogleAuthAPIView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [UserRenderer]
    """
    Google Authentication API View.
    """

    def post(self, request):
        """
        Authenticate user using Google ID token.

        Args:
            request: HTTP request object containing ID token.

        Returns:
            HTTP response with user data and authentication token.
        """
        id_token = request.data.get('idToken')

        try:
            # Verify the ID token
            id_info = verify_oauth2_token(id_token, requests.Request())

            # Get user info
            user_email = id_info.get('email')
            user_image_url = id_info.get('picture')
            name = id_info.get('name')

            if not user_email:
                return Response({"error": "Email not provided in ID token"}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the user exists in the database, or create a new one
            try:
                user = User.objects.get(email=user_email)
                created = False
            except User.DoesNotExist:
                # Generate a random username and password for new user
                username = user_email.split('@')[0]
                password = ''.join(random.choices(
                    string.ascii_letters + string.digits, k=12))
                user = User.objects.create_user(
                    email=user_email, username=username, password=password, full_name=name)
                created = True
            # Download and save the profile picture if available
            if user_image_url:
                try:
                    image_response = efwe.get(user_image_url)
                    image_response.raise_for_status()  # Raise exception for non-200 status codes
                    file_extension = os.path.splitext(
                        urlparse(user_image_url).path)[1] or '.jpg'
                    random_filename = ''.join(random.choices(
                        string.ascii_letters + string.digits, k=12))
                    file_path = os.path.join(
                        settings.MEDIA_ROOT, random_filename + file_extension)
                    with open(file_path, 'wb') as f:
                        f.write(image_response.content)
                    user.profile.save(random_filename + file_extension,
                                      ContentFile(image_response.content), save=True)
                except (requests.RequestException, IOError) as e:
                    return Response({"error": f"Error while fetching image: {e}"}, status=status.HTTP_400_BAD_REQUEST)

            # Generate authentication token
            token = get_tokens_for_user(user)

            # Construct response data
            response_data = {
                'response': 'Account Created' if created else 'Account Logged In',
                'id': user.id,
                'username': user.username,
                'profile_image': user.profile.url if user.profile else None,
                'email': user.email,
                'token': token
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except ValueError as e:
            # Invalid token
            return Response({"error": f"Invalid token: {e}"}, status=status.HTTP_400_BAD_REQUEST)
