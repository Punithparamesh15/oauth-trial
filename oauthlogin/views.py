from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import *
from .serializers import UserSerializer, AdminSerializer
from django.contrib.auth.hashers import check_password, make_password
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model, authenticate
from oauth2_provider.models import AccessToken, oauth2_settings
from django.core.exceptions import ObjectDoesNotExist
import requests
from oauth2_provider.models import AccessToken, Application
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import timedelta
from django.conf import settings
from oauth2_provider.models import RefreshToken
from django.db import transaction
from rest_framework.pagination import PageNumberPagination
from rest_framework import pagination

# Create your views here.
def home(request):
    return HttpResponse("Welcome to the new project!")

class CustomPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):

        return Response({                                 # Customizing the response to include 'links' (next and previous)
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
            },
            'count': self.page.paginator.count,           # Total number of items
            'results': data                               # The paginated results (the actual data)
        })
    
#class UserPagination(PageNumberPagination):
#    page_size = 5

class UserAPIView(APIView):

    #authentication_classes = [OAuth2Authentication]
    #permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    def get(self, request, user_id=None):
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                serializer = UserSerializer(user)
                return Response(serializer.data)
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            
        users = User.objects.all()
        #paginator = UserPagination()
        paginator = CustomPagination()                             # Use the custom pagination class
        
        result_page = paginator.paginate_queryset(users, request)

        #serializer = UserSerializer(users, many=True)
        serializer = UserSerializer(result_page, many=True)

        #return Response(serializer.data)
        return paginator.get_paginated_response(serializer.data)
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            print("Validated Data:", validated_data) 
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("Errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user, data=request.data)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                print("Validated Data:", validated_data) 
                serializer.save()
                return Response(serializer.data)
            else:
                print("Errors:", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
    def patch(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user, data=request.data, partial=True)  # Allow partial updates
            if serializer.is_valid():
                validated_data = serializer.validated_data
                print("Validated Data:", validated_data) 
                serializer.save()
                return Response(serializer.data)
            else:
                print("Errors:", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
#class AdminPagination(PageNumberPagination):       # custom pagination, We can set differnt page size for each class 
#    page_size = 5                           

class AdminAPIView(APIView):

    #authentication_classes = [OAuth2Authentication]
    #permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    def get(self, request, admin_id=None):
        if admin_id:
            try:
                admin = Admin.objects.get(id=admin_id)
                serializer = AdminSerializer(admin)
                return Response(serializer.data)
            except Admin.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

        admins = Admin.objects.all()
        #paginator = AdminPagination()
        paginator = CustomPagination()                                             # Use the custom pagination class

        result_page = paginator.paginate_queryset(admins, request)

        serializer = AdminSerializer(result_page, many=True)
        #serializer = AdminSerializer(admins, many=True)

        #return Response(serializer.data)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = AdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("Errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, admin_id):
        try:
            admin = Admin.objects.get(id=admin_id)
            serializer = AdminSerializer(admin, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Admin.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, admin_id):
        try:
            admin = Admin.objects.get(id=admin_id)
            serializer = AdminSerializer(admin, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Admin.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, admin_id):
        try:
            admin = Admin.objects.get(id=admin_id)
            admin.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Admin.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

User = get_user_model()

class OAuthTokenView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        #print("Received request with data stage-1:", request.data)
        
        client_id = request.data.get("client_id")
        client_secret = request.data.get("client_secret")
        contact = request.data.get("contact")
        password = request.data.get("password")

        #print("Extracted client_id stage-2:", client_id)               # Debug client_id
        #print("Extracted client_secret stage-2:", client_secret)       # Debug client_secret
        #print("Extracted contact stage-2:", contact)                   # Debug contact
        #print("Extracted password stage-2:", password)                 # Debug password

        try:
            user = User.objects.get(contact=contact)
            #print("User ID:", user.id)
            #print("User found stage-3:", user)
            if not user.check_password(password):
                #print("Password mismatch for user stage-4.")
                return Response({"error": "Invalid contact or password."}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            #print("User with contact does not exist stage-4.")
            return Response({"error": "Invalid contact or password."}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            application = Application.objects.get(client_id=client_id)

            #print("Application ID:", application.id)
            #print("Application found stage-5:", application)
            
            if client_secret != application.client_secret:
               
               #print("Client secret mismatch.") 

               return Response({"error": "Invalid client credentials stage-6."}, status=status.HTTP_401_UNAUTHORIZED)
        except Application.DoesNotExist:

            #print("Application with client_id does not exist stage-6.") 

            return Response({"error": "Invalid client_id."}, status=status.HTTP_401_UNAUTHORIZED)

        
        expires = timezone.now() + timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS)
        print("Token expiration time set to stage-7:", expires)

        with transaction.atomic():
            try:

                AccessToken.objects.filter(user=user, application=application).delete()
                RefreshToken.objects.filter(user=user, application=application).delete()

                access_token = AccessToken.objects.create(
                    user=user,
                    application=application,
                    token=uuid4().hex,
                    expires=expires,
                )

                #print("Access token created stage-8:", access_token)

                refresh_token = RefreshToken.objects.create(
                    user=user,
                    application=application,
                    token=uuid4().hex,
                    access_token=access_token,
                )

                #print("Refresh token created stage-9:", refresh_token)
            except Exception as e:
                #print("Error creating tokens:", str(e))  # Debug any token creation errors
                return Response({"error": "Failed to create tokens."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "access_token": access_token.token,
            "refresh_token": refresh_token.token,
            "expires_in": oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS
        }, status=status.HTTP_200_OK)

class UserDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user                   # Retrieve the authenticated user from the token

        try:
            user_serializer = UserSerializer(user)
            admin = Admin.objects.get(user=user)  # Get the associated admin info
            admin_serializer = AdminSerializer(admin)

            return Response({
                "admin": admin_serializer.data
            })
        except Admin.DoesNotExist:
            return Response({"error": "Admin details not found."}, status=status.HTTP_404_NOT_FOUND)