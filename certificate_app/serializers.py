from rest_framework import serializers
from .models import Profile, Certificate

class CertificateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Certificate
        fields = ['id', 'name', 'issuer', 'date', 'profile']


class ProfileSerializer(serializers.ModelSerializer):
    certificates = CertificateSerializer(many=True)

    class Meta:
        model = Profile
        fields = ['full_name', 'email', 'certificates']

    def create(self, validated_data):
        certificates_data = validated_data.pop('certificates', [])
        profile = Profile.objects.create(**validated_data)
        for cert_data in certificates_data:
            cert_data.pop('profile', None)  # ✅ prevent duplicate profile
            Certificate.objects.create(profile=profile, **cert_data)
        return profile

    def update(self, instance, validated_data):
        certificates_data = validated_data.pop('certificates', None)

        # Update profile fields
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        if certificates_data is not None:
            # Map existing certificates by id for easy access
            existing_certs = {c.id: c for c in instance.certificates.all()}

            for cert_data in certificates_data:
                cert_data.pop('profile', None)  # ✅ remove profile if present
                cert_id = cert_data.pop("id", None)

                if cert_id and cert_id in existing_certs:
                    # Update existing certificate
                    cert = existing_certs[cert_id]
                    for attr, value in cert_data.items():
                        setattr(cert, attr, value)
                    cert.save()
                else:
                    # Create new certificate
                    Certificate.objects.create(profile=instance, **cert_data)

        return instance
