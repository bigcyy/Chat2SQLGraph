from rest_framework.authentication import TokenAuthentication
from common.auth.jwt_utils import is_valid_jwt_token
from common.auth.token_details import UserTokenDetails
from common.exceptions.exception import AppAuthenticationFailed


class AnonymousAuthentication(TokenAuthentication):
    def authenticate(self, request):
        return None, None
    

class JWTAuthentication(TokenAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Authorization')
        # 判断是否有token
        if not token:
            raise AppAuthenticationFailed()
        # 判断 token 是否合法
        if not is_valid_jwt_token(token):
            # 不合法或者已经过期
            raise AppAuthenticationFailed()
        # 使用权限处理器判断用户是否具备权限
        return UserTokenDetails(token).get_token_details()
        


