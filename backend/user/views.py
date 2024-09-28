from rest_framework.views import APIView
from rest_framework.decorators import action
from .serializers import LoginSerializer, RegisterSerializer
from common.response import result
from common.auth.authenticate import JWTAuthentication

class LoginView(APIView):
    @action(methods=['POST'], detail=False)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        # 验证并获取token
        token = serializer.get_jwt_token()
        return result.success(data=token)
    
class TokenView(APIView):
    authentication_classes = [JWTAuthentication]
    @action(methods=['POST'], detail=False)
    def post(self, request):
        serializer = LoginSerializer.Refresh(data={"user_id": request.user.id})
        # 刷新token
        token = serializer.refresh_jwt_token()
        return result.success(data=token)
class RegisterView(APIView):
    @action(methods=['POST'], detail=False)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save_user()
        return result.success("xx")

class HelloView(APIView):
    authentication_classes = [JWTAuthentication]
    @action(methods=['GET'], detail=False)
    def get(self, request):
        return result.success(data="hello")

