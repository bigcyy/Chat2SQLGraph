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

    class OperationView(APIView):
        authentication_classes = [JWTAuthentication]
        @swagger_auto_schema(
            method='PUT',
            operation_summary='更新应用',
            operation_description='成功返回应用详情\n',
            request_body=ApplicationSerializer.Update
        )
        @action(methods=['PUT'], detail=False)
        def put(self, request, application_id):
            serializer = ApplicationSerializer.Update(data={**request.data, 'id': application_id, 'user_id': request.user.id})
            return result.success(serializer.update())
        
        @swagger_auto_schema(
            method='DELETE',
            operation_summary='删除应用',
            operation_description='成功返回ok\n',
        )
        @action(methods=['DELETE'], detail=False)
        def delete(self, request, application_id):
            serializer = ApplicationSerializer.Delete(data={'id': application_id, 'user_id': request.user.id})
            serializer.delete()
            return result.success("ok")

        @swagger_auto_schema(
            method='GET',
            operation_summary='获取应用详情',
            operation_description='成功返回应用详情\n',
        )
        @action(methods=['GET'], detail=False)
        def get(self, request, application_id):
            serializer = ApplicationSerializer.Detail(data={'id': application_id, 'user_id': request.user.id})
            return result.success(serializer.detail())
        
    
