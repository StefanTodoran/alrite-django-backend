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
    path('', DashboardView.as_view(), name='dashboard'),
    path('workflows', WorkflowsView.as_view(), name='workflows'),
    path('workflows/<workflow_id>', WorkflowInfoView.as_view(), name='workflow-page'),
    path('workflows/<workflow_id>/<int:version>', WorkflowInfoView.as_view(), name='workflow-page-version'),

    path('apis/login/', login_api),
    path('registration/', RegisterView.as_view(), name='register'),
    path('clinicians/', CliniciansPageView.as_view(), name='clinicians'),
    path('app_usage/', AppUsageView.as_view(), name='app_usage'),
    path('apis/saveData/', SavePatientDataView.as_view()),
    path('apis/saveCounter/', SaveCountDataView.as_view()),

    # API endpoints for getting and saving a workflow.
    # Workflows are identified by their id, a short unique string without spaces or capitals.
    # Different versions of workflows are stored using version numbers, starting at 1 and
    # increasing as changes are made.
    # 
    # To get a workflow, make a GET request to one of the urls below, specifying the id
    # and possibly the version, which defaults to the latest one.
    # On success the json of the workflow is returned
    # If the workflow doesn't exist, a 404 error is returned
    # 
    # To save a workflow, make a POST request to one of the urls below, with the body
    # being the workflow as json. When saving a new version is created with the given
    # workflow. If invalid json is passed in an 400 error is returned.
    # 
    # A GET request to the 'workflows/' directiory will return a json list of
    # all of the workflows with their id, version, creation time and author.
    path('apis/workflows/<workflow_id>', WorkflowAPIView.as_view()),
    path('apis/workflows/<workflow_id>/<int:version>', WorkflowAPIView.as_view()),
    path('apis/workflows/<workflow_id>/preview', WorkflowAPIView.as_view(), {"preview": True}),
    path('apis/workflows', ListWorkflowsView.as_view()),

    #path('apis/download_data/', ExportCSVAPIView.as_view()),
    path('download_data/', ExportCSVView.as_view(), name="download")
]
