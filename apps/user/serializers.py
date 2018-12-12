from rest_framework import serializers
from rest_framework.validators import UniqueValidator
import re
from user.models import UserProfile


class RegisterUserSerializer(serializers.ModelSerializer):
	username = serializers.CharField(label='用户名', required=True, allow_blank=False, validators=[
		UniqueValidator(queryset=UserProfile.objects.all(), message='用户名不能重复')
	])
	password = serializers.CharField(label='密码', write_only=True,required=True, allow_blank=False, min_length=6,
									 style={'input_type': 'password'})
	password2 = serializers.CharField(label='确认密码', write_only=True, required=True, allow_blank=False, min_length=6,
									  style={'input_type': 'password'})
	mobile = serializers.CharField(label='手机号', required=True, allow_blank=False, min_length=11, max_length=11,
								   validators=[
									   UniqueValidator(queryset=UserProfile.objects.all(), message='手机号不能重复')
								   ])

	class Meta:
		model = UserProfile
		fields = ['username', 'password', 'password2', 'mobile','verify_info']

	def validate_mobile(self, data):
		if not re.match(r'^1([38][0-9]|4[579]|5[0-3,5-9]|6[6]|7[0135678]|9[89])\d{8}$', data):
			raise serializers.ValidationError('手机号格式错误')
		return data

	def validate(self, attrs):
		if attrs['password'] != attrs['password2']:
			raise serializers.ValidationError('两次输入密码不一致')
		return attrs

	def create(self, validated_data):
		del validated_data['password2']
		user = UserProfile.objects.create(**validated_data)
		user.set_password(validated_data['password'])
		user.save()
		return user
