from rest_framework.views import APIView
from rest_framework.response import Response

class HomeView(APIView):
    def get(self, request):
        return Response({
            'message': 'Welcome to Compass News API',
            'version': '1.0.0',
            'endpoints': {
                'admin': '/admin/',
                'articles': '/api/v1/articles/',
                'accounts': '/api/v1/accounts/',
                'schema': '/api/schema/',
                'docs': '/api/docs/',
                'redoc': '/api/redoc/',
            }
        })
