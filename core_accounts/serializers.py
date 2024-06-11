import random
import string
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class CreateUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['first_name','last_name', 'email', 'password', 'password2']
        extra_kwargs = {'password': {'write_only': True}}
    
    def generate_random_username(self, prefix="CM", length=8):
        letters = string.ascii_letters + string.digits
        random_string = ''.join(random.choice(letters) for i in range(length))
        
        max_length = 200
        total_length = len(prefix) + length
        if total_length > max_length:
            raise ValueError(f"Total length of generated username ({total_length}) exceeds the maximum allowed length ({max_length}).")
        
        return f"{prefix}{random_string}"

    def validate(self, data):
        password = data.get('password')
        password2 = data.pop('password2', None)

        validate_password(password)

        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords do not match'})

        return data

    def create(self, validated_data):
        email = validated_data.pop('email', None)
        if email is None:
            raise serializers.ValidationError({'email': 'Email field is required'})

        validated_data['password'] = validated_data.get('password')
        username = self.generate_random_username(prefix="CM", length=8)
        user = User.objects.create_user(email=email, username=username, **validated_data)
        return user

class UpdateUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile', 'first_name', 'last_name', 'email', 'date_of_birth', 'gender', 'mobile_number', 'hourly_rate', 'experience', 'info', 'degree']
        extra_kwargs = {
            'hourly_rate': {'required': False},
            'experience': {'required': False},
            'info': {'required': False},
            'degree': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'email': {'required': False},
        }

    def update(self, instance, validated_data):
        user_type = instance.user_type
        if user_type == 'tutee':
            validated_data.pop('hourly_rate', None)
            validated_data.pop('experience', None)
            validated_data.pop('degree', None)
        elif user_type == 'tutor':
            validated_data.pop('info', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class ShowUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id',
            'profile', 'profile_slug', 'first_name', 'last_name', 'email', 
            'date_of_birth', 'gender', 'mobile_number', 'user_type', 
            'hourly_rate', 'response_time', 't_to_number_of_students', 
            'experience', 'degree', 'info'
        )
        extra_kwargs = {
            'hourly_rate': {'required': False},
            'response_time': {'required': False},
            't_to_number_of_students': {'required': False},
            'experience': {'required': False},
            'degree': {'required': False},
            'info': {'required': False}
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.user_type == 'tutee':
            representation.pop('hourly_rate', None)
            representation.pop('response_time', None)
            representation.pop('t_to_number_of_students', None)
            representation.pop('experience', None)
            representation.pop('degree', None)
        elif instance.user_type == 'tutor':
            representation.pop('info', None)
        return representation