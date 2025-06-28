from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken as JWTRefreshToken
from django.contrib.auth import login, logout
from django.utils import timezone
from django.http import JsonResponse

from .models import User, RefreshToken
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserProfileSerializer,
    ChangePasswordSerializer
)

def get_client_info(request):
    """Get client information (IP, User-Agent)"""
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    return ip_address, user_agent

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    """
    New User Registration

    Process:
    1. Validate data (email, username uniqueness, password strength)
    2. Create a user with a hashed password
    3. Generate JWT tokens
    4. Return tokens and user data
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        # Utwórz użytkownika
        user = serializer.save()
        
        # Pobierz informacje o kliencie
        ip_address, user_agent = get_client_info(request)
        
        # Wygeneruj JWT tokeny
        jwt_refresh = JWTRefreshToken.for_user(user)
        jwt_access = jwt_refresh.access_token
        
        # Utwórz custom refresh token w bazie
        refresh_token = RefreshToken.create_for_user(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Aktualizuj last_login
        user.last_login = timezone.now()
        user.save()
        
        # Przygotuj odpowiedź
        user_data = UserProfileSerializer(user).data
        
        return Response({
            'status': 'success',
            'message': 'The account has been created successfully!',
            'user': user_data,
            'tokens': {
                'access': str(jwt_access),
                'refresh': str(jwt_refresh),
                'custom_refresh': str(refresh_token.token)
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'status': 'error',
        'message': 'Validation errors!',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_user(request):
    """
    User Login

    Process:
    1. Check Email/Password
    2. Generate New Tokens
    3. Invalidate Old Tokens (Optional)
    4. Return Tokens and User Data
    """
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Pobierz informacje o kliencie
        ip_address, user_agent = get_client_info(request)
        
        # Wygeneruj JWT tokeny
        jwt_refresh = JWTRefreshToken.for_user(user)
        jwt_access = jwt_refresh.access_token
        
        # Utwórz custom refresh token
        refresh_token = RefreshToken.create_for_user(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Aktualizuj last_login
        user.last_login = timezone.now()
        user.save()
        
        # Przygotuj odpowiedź
        user_data = UserProfileSerializer(user).data
        
        return Response({
            'status': 'success',
            'message': 'Log in successfull',
            'user': user_data,
            'tokens': {
                'access': str(jwt_access),
                'refresh': str(jwt_refresh),
                'custom_refresh': str(refresh_token.token)
            }
        }, status=status.HTTP_200_OK)
    
    return Response({
        'status': 'error',
        'message': 'Incorrect login details',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_user(request):
    """
    Logging out a user

    Process:
    1. Invalidate all user refresh tokens
    2. Add current JWT token to blacklist (if using)
    3. Clear session
    """
    try:
        user = request.user
        
        # Unieważnij wszystkie custom refresh tokeny
        RefreshToken.objects.filter(user=user, is_active=True).update(is_active=False)
        
        # Jeśli chcesz dodać JWT token do blacklisty, możesz to zrobić tutaj
        # (wymaga dodatkowej konfiguracji djangorestframework-simplejwt)
        
        return Response({
            'status': 'success',
            'message': 'Log out successfull'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': 'Log out error',
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    """
    Get or update user profile

    GET: Returns profile data
    PUT: Updates profile data (without password)
    """
    user = request.user
    
    if request.method == 'GET':
        # Zwróć dane profilu
        serializer = UserProfileSerializer(user)
        return Response({
            'status': 'success',
            'user': serializer.data
        })
    
    elif request.method == 'PUT':
        # Aktualizuj profil
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Profile updated successfully',
                'user': serializer.data
            })
        
        return Response({
            'status': 'error',
            'message': 'Validation errors',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """
    Changing User Password

    Process:
    1. Check Current Password
    2. Validate New Password
    3. Set New Password
    4. Invalidate All Refresh Tokens (Forces Re-Login)
    """
    serializer = ChangePasswordSerializer(
        data=request.data, 
        context={'request': request}
    )
    
    if serializer.is_valid():
        user = request.user
        new_password = serializer.validated_data['new_password']
        
        # Ustaw nowe hasło
        user.set_password(new_password)
        user.save()
        
        # Unieważnij wszystkie refresh tokeny (wymusza ponowne logowanie)
        RefreshToken.objects.filter(user=user, is_active=True).update(is_active=False)
        
        return Response({
            'status': 'success',
            'message': 'HPassword changed successfully. Log in again.'
        })
    
    return Response({
        'status': 'error',
        'message': 'Validation errors',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def auth_status(request):
    """
Check user authorization status

Useful for verifying if the token is still valid
    """
    user = request.user
    user_data = UserProfileSerializer(user).data
    
    return Response({
        'status': 'success',
        'authenticated': True,
        'user': user_data
    })

# Secondary endpoint for testing
@api_view(['GET'])
def auth_test(request):
    """Test endpoint autoryzacji"""
    if request.user.is_authenticated:
        return JsonResponse({
            'authenticated': True,
            'user': request.user.username,
            'user_id': request.user.id
        })
    else:
        return JsonResponse({
            'authenticated': False,
            'user': None
        })