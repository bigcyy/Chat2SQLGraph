from rest_framework.views import APIView
from rest_framework.decorators import action
from .serializers import ModelSerializer, DatasourceSerializer, TableInfoSerializer
from common.response import result
from common.providers.model_provider_constants import ModelProviderConstants
from common.auth.authenticate import JWTAuthentication
from common.utils.utils import query_params_to_single_dict

# Create your views here.


class ModelView(APIView):

    authentication_classes = [JWTAuthentication]

    @action(methods=['POST'], detail=False)
    def post(self, request):
        serializer = ModelSerializer.Create(data={**request.data, 'user_id': request.user.id})
        id = serializer.save_model()
        return result.success(id)

    @action(methods=['GET'], detail=False)
    def get(self, request):
        user_id = request.user.id
        models = ModelSerializer.Query(
                data={**query_params_to_single_dict(request.query_params),'user_id': user_id}).list(with_valid=True)
        return result.success(models)
    
    @action(methods=['DELETE'], detail=False)
    def delete(self, request):
        serializer = ModelSerializer.Delete(data={**request.data, 'user_id': request.user.id})
        serializer.delete_model()
        return result.success("ok")


class ProviderView(APIView):
    authentication_classes = [JWTAuthentication]

    @action(methods=['GET'], detail=False)
    def get(self, request):
        return result.success([
            provider.value.get_model_provider_info().to_dict() for provider in ModelProviderConstants
        ])

    class ModelListView(APIView):
        authentication_classes = [JWTAuthentication]

        @action(methods=['GET'], detail=False)
        def get(self, request, provider:str):
            provider = ModelProviderConstants[provider]
            model_info_manager = provider.value.get_model_info_manager()
            model_list = model_info_manager.get_model_list()
            return result.success([model.to_dict() for model in model_list])


class DatasourceView(APIView):
    authentication_classes = [JWTAuthentication]

    @action(methods=['POST'], detail=False)
    def post(self, request):
        serializer = DatasourceSerializer.Create(data={**request.data, 'user_id': request.user.id})
        id = serializer.save_datasource()
        return result.success(id)
    
    @action(methods=['GET'], detail=False)
    def get(self, request):
        serializer = DatasourceSerializer.Query(data={**query_params_to_single_dict(request.query_params),'user_id': request.user.id})
        datasources = serializer.query_datasource()
        return result.success(datasources)

    @action(methods=['DELETE'], detail=False)
    def delete(self, request):
        serializer = DatasourceSerializer.Delete(data={**request.data, 'user_id': request.user.id})
        serializer.delete_datasource()
        return result.success("ok")

    class TableInfoView(APIView):
        authentication_classes = [JWTAuthentication]

        @action(methods=['GET'], detail=False)
        def get(self, request, datasource_id:int):
            serializer = TableInfoSerializer.Query(data={**request.data, 'datasource_id': datasource_id, 'user_id': request.user.id})
            table_infos = serializer.query_table_info()
            return result.success(table_infos)

        @action(methods=['POST'], detail=False)
        def post(self, request, datasource_id:int):
            serializer = TableInfoSerializer.Create(data={**request.data, 'datasource_id': datasource_id, 'user_id': request.user.id})
            id = serializer.save_table_info()
            return result.success(id)

        @action(methods=['DELETE'], detail=False)
        def delete(self, request, datasource_id:int):
            serializer = TableInfoSerializer.Delete(data={**request.data, 'datasource_id': datasource_id, 'user_id': request.user.id})
            serializer.delete_table_info()
            return result.success("ok")

