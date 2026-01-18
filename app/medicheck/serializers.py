"""
Serializers for medicheck APIs

"""

from rest_framework import serializers


from core.models import (
    Disease,
    Tag,
)

class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class DiseaseSerializer(serializers.ModelSerializer):
    """Serializer for disease"""
    tags = TagSerializer(many=True, required=False)


    class Meta:
        model = Disease
        fields = ['id', 'name', 'description', 'cause', 'symptoms', 'prevention', 'link', 'tags']
        read_only_fields = ['id']


    def _get_or_create_tags(self, tags, disease):
        """Handle getting or creating tags as needed"""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag
            )
            disease.tags.add(tag_obj)

    def create(self, validated_data):
        """Create a disease"""
        tags = validated_data.pop('tags', [])

        disease = Disease.objects.create(**validated_data)
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag
            )
            disease.tags.add(tag_obj)
        return disease

    def update(self, instance, validated_data):
        """Update a disease"""
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance



class DiseaseDetailSerializer(DiseaseSerializer):
    """Serializer for disease detail view"""

    class Meta(DiseaseSerializer.Meta):
        fields = DiseaseSerializer.Meta.fields + ['description']



