from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import SurveysSerializer
from .models import Surveys

# Create your views here.


@api_view(['GET', 'POST'])
def survey_list(request):
    """
    List all surveys or create a new survey.
    """
    if request.method == 'GET':
        surveys = Surveys.objects.all()
        serializer = SurveysSerializer(surveys, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = SurveysSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
