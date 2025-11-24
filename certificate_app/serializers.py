from rest_framework import serializers
from .models import Profile, Certificate

class CertificateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    profile = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Certificate
        fields = ['id', 'name', 'issuer', 'date', 'profile']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance



class ProfileSerializer(serializers.ModelSerializer):
    certificates = CertificateSerializer(many=True, required=False)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Profile
        fields = ['full_name', 'email', 'user', 'certificates']

    def update(self, instance, validated_data):
        certificates_data = validated_data.pop('certificates', None)

        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if certificates_data is not None:
            existing = {c.id: c for c in instance.certificates.all()}

            sent_ids = []

            for cert_data in certificates_data:
                cert_id = cert_data.get("id")

                if cert_id and cert_id in existing:
                    # update
                    cert = existing[cert_id]
                    for attr, value in cert_data.items():
                        setattr(cert, attr, value)
                    cert.save()
                    sent_ids.append(cert_id)
                else:
                    # create
                    new = Certificate.objects.create(profile=instance, **cert_data)
                    sent_ids.append(new.id)

            # delete removed certificates
            for cid, cert in existing.items():
                if cid not in sent_ids:
                    cert.delete()

        return instance
