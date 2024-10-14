from rest_framework import serializers
from common.response.field_response import ErrMessage
from common.exceptions.exception import ExceptionCodeConstants
from setting.models.datasource import Datasource
from setting.models.model import Model
from application.models import Application, ApplicationAccessToken
from user.models import User
import hashlib
import uuid

class ApplicationSerializer(serializers.Serializer):
    class Create(serializers.Serializer):
        name = serializers.CharField(required=True,min_length=1,max_length=255,error_messages=ErrMessage.char("应用名称"))
        description = serializers.CharField(required=False,allow_blank=True,max_length=1000,error_messages=ErrMessage.char("应用描述"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("用户 id"))
        model_id = serializers.IntegerField(required=False,error_messages=ErrMessage.char("模型 id"))
        datasource_id = serializers.IntegerField(required=False,error_messages=ErrMessage.char("数据源 id"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if self.data.get('datasource_id') is not None :
                datasource = Datasource.objects.filter(id=self.data.get('datasource_id'),created_by=self.data.get('user_id')).first()
                if not datasource:
                    raise ExceptionCodeConstants.DATASOURCE_NOT_EXIST.value.to_app_api_exception()
            if self.data.get('model_id') is not None:
                model = Model.objects.filter(id=self.data.get('model_id'),created_by=self.data.get('user_id')).first()
                if not model:
                    raise ExceptionCodeConstants.MODEL_NOT_EXIST.value.to_app_api_exception()

        def save(self):
            self.is_valid(raise_exception=True)
            creator = User(id=self.data.get('user_id'))
            model = Model(id=self.data.get('model_id')) if self.data.get('model_id') is not None else None
            datasource = Datasource(id=self.data.get('datasource_id')) if self.data.get('datasource_id') is not None else None
            # 创建应用
            application = Application.objects.create(name=self.data['name'],description=self.data.get('description'),creator=creator,model=model,datasource=datasource)
            # 创建应用认证 token
            ApplicationAccessToken.objects.create(application=application,access_token=hashlib.md5(str(uuid.uuid1()).encode()).hexdigest()[8:24])                                          
            return ApplicationSerializerModel(application).data
    class Update(serializers.Serializer):
        id = serializers.CharField(required=True,error_messages=ErrMessage.char("应用 id"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("用户 id"))
        name = serializers.CharField(required=True,min_length=1,max_length=255,error_messages=ErrMessage.char("应用名称"))
        description = serializers.CharField(required=True,allow_blank=True,allow_null=True,max_length=1000,error_messages=ErrMessage.char("应用描述"))
        model = serializers.IntegerField(required=True,allow_null=True,error_messages=ErrMessage.char("模型 id"))
        datasource = serializers.IntegerField(required=True,allow_null=True,error_messages=ErrMessage.char("数据源 id"))
        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            application = Application.objects.filter(id=self.data.get('id'),creator=self.data.get('user_id')).first()
            if not application:
                raise ExceptionCodeConstants.APPLICATION_NOT_EXIST.value.to_app_api_exception()
            if self.data.get('datasource') is not None :
                datasource = Datasource.objects.filter(id=self.data.get('datasource'),created_by=self.data.get('user_id')).first()
                if not datasource:
                    raise ExceptionCodeConstants.DATASOURCE_NOT_EXIST.value.to_app_api_exception()
            if self.data.get('model') is not None:
                model = Model.objects.filter(id=self.data.get('model'),created_by=self.data.get('user_id')).first()
                if not model:
                    raise ExceptionCodeConstants.MODEL_NOT_EXIST.value.to_app_api_exception()

        def update(self):
            self.is_valid(raise_exception=True)
            application = Application.objects.filter(id=self.data.get('id'),creator=self.data.get('user_id')).first()
            application.name = self.data.get('name')
            application.description = self.data.get('description')
            application.model = Model(id=self.data.get('model')) if self.data.get('model') is not None else None
            application.datasource = Datasource(id=self.data.get('datasource')) if self.data.get('datasource') is not None else None
            application.save()
            return ApplicationSerializerModel(application).data
    
    class Delete(serializers.Serializer):
        id = serializers.CharField(required=True,error_messages=ErrMessage.char("应用 id"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("用户 id"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            application = Application.objects.filter(id=self.data.get('id'),creator=self.data.get('user_id')).first()
            if not application:
                raise ExceptionCodeConstants.APPLICATION_NOT_EXIST.value.to_app_api_exception()

        def delete(self):
            self.is_valid(raise_exception=True)
            application = Application.objects.filter(id=self.data.get('id'),creator=self.data.get('user_id')).first()
            application.delete()
            return True
    
    class Detail(serializers.Serializer):
        id = serializers.CharField(required=True,error_messages=ErrMessage.char("应用 id"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("用户 id"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            application = Application.objects.filter(id=self.data.get('id'),creator=self.data.get('user_id')).first()
            if not application:
                raise ExceptionCodeConstants.APPLICATION_NOT_EXIST.value.to_app_api_exception()

        def detail(self):
            self.is_valid(raise_exception=True)
            application = Application.objects.filter(id=self.data.get('id'),creator=self.data.get('user_id')).first()
            return ApplicationSerializerModel(application).data
        
class ApplicationSerializerModel(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = "__all__"
