from rest_framework.views import APIView
from common.auth.authenticate import JWTAuthentication
from application.serializers import ApplicationSerializer
from drf_yasg.utils import swagger_auto_schema
from common.response import result
from rest_framework.decorators import action
# Create your views here.
class ApplicationView(APIView):
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        method='POST',
        operation_summary='创建应用',
        operation_description='成功返回应用 id\n',
        request_body=ApplicationSerializer.Create
    )
    @action(methods=['POST'], detail=False)
    def post(self, request):
        serializer = ApplicationSerializer.Create(data={**request.data, 'user_id': request.user.id})
        return result.success(serializer.save())
