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
        request_body=ApplicationSerializer.ApplicationCreate
    )
    @action(methods=['POST'], detail=False)
    def post(self, request):
        serializer = ApplicationSerializer.ApplicationCreate(data={**request.data, 'user_id': request.user.id})
        return result.success(serializer.save())

    class OperationView(APIView):
        authentication_classes = [JWTAuthentication]
        @swagger_auto_schema(
            method='PUT',
            operation_summary='更新应用',
            operation_description='成功返回应用详情\n',
            request_body=ApplicationSerializer.ApplicationUpdate
        )
        @action(methods=['PUT'], detail=False)
        def put(self, request, application_id):
            serializer = ApplicationSerializer.ApplicationUpdate(data={**request.data, 'id': application_id, 'user_id': request.user.id})
            return result.success(serializer.update())
        
        @swagger_auto_schema(
            method='DELETE',
            operation_summary='删除应用',
            operation_description='成功返回ok\n',
            request_body=ApplicationSerializer.ApplicationDelete
        )
        @action(methods=['DELETE'], detail=False)
        def delete(self, request, application_id):
            serializer = ApplicationSerializer.ApplicationDelete(data={'id': application_id, 'user_id': request.user.id})
            serializer.delete()
            return result.success("ok")

        @swagger_auto_schema(
            method='GET',
            operation_summary='获取应用详情',
            operation_description='成功返回应用详情\n'
        )
        @action(methods=['GET'], detail=False)
        def get(self, request, application_id):
            serializer = ApplicationSerializer.ApplicationDetail(data={'id': application_id, 'user_id': request.user.id})
            return result.success(serializer.detail())
        
    
    class ChatView(APIView):
        authentication_classes = [JWTAuthentication]
        @swagger_auto_schema(
            method='POST',
            operation_summary='开始聊天',
            operation_description='成功返回 LLM SSE 回复\n',
            request_body=ApplicationSerializer.ApplicationChat
        )
        @action(methods=['POST'], detail=False)
        def post(self, request, application_id):
            serializer = ApplicationSerializer.ApplicationChat(data={**request.data, 'application_id': application_id})
            return serializer.chat();
