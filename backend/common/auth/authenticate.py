from rest_framework.authentication import TokenAuthentication
from common.auth.jwt_utils import is_valid_jwt_token, get_token_data
from common.auth.token_details import UserTokenDetails, ApplicationTokenDetails
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
        token_data = get_token_data(token)
        if token_data.get('type') == 'application':
            application_token,application_token_dict = ApplicationTokenDetails(token).get_token_details()
            if not application_token_dict.get('is_active'):
                raise AppAuthenticationFailed()
            if application_token_dict.get('white_active'):
                if request.get('ip') not in application_token.get('white_list'):
                    raise AppAuthenticationFailed()
            if application_token_dict.get('access_num') <= 0:
                raise AppAuthenticationFailed()
            return application_token, application_token_dict
        else:
            return UserTokenDetails(token).get_token_details()
        


