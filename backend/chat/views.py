from rest_framework.views import APIView

from common.auth.authenticate import JWTAuthentication
from common.response import result
from .serializers import ChatSerializer,ChatMessageSerializer
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
# Create your views here.
class ChatView(APIView):
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        method='POST',
        operation_summary='创建聊天',
        operation_description='成功返回聊天id\n'
    )
    @action(methods=['POST'], detail=False)
    def post(self, request, datasource_id):
            user_id = request.user.id
            serializer = ChatSerializer.Create(data={**request.data,"user_id":user_id,"datasource_id":datasource_id})
            id = serializer.chat()
            return result.success(str(id))

    @swagger_auto_schema(
        method='GET',
        operation_summary='获取所有聊天列表',
        operation_description='成功返回所有聊天列表\n'
    )
    @action(methods=['GET'], detail=False)
    def get(self, request, datasource_id):
            serializer = ChatSerializer.Query(data={**request.data,"datasource_id":datasource_id,"user_id":request.user.id})
            ans = serializer.list()
            return result.success(ans)

    @swagger_auto_schema(
        method='DELETE',
        operation_summary='删除聊天',
        operation_description='成功返回ok\n'
    )
    @action(methods=['DELETE'], detail=False)
    def delete(self, request, datasource_id):
        serializer = ChatSerializer.Delete(data={**request.data,"datasource_id":datasource_id,"user_id":request.user.id})
        serializer.delete()
        return result.success("ok")
    
    class MessageView(APIView): 

        authentication_classes = [JWTAuthentication]

        @swagger_auto_schema(
            method='POST',
            operation_summary='开始聊天',
            operation_description='结果为流式传输\n'
        )
        @action(methods=['POST'], detail=False)
        def post(self, request, datasource_id, chat_id):
            user_id = request.user.id
            serializer = ChatMessageSerializer.Create(data={**request.data,"user_id":user_id,"datasource_id":datasource_id,"chat_id":chat_id})
            return serializer.chat()
        
        @swagger_auto_schema(
            method='GET',
            operation_summary='获取单条消息详情',
            operation_description='成功返回消息详情\n'
        )
        @action(methods=['GET'], detail=False)
        def get(self, request, datasource_id, chat_id):
            serializer = ChatMessageSerializer.Query(data={**request.data,"datasource_id":datasource_id,"chat_id":chat_id, "user_id":request.user.id})
            return result.success(serializer.list())    


        @swagger_auto_schema(
            method='PUT',
            operation_summary='重新聊天',
            operation_description='结果为流式传输\n'
        )
        @action(methods=['PUT'], detail=False)
        def put(self, request, datasource_id, chat_id):
            serializer = ChatMessageSerializer.Update(data={**request.data,"datasource_id":datasource_id,"chat_id":chat_id, "user_id":request.user.id})
            return serializer.update()

