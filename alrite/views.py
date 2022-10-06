from django.shortcuts import render
from .serializers import *
from .models import *
from .forms import *
from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import make_password
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import authentication, permissions, status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
import json
from bs4 import BeautifulSoup as bs
from django.db.models import F
from django.db.models import Sum


# Create your views here.
class RegisterView(LoginRequiredMixin, CreateView):
    template_name = 'registration/register.html'
    form_class = CreateUser
    success_url = reverse_lazy('clinicians')

    def form_valid(self, form):
        # user = form.save(commit=False)
        first = form.cleaned_data['first_name']
        last = form.cleaned_data['last_name']
        healthy = form.cleaned_data['healthy_facility']
        password = form.cleaned_data['password']
        username = first + "_" + last

        clinician_code = CustomUser.objects.filter(healthy_facility=healthy)

        if clinician_code.exists():
            clinician_code = clinician_code.latest('date_joined').code
            new_code = int(clinician_code)
            new_code = new_code + 1
            code = "0" + str(new_code)
        else:
            code = "01"

        user = form.save(commit=False)
        user.username = username
        user.password = make_password(password)
        user.is_nurse = True
        user.code = code

        user.save()

        return super(RegisterView, self).form_valid(form)


@api_view(['POST'])
def login_api(request):
    serializer = AuthTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    token = Token.objects.get(user=user).key

    return Response({
        'user_info': {
            'code': user.code,
            'healthy_facility': user.healthy_facility.code
        },
        'token': token
    })


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):

        patient = Patient.objects.all()
        # Patient.objects.update(incomplete='complete')

        clinicians = CustomUser.objects.filter(is_nurse=True).count()
        forms = patient.count()
        complete = Patient.objects.filter(incomplete="complete").count()
        incomplete = Patient.objects.filter(incomplete="incomplete").count()
        severe = Patient.objects.filter(diagnosis_1__isnull=False).count()
        brochodilator = Patient.objects.filter(bronchodilator="Bronchodialtor Given")
        eligible = brochodilator.count()
        reassessed = brochodilator.filter(after_bronchodilator__isnull=False).count()

        # counter details
        app_opening = (Counter.objects.aggregate(Sum('app_opening_count')))['app_opening_count__sum']
        rr_counter = (Counter.objects.aggregate(Sum('rr_counter_count')))['rr_counter_count__sum']
        learn = (Counter.objects.aggregate(Sum('learn_opening_count')))['learn_opening_count__sum']
        active_users = Patient.objects.values('clinician').distinct().count()

        context = super(HomePageView, self).get_context_data(**kwargs)

        context.update({
            "patients": patient,
            "clinicians": clinicians,
            "forms": forms,
            "complete": complete,
            "incomplete": incomplete,
            "severe": severe,
            "eligible": eligible,
            "reassessed": reassessed,
            "app_opening": app_opening,
            "rr_counter": rr_counter,
            "learn": learn,
            "active_users": active_users,
        })

        return context


class CliniciansPageView(LoginRequiredMixin, TemplateView):
    template_name = 'clinicians.html'

    def get_context_data(self, **kwargs):

        clinicians = CustomUser.objects.filter(is_nurse=True)

        context = super(CliniciansPageView, self).get_context_data(**kwargs)

        context.update({
            "clinicians": clinicians,
        })

        return context


class AppUsageView(LoginRequiredMixin, TemplateView):
    template_name = "app_usage.html"


class SavePatientDataView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @csrf_exempt
    def post(self, request):

        file = request.FILES.get('patient')
        print(file)

        user = self.request.user

        bs_content = bs(file, 'lxml')
        list_ = list(bs_content.find('map').children)
        list_ = list(filter(lambda a: a != '\n', list_))

        myDict = {}
        for c in list_:
            myDict[c.get('name')] = c.text

        if "clinician" in myDict:
            username = myDict["clinician"]
            username = CustomUser.objects.get(username=username)
            if "incomplete" in myDict:
                incomplete = myDict['incomplete']
                if incomplete == "incomplete":
                    CustomUser.objects.filter(username=username)\
                        .update(forms=F("forms") + 1, incomplete_forms=F("incomplete_forms") + 1)
                    incomplete = "incomplete"
                else:
                    CustomUser.objects.filter(username=username) \
                        .update(forms=F("forms") + 1, completed_forms=F("completed_forms") + 1)
                    incomplete = "complete"
            else:
                incomplete = ""

        else:
            username = CustomUser.objects.get(username="chodrine")
            incomplete = ""

        popKey("diagnosis", myDict)
        popKey("oxDiagnosis", myDict)
        popKey("stDiagnosis", myDict)
        popKey("gnDiagnosis", myDict)
        popKey("gnDiagnosis", myDict)
        popKey("clinician", myDict)
        popKey("second", myDict)
        popKey("filename", myDict)
        popKey("final", myDict)
        popKey("study_id_2", myDict)
        popKey("reassess", myDict)
        popKey("pending", myDict)
        popKey("incomplete", myDict)

        Patient.objects.create(**myDict, clinician_2=user, clinician=username, incomplete=incomplete)

        return Response("Data saved successfully")


def popKey(key, dict):
    if key in dict:
        dict.pop(key)


class SaveCountDataView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @csrf_exempt
    def post(self, request):

        file = request.FILES.get('counter')
        # new changes

        user = self.request.user

        bs_content = bs(file, 'lxml')
        list_ = list(bs_content.find('map').children)
        list_ = list(filter(lambda a: a != '\n', list_))

        myDict = {}
        for c in list_:
            myDict[c.get('name')] = c.text

        Counter.objects.create(**myDict, clinician=user)

        return Response("Data saved successfully")



