from rest_framework import serializers
from neuroglancer.models import UrlModel


class UrlSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = UrlModel
        fields = ['animal', 'url', 'user_date', 'comments']
        ordering = ['-created']


    def create(self, validated_data):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        urlModel = UrlModel(
            url=validated_data['url'],
            user_date=validated_data['user_date'],
            comments=validated_data['comments'],
            person=user
        )
        urlModel.save()
        return urlModel
