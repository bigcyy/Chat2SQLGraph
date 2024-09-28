from rest_framework.views import APIView

from common.auth.authenticate import JWTAuthentication
from common.response import result
from .serializers import ChatSerializer,ChatMessageSerializer
from rest_framework.decorators import action
    
# Create your views here.
class ChatView(APIView):
    authentication_classes = [JWTAuthentication]

    @action(methods=['POST'], detail=False)
    def post(self, request, datasource_id):
            user_id = request.user.id
            serializer = ChatSerializer.Create(data={**request.data,"user_id":user_id,"datasource_id":datasource_id})
            id = serializer.chat()
            return result.success(str(id))
    
    @action(methods=['GET'], detail=False)
    def get(self, request, datasource_id):
            serializer = ChatSerializer.Query(data={**request.data,"datasource_id":datasource_id,"user_id":request.user.id})
            ans = serializer.list()
            return result.success(ans)


    class MessageView(APIView): 

        authentication_classes = [JWTAuthentication]

        @action(methods=['POST'], detail=False)
        def post(self, request, datasource_id, chat_id):
            user_id = request.user.id
            serializer = ChatMessageSerializer.Create(data={**request.data,"user_id":user_id,"datasource_id":datasource_id,"chat_id":chat_id})
            return serializer.chat()
        
        @action(methods=['GET'], detail=False)
        def get(self, request, datasource_id, chat_id):
            serializer = ChatMessageSerializer.Query(data={**request.data,"datasource_id":datasource_id,"chat_id":chat_id, "user_id":request.user.id})
            return result.success(serializer.list())    

        @action(methods=['PUT'], detail=False)
        def put(self, request, datasource_id, chat_id):
            serializer = ChatMessageSerializer.Update(data={**request.data,"datasource_id":datasource_id,"chat_id":chat_id, "user_id":request.user.id})
            return serializer.update()

