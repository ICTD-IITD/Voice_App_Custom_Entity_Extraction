from django.conf.urls import url
from vsurvey import views

urlpatterns = [
    url(r'est_conn/', views.establish_connection),
    url(r'get_entity/', views.get_entity),
    url(r'webhook/', views.test_api)
]