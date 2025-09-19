from rest_framework import serializers
from .models import Profile, Certificate


class CertificateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)  # allow existing certs to be updated

    class Meta:
        model = Certificate
        fields = ['id', 'name', 'issuer', 'date', 'profile']
        read_only_fields = ['id', 'profile']


class ProfileSerializer(serializers.ModelSerializer):
    certificates = CertificateSerializer(many=True)

    class Meta:
        model = Profile
        fields = ['full_name', 'email', 'certificates']

    def create(self, validated_data):
        certificates_data = validated_data.pop('certificates', [])
        profile = Profile.objects.create(**validated_data)
        for cert_data in certificates_data:
            Certificate.objects.create(profile=profile, **cert_data)
        return profile

    def update(self, instance, validated_data):
        certificates_data = validated_data.pop('certificates', None)

        # Update profile fields
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        if certificates_data is not None:
            existing_ids = [c.id for c in instance.certificates.all()]
            sent_ids = [c.get("id") for c in certificates_data if "id" in c]

            # Delete certificates that are missing in the request
            for cert in instance.certificates.all():
                if cert.id not in sent_ids:
                    cert.delete()

            # Update existing or create new certificates
            for cert_data in certificates_data:
                cert_id = cert_data.pop("id", None)
                if cert_id and cert_id in existing_ids:
                    cert = Certificate.objects.get(id=cert_id, profile=instance)
                    for attr, value in cert_data.items():
                        setattr(cert, attr, value)
                    cert.save()
                else:
                    Certificate.objects.create(profile=instance, **cert_data)

        return instance
