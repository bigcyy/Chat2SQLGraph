from django.urls import path

from . import views

app_name = "setting"
urlpatterns = [
    path('setting/provider', views.ProviderView.as_view(), name='provider'),
    path('setting/<str:provider>/model_list', views.ProviderView.ModelListView.as_view(), name='model_list'),
    path('setting/model', views.ModelView.as_view(), name='model'),
    path('setting/datasource', views.DatasourceView.as_view(), name='datasource'),
    path('setting/datasource/<int:datasource_id>/table_info', views.DatasourceView.TableInfoView.as_view(), name='table_info'),
]
