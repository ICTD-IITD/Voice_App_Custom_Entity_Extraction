from rest_framework import serializers

from .models import surveyUser, surveyQuestion

class userSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = surveyUser
        fields = ('ph_no', 'name', 'location')

class questionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = surveyQuestion
        fields = ('question_id', 'user', 'question', 'answer', 'audio')
