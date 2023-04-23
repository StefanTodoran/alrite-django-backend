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

    # GET API endpoints for getting a workflow.
    # Workflows are identified by their id, a short unique string without spaces,
    # and their version, an integer than increases with changes.
    # With these endpoints you can request a workflow from its id and version.
    # if the version is not specified it defaults to the latest one.
    # The workflow is returned in json format. if the given id or version don't exist,
    # a 404 error is returned.
    path('apis/getWorkflow/<workflow_id>/', GetWorkflowView.as_view()),
    path('apis/getWorkflow/<workflow_id>/<int:version>/', GetWorkflowView.as_view()),

    # POST API endpoint to save a workflow to the given workflow_id. The version
    # is updated to the next available one, or 1 if this is the first workflow
    # under this id. The workflow should be stored as json in the post data
    # of the request. If invalid json is sent an error code is returned and the
    # workflow is not saved.
    # Authenication is needed to upload a workflow, and only admins will be allowed.
    path('apis/saveWorkflow/<workflow_id>/', SaveWorkflowView.as_view()),

    # GET API endpoint that returns a json list of all workflows, with their
    # id, version, time created and author
    path('apis/listWorkflows/', ListWorkflowsView.as_view()),

    #path('apis/download_data/', ExportCSVAPIView.as_view()),
    path('download_data/', ExportCSVView.as_view(), name="download")
]
