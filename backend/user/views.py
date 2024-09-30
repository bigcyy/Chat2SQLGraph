from rest_framework.views import APIView
from rest_framework.decorators import action
from .serializers import LoginSerializer, RegisterSerializer
from common.response import result
from common.auth.authenticate import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema

class LoginView(APIView):
    @swagger_auto_schema(
        method='POST',
        operation_summary='登录',
        operation_description='成功返回token\n'
    )
    @action(methods=['POST'], detail=False)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        # 验证并获取token
        token = serializer.get_jwt_token()
        return result.success(data=token)
    
class TokenView(APIView):
    authentication_classes = [JWTAuthentication]
    @swagger_auto_schema(
        method='POST',
        operation_summary='刷新token',
        operation_description='成功返回token\n'
    )
    @action(methods=['POST'], detail=False)
    def post(self, request):
        serializer = LoginSerializer.Refresh(data={"user_id": request.user.id})
        # 刷新token
        token = serializer.refresh_jwt_token()
        return result.success(data=token)
    
class RegisterView(APIView):
    @swagger_auto_schema(
        method='POST',
        operation_summary='注册',
        operation_description='成功返回用户id\n'
    )
    @action(methods=['POST'], detail=False)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        id = serializer.save_user()
        return result.success(data=id)

class HelloView(APIView):
    authentication_classes = [JWTAuthentication]
    @swagger_auto_schema(
        method='GET',
        operation_summary='测试',
        operation_description='成功返回hello\n'
    )
    @action(methods=['GET'], detail=False)
    def get(self, request):
        return result.success(data="hello")

class UserView(APIView):
    authentication_classes = [JWTAuthentication]
    @swagger_auto_schema(
        method='GET',
        operation_summary='获取用户信息',
        operation_description='成功返回用户信息\n'
    )
    @action(methods=['GET'], detail=False)
    def get(self, request):
        user = request.auth
        return result.success(data=user)
