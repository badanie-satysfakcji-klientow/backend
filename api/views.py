from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['GET'])
def getSurveys(request):
    test_data = {'title':'Pierwsza ankieta', 'description':'Cool survey'}
    return Response(test_data)
