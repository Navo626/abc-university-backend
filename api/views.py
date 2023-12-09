from django.contrib.auth import get_user_model, update_session_auth_hash
from knox.auth import AuthToken, TokenAuthentication
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import models
from .serializers import UserSerializer, StudentSerializer


@api_view(['GET'])
def get_routes(request):
    """
    Get a list of available API routes.

    Returns:
        Response: JSON response containing a list of routes.
    """
    try:
        # Define the available routes
        routes = [
            "api/login",
            "api/user",
        ]
        # Return the list of routes as a JSON response with a 200 status code
        return Response(routes, status=status.HTTP_200_OK)

    # Handle unexpected exceptions and provide a generic error message
    except Exception as e:
        return Response({
            "error": f"An error occurred: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def create_user(request):
    """
    Create a new user.

    Args:
        request: The HTTP request object.

    Returns:
        Response: JSON response containing user information.
    """
    try:
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Return a JSON response with the created user information and a 201 status code
        return Response({
            'user_info': {
                'username': user.username,
            },
        }, status=status.HTTP_201_CREATED)

    # Handle unexpected exceptions and provide a generic error message
    except Exception as e:
        return Response({
            "error": f"An error occurred: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def login_user(request):
    """
    Log in a user and generate an authentication token.

    Args:
        request: The HTTP request object.

    Returns:
        Response: JSON response containing user information and token.
    """
    try:
        # Extract username and password from the request data
        username = request.data.get('username')
        password = request.data.get('password')

        # Retrieve the user based on the provided username
        user = get_user_model().objects.filter(username=username).first()

        # Check if the user exists
        if user is None:
            raise AuthenticationFailed("User not found")

        # Check if the provided password is correct
        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password")

        # Generate an authentication token for the user
        _, token = AuthToken.objects.create(user)

        # Set user as active (if needed)
        if not user.is_active:
            user.is_active = True
            user.save()

        # Return a JSON response with user information and the generated token
        return Response({
            'user_info': {
                'username': user.username,
            },
            'token': token
        }, status=status.HTTP_200_OK)

    # Handle unexpected exceptions and provide a generic error message
    except Exception as e:
        return Response({
            "error": f"An error occurred: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_user(request):
    """
    Check if the user is authenticated.

    Returns:
        Response: JSON response indicating whether the token is valid.
    """
    return Response({
        "message": "Token is valid"
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_student(request):
    """
    Retrieve information about the authenticated student.

    Returns:
        Response: JSON response containing student details.
    """
    try:
        # Get the authenticated user
        user = request.user

        # Retrieve the associated student based on the username
        student = models.Student.objects.get(username=user.username)

        # Check if the student exists
        if student:
            # Serialize the student data and return a JSON response
            serializer = StudentSerializer(student)
            return Response(serializer.data, status=status.HTTP_200_OK)

    # Handle the case when the student is not found
    except models.Student.DoesNotExist:
        return Response({
            "error": "Student not found"
        }, status=status.HTTP_404_NOT_FOUND)

    # Handle unexpected exceptions and provide a generic error message
    except Exception as e:
        return Response({
            "error": f"An error occurred: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_password(request):
    """
    Update the user's password.

    Args:
        request: The HTTP request object.

    Returns:
        Response: JSON response indicating the result of the password update.
    """
    # Extract data from the request
    current_password = request.data.get('currentPassword')
    new_password = request.data.get('newPassword')
    confirm_password = request.data.get('confirmPassword')

    # Get the user associated with the provided token
    user = request.user

    # Check if the current password matches the one in the database
    if not user.check_password(current_password):
        return Response({'error': 'Current password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the new password and confirm password match
    if new_password != confirm_password:
        return Response({'error': 'New password and confirm password do not match.'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Update the user's password
    user.set_password(new_password)
    user.save()

    # Update session authentication hash
    update_session_auth_hash(request, user)

    # Generate a new token to invalidate the old ones
    AuthToken.objects.create(user)

    return Response({'message': 'Password updated successfully.'}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile_student(request):
    """
    Update the user's profile details.

    Args:
        request: The HTTP request object.

    Returns:
        Response: JSON response indicating the result of the profile update.
    """
    try:
        # Get the user associated with the provided token
        user = request.user

        # Retrieve the associated student based on the username
        student = models.Student.objects.get(username=user.username)

        if 'fnameUpdate' in request.data:
            student.first_name = request.data.get('fnameUpdate')
            student.save()
            return Response({'message': 'First name updated successfully.'}, status=status.HTTP_200_OK)
        if 'lnameUpdate' in request.data:
            student.last_name = request.data.get('lnameUpdate')
            student.save()
            return Response({'message': 'Last name updated successfully.'}, status=status.HTTP_200_OK)
        if 'telUpdate' in request.data:
            student.tel = request.data.get('telUpdate')
            student.save()
            return Response({'message': 'Mobile number updated successfully.'}, status=status.HTTP_200_OK)
        if 'dobUpdate' in request.data:
            student.dob = request.data.get('dobUpdate')
            student.save()
            return Response({'message': 'DOB updated successfully.'}, status=status.HTTP_200_OK)
        if 'descriptionUpdate' in request.data:
            student.description = request.data.get('descriptionUpdate')
            student.save()
            return Response({'message': 'Description updated successfully.'}, status=status.HTTP_200_OK)

        return Response({'error': 'Missing or invalid data'}, status=status.HTTP_400_BAD_REQUEST)

    except models.Student.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if 'fname' is in the request data
