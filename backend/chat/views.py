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
        operation_summary='打开一个聊天会话',
        operation_description='成功返回聊天id\n',
        request_body=ChatSerializer.Open
    )
    @action(methods=['POST'], detail=False)
    def post(self, request, datasource_id):
            user_id = request.user.id
            serializer = ChatSerializer.Open(data={**request.data,"user_id":user_id,"datasource_id":datasource_id})
            id = serializer.chat()
            return result.success(str(id))

    @swagger_auto_schema(
        method='GET',
        operation_summary='获取所有聊天列表',
        operation_description='成功返回所有聊天列表\n',
        query_serializer=ChatSerializer.Query
    )
    @action(methods=['GET'], detail=False)
    def get(self, request, datasource_id):
            serializer = ChatSerializer.Query(data={**request.data,"datasource_id":datasource_id,"user_id":request.user.id})
            ans = serializer.list()
            return result.success(ans)

    @swagger_auto_schema(
        method='DELETE',
        operation_summary='删除聊天',
        operation_description='成功返回ok\n',
        request_body=ChatSerializer.Delete
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
            operation_description='结果为流式传输\n',
            request_body=ChatMessageSerializer.Start
        )
        @action(methods=['POST'], detail=False)
        def post(self, request, datasource_id, chat_id):
            user_id = request.user.id
            serializer = ChatMessageSerializer.Start(data={**request.data,"user_id":user_id,"datasource_id":datasource_id,"chat_id":chat_id})
            return serializer.chat()
        
        @swagger_auto_schema(
            method='GET',
            operation_summary='获取单条消息详情',
            operation_description='成功返回消息详情\n',
            query_serializer=ChatMessageSerializer.QueryOne
        )
        @action(methods=['GET'], detail=False)
        def get(self, request, datasource_id, chat_id):
            serializer = ChatMessageSerializer.QueryOne(data={**request.data,"datasource_id":datasource_id,"chat_id":chat_id, "user_id":request.user.id})
            return result.success(serializer.one())    


    
        class DemandView(APIView):

            authentication_classes = [JWTAuthentication]
            @swagger_auto_schema(
                method='PUT',
                operation_summary='修改demand重新聊天',
                operation_description='结果为流式传输\n',
                request_body=ChatMessageSerializer.UpdateDemand
            )
            @action(methods=['PUT'], detail=False)
            def put(self, request, datasource_id, chat_id):
                serializer = ChatMessageSerializer.UpdateDemand(data={**request.data,"datasource_id":datasource_id,"chat_id":chat_id, "user_id":request.user.id})
                return serializer.update()

        class SqlView(APIView):

            authentication_classes = [JWTAuthentication]
            @swagger_auto_schema(
                method='PUT',
                operation_summary='修改sql重新聊天',
                operation_description='结果为流式传输\n',
                request_body=ChatMessageSerializer.UpdateSql
            )
            @action(methods=['PUT'], detail=False)
            def put(self, request, datasource_id, chat_id):
                serializer = ChatMessageSerializer.UpdateSql(data={**request.data,"datasource_id":datasource_id,"chat_id":chat_id, "user_id":request.user.id})
                return serializer.update()

        class TablesView(APIView):

            authentication_classes = [JWTAuthentication]
            @swagger_auto_schema(
                method='PUT',
                operation_summary='修改tables重新聊天',
                operation_description='结果为流式传输\n',
                request_body=ChatMessageSerializer.UpdateTables
            )
            @action(methods=['PUT'], detail=False)
            def put(self, request, datasource_id, chat_id):
                serializer = ChatMessageSerializer.UpdateTables(data={**request.data,"datasource_id":datasource_id,"chat_id":chat_id, "user_id":request.user.id})
                return serializer.update()

