from django.template.defaulttags import url
from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    # path('register/', registration_view),
    # new changes
    # path('apis/login/', obtain_auth_token),
    path('apis/login/', login_api),
    path('registration/', RegisterView.as_view(), name='register'),
    path('clinicians/', CliniciansPageView.as_view(), name='clinicians'),
    path('app_usage/', AppUsageView.as_view(), name='app_usage'),
    path('apis/saveData/', SavePatientDataView.as_view()),
    path('apis/saveCounter/', SaveCountDataView.as_view()),
    path('apis/getWorkflow/<workflow_id>/', GetWorkflowView.as_view()),
    path('apis/getWorkflow/<workflow_id>/<int:version>/', GetWorkflowView.as_view()),
    path('apis/saveWorkflow/', SaveWorkflowView.as_view()),
    path('apis/download_data/', ExportCSVAPIView.as_view()),
    path('download_data/', ExportCSVView.as_view(), name="download")
]
