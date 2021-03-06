from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from open_facebook.api import OpenFacebook
from serializers import FacebookSerializer, UserSerializer
from django_facebook.connect import connect_user
from django.utils.http import urlencode
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
class FacebookLogin(APIView):
	def post(self, request, format=None):
		serializer = FacebookSerializer(data=request.data)
		if serializer.is_valid():
			access_token = serializer.data['access_token']
			facebook = OpenFacebook(access_token)
			try:
				user = User.objects.get(username=facebook.get('me')['id'])
				user.last_name = serializer.data['access_token']
				user.save()
			except ObjectDoesNotExist:
				user = User.objects.create_user(facebook.get('me')['id'])
				user.first_name = 'facebook'
				user.last_name = serializer.data['access_token']
				user.save()
			token = Token.objects.get_or_create(user=user)
			return Response({'token': token[0].key})
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateUser(APIView):
	def post(self, request, format=None):
		serializer = UserSerializer(data=request.data)
		if serializer.is_valid():
			try:
				user = User.objects.get(username=serializer.data['username'])
			except ObjectDoesNotExist:
				user = User.objects.create_user(serializer.data['username'], password=serializer.data['password'])
				user.save()
				token = Token.objects.create(user=user)
				return Response({'token': token.key}, status=status.HTTP_201_CREATED)
			return Response({'errors': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
		return Response({'errors': 'Fields may not be blank'}, status=status.HTTP_400_BAD_REQUEST)

class LoginUser(APIView):
	def post(self, request, format=None):
		serializer = UserSerializer(data=request.data)
		print request.data
		if serializer.is_valid():
			user = authenticate(username=serializer.data['username'], password=serializer.data['password'])
			if user:
				if user.first_name == 'facebook':
					return Response({'errors': 'Facebook User'}, status=status.HTTP_400_BAD_REQUEST)
				token = Token.objects.get_or_create(user=user)
				return Response({'token': token[0].key})
		return Response({'errors': 'Username/Password is not correct'}, status=status.HTTP_400_BAD_REQUEST)
