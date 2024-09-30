from abc import ABC, abstractmethod
from user.models import User
from django.db.models import QuerySet, Q
from .jwt_utils import get_object_id_by_token

class TokenDetails(ABC):
    token_details = None
    is_load = False

    def __init__(self, token: str):
        self.token = token

    def get_token_details(self):
        if self.token_details is None and not self.is_load:
            try:
                modle, self.token_details = self.load_token_details()
            except Exception as e:
                self.is_load = True
        return (modle, self.token_details)

    @abstractmethod
    def load_token_details(self):
        pass


class UserTokenDetails(TokenDetails):
    def load_token_details(self):
        # todo: 从缓存中查询用户信息
        # 从数据库中查询用户信息
        object_id = get_object_id_by_token(self.token)
        user = QuerySet(User).filter(Q(id = object_id)).first()
        return user,{
            "user_id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "role": user.role,
            "is_active": user.is_active,
            "create_time": user.create_time,
            "update_time": user.update_time,
        }

