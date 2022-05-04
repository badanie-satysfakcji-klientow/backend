from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import SurveySerializer
from .models import Survey


class SurveysList(APIView):
    def get(self, request):
        surveys = Survey.objects.all()
        serializer = SurveySerializer(surveys, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SurveySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SurveyDetail(APIView):
    def get(self, request, pk):
        """
        # get survey by its id
        """
        survey = Survey.objects.get(pk=pk)
        serializer = SurveySerializer(survey)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        # update survey by its id
        """
        survey = Survey.objects.get(pk=pk)
        serializer = SurveySerializer(survey, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, pk):
        """
        # save survey answer by its id
        """
        survey = Survey.objects.get(pk=pk)
        survey.answers.append(request.data)
        survey.save()
        return Response(status=status.HTTP_201_CREATED)


class SurveyResults(APIView):
    def get(self, request, pk):
        """
        # get survey results by its id
        """
        survey = Survey.objects.get(pk=pk)
        serializer = SurveySerializer(survey)
        return Response(serializer.data)


class SendSurvey(APIView):
    def post(self, request):
        """
        # send survey by its id
        """
        survey = Survey.objects.get(pk=request.data['id'])
        survey.send()
        return Response(status=status.HTTP_201_CREATED)
