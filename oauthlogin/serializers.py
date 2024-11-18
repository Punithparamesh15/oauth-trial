from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def validate(self, data):
        
        if not data['first_name'].isalpha():
            raise serializers.ValidationError({"first_name": "First name must contain only alphabets."})

        middle_name = data.get('middle_name')
        if middle_name and not middle_name.isalpha():
            raise serializers.ValidationError({"middle_name": "Middle name must contain only alphabets."})

        if not data['last_name'].isalpha():
            raise serializers.ValidationError({"last_name": "Last name must contain only alphabets."})

        if not data['contact'].isdigit() or len(data['contact']) != 10:
            raise serializers.ValidationError({"contact": "Contact number must be exactly 10 digits and contain only numeric values."})
        
        return data
    
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])  
        return super().create(validated_data)
    
class AdminSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  

    class Meta:
        model = Admin
        fields = ['id', 'user', 'degree', 'university', 'year_of_passing']

    def create(self, validated_data):
        user = validated_data.pop('user')
        return Admin.objects.create(user=user, **validated_data)
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = UserSerializer(instance.user).data
        return representation