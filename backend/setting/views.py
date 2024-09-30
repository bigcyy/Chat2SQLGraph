from rest_framework.views import APIView
from rest_framework.decorators import action
from .serializers import ModelSerializer, DatasourceSerializer, TableInfoSerializer
from common.response import result
from common.providers.model_provider_constants import ModelProviderConstants
from common.auth.authenticate import JWTAuthentication
from common.utils.utils import query_params_to_single_dict
from .serializers import RemoteTableInfoSerializer
from drf_yasg.utils import swagger_auto_schema
# Create your views here.


class ModelView(APIView):

    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        method='POST',
        operation_summary='添加模型',
        operation_description='成功返回模型id\n',
        request_body=ModelSerializer.Add
    )
    @action(methods=['POST'], detail=False)
    def post(self, request):
        serializer = ModelSerializer.Add(data={**request.data, 'user_id': request.user.id})
        id = serializer.add_model()
        return result.success(id)

    @swagger_auto_schema(
        method='GET',
        operation_summary='获取保存的模型列表',
        operation_description='成功返回保存的模型列表\n',
        query_serializer=ModelSerializer.Query
    )
    @action(methods=['GET'], detail=False)
    def get(self, request):
        user_id = request.user.id
        models = ModelSerializer.Query(
                data={**query_params_to_single_dict(request.query_params),'user_id': user_id}).list(with_valid=True)
        return result.success(models)
    
    @swagger_auto_schema(
        method='DELETE',
        operation_summary='删除模型',
        operation_description='成功返回ok\n',
        request_body=ModelSerializer.Remove
    )
    @action(methods=['DELETE'], detail=False)
    def delete(self, request):
        serializer = ModelSerializer.Remove(data={**request.data, 'user_id': request.user.id})
        serializer.delete_model()
        return result.success("ok")


class ProviderView(APIView):
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        method='GET',
        operation_summary='获取模型提供者列表',
        operation_description='成功返回模型提供者列表\n',
        query_serializer=ModelSerializer.Query
    ) 
    @action(methods=['GET'], detail=False)
    def get(self, request):
        return result.success([
            provider.value.get_model_provider_info().to_dict() for provider in ModelProviderConstants
        ])

    class ModelListView(APIView):
        authentication_classes = [JWTAuthentication]

        @swagger_auto_schema(
            method='GET',
            operation_summary='获取模型列表',
            operation_description='成功返回模型列表\n',
            query_serializer=ModelSerializer.Query
        )
        @action(methods=['GET'], detail=False)
        def get(self, request, provider:str):
            provider = ModelProviderConstants[provider]
            model_info_manager = provider.value.get_model_info_manager()
            model_list = model_info_manager.get_model_list()
            return result.success([model.to_dict() for model in model_list])


class DatasourceView(APIView):
    authentication_classes = [JWTAuthentication]

    
    @swagger_auto_schema(
        method='POST',
        operation_summary='添加数据源',
        operation_description='成功返回数据源id\n',
        request_body=DatasourceSerializer.AddDatasource
    )
    @action(methods=['POST'], detail=False)
    def post(self, request):
        serializer = DatasourceSerializer.AddDatasource(data={**request.data, 'user_id': request.user.id})
        id = serializer.add_datasource()
        return result.success(id)
    
    
    @swagger_auto_schema(
        method='GET',
        operation_summary='获取数据源列表',
        operation_description='成功返回数据源列表\n',
        query_serializer=DatasourceSerializer.Query
    )
    @action(methods=['GET'], detail=False)
    def get(self, request):
        serializer = DatasourceSerializer.Query(data={**query_params_to_single_dict(request.query_params),'user_id': request.user.id})
        datasources = serializer.query_datasource()
        return result.success(datasources)

    @swagger_auto_schema(
        method='DELETE',
        operation_summary='删除数据源',
        operation_description='成功返回ok\n',
        request_body=DatasourceSerializer.DeleteDatasource
    )
    @action(methods=['DELETE'], detail=False)
    def delete(self, request):
        serializer = DatasourceSerializer.DeleteDatasource(data={**request.data, 'user_id': request.user.id})
        serializer.delete_datasource()
        return result.success("ok")

    class TableInfoView(APIView):
        authentication_classes = [JWTAuthentication]

        @swagger_auto_schema(
            method='GET',
            operation_summary='获取表信息列表',
            operation_description='成功返回表信息列表\n',
            query_serializer=TableInfoSerializer.Query
        )
        @action(methods=['GET'], detail=False)
        def get(self, request, datasource_id:int):
            serializer = TableInfoSerializer.Query(data={**request.data, 'datasource_id': datasource_id, 'user_id': request.user.id})
            table_infos = serializer.query_table_info()
            return result.success(table_infos)

        @swagger_auto_schema(
            method='POST',
            operation_summary='添加表信息',
            operation_description='成功返回ok\n',
            request_body=TableInfoSerializer.Create
        )
        @action(methods=['POST'], detail=False)
        def post(self, request, datasource_id:int):
            
            # start_time = time.time()
            serializer = TableInfoSerializer.Create(data={**request.data, 'datasource_id': datasource_id, 'user_id': request.user.id})
            # asyncio.run(serializer.async_save_table_info())
            # asyncio.run(serializer.test())
            serializer.multi_thread_save()
            # serializer.save_table_info()
            # end_time = time.time()
            return result.success("ok")

        @swagger_auto_schema(
            method='DELETE',
            operation_summary='删除表信息',
            operation_description='成功返回ok\n',
            request_body=TableInfoSerializer.DeleteTable
        )
        @action(methods=['DELETE'], detail=False)
        def delete(self, request, datasource_id:int):
            serializer = TableInfoSerializer.DeleteTable(data={**request.data, 'datasource_id': datasource_id, 'user_id': request.user.id})
            serializer.delete_table_info()
            return result.success("ok")

    class RemoteTableInfoView(APIView):
        authentication_classes = [JWTAuthentication]

        @swagger_auto_schema(
            method='GET',
            operation_summary='获取远程表信息列表',
            operation_description='成功返回远程表信息列表\n',
            query_serializer=RemoteTableInfoSerializer.Query
        )
        @action(methods=['GET'], detail=False)
        def get(self, request, datasource_id:int):
            serializer = RemoteTableInfoSerializer.Query(data={**request.data, 'datasource_id': datasource_id, 'user_id': request.user.id})
            table_infos = serializer.query_table_info()
            return result.success(table_infos)
