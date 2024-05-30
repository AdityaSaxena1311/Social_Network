from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import FriendRequest
from .serializers import UserSerializer, LoginSerializer, FriendRequestSerializer
from django.db.models import Q

@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email'].lower()
        password = serializer.validated_data['password']
        user = authenticate(username=email, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_users(request):
    keyword = request.query_params.get('keyword', '')
    if keyword:
        users = User.objects.filter(Q(email__iexact=keyword) | Q(username__icontains=keyword)).distinct()
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(users, request)
        serializer = UserSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    return Response({'error': 'Keyword is required'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_friend_request(request, to_user_id):
    to_user = User.objects.get(id=to_user_id)
    friend_request, created = FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
    if created:
        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response({'error': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def handle_friend_request(request, request_id, action):
    friend_request = FriendRequest.objects.get(id=request_id, to_user=request.user)
    if action == 'accept':
        friend_request.status = 'accepted'
    elif action == 'reject':
        friend_request.status = 'rejected'
    else:
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
    friend_request.save()
    return Response(FriendRequestSerializer(friend_request).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_friends(request):
    friends = User.objects.filter(Q(sent_requests__to_user=request.user, sent_requests__status='accepted') | Q(received_requests__from_user=request.user, received_requests__status='accepted'))
    serializer = UserSerializer(friends, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_pending_requests(request):
    pending_requests = FriendRequest.objects.filter(to_user=request.user, status='pending')
    serializer = FriendRequestSerializer(pending_requests, many=True)
    return Response(serializer.data)
