from django.shortcuts import render
from rest_framework import generics, status, views
from .serializer import RegisterSerializer, EmailVerificationSerializer, LoginSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .utils import Utils
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from drf_spectacular import openapi
# Create your views here.

class RegisterView(generics.GenericAPIView):

    serializer_class = RegisterSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_data = serializer.data
        user=User.objects.get(email=user_data['email'])

        token=RefreshToken.for_user(user).access_token
        current_site = get_current_site(request).domain
        relativeLink=reverse('email-verify')

        absolute_url = 'http://'+current_site+relativeLink+"?token="+str(token)

        email_body = 'Hi ' +user.username+ ' Use link below to verify the email.\n' +absolute_url

        data={'email_body': email_body, 'to_email': user.email , 'domain': absolute_url, 'email_subject': 'Verify email'}

        Utils.send_email(data)

        return Response(user_data, status = status.HTTP_201_CREATED)



class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializer
    # token_param_config = openapi.Parameter('token', in_=openapi.IN_QUERY, description='description', type=openapi.TYPE_STRING)
    # @extend_schema(manual_parameter=token_param_config)
    @extend_schema(
            parameters=[
                OpenApiParameter(name='token', description='token', required=False, type=str),
            ]
    )
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode( token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()

            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as indentifier:
            return Response({'error': 'Link was expired.'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as indentifier:
            return Response({'error': 'Invalid token found here.'}, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
