from rest_framework import serializers
from .models import Profile, Certificate

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ['name', 'issuer', 'date']

class ProfileSerializer(serializers.ModelSerializer):
    certificates = CertificateSerializer(many=True)

    class Meta:
        model = Profile
        fields = ['full_name', 'email', 'certificates']

    def create(self, validated_data):
        certificates_data = validated_data.pop('certificates')
        profile = Profile.objects.create(**validated_data)
        for cert_data in certificates_data:
            Certificate.objects.create(profile=profile, **cert_data)
        return profile

    def update(self, instance, validated_data):
        certificates_data = validated_data.pop('certificates', None)
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        if certificates_data is not None:
            instance.certificates.all().delete()
            for cert_data in certificates_data:
                Certificate.objects.create(profile=instance, **cert_data)
        return instance
