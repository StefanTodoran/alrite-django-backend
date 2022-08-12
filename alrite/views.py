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
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
import json
from bs4 import BeautifulSoup as bs


# Create your views here.
class RegisterView(LoginRequiredMixin, CreateView):
    template_name = 'registration/register.html'
    form_class = CreateUser
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        user = form.save(commit=False)
        first = form.cleaned_data['first_name']
        last = form.cleaned_data['last_name']
        password = form.cleaned_data['password']
        username = first + "_" + last
        user.username = username
        user.password = make_password(password)
        user.save()
        return super(RegisterView, self).form_valid(form)


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):

        patient = Patient.objects.all()

        context = super(HomePageView, self).get_context_data(**kwargs)

        context.update({
            "patients": patient,
        })

        return context


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

        else:
            username = CustomUser.objects.get(username="chodrine")

        popKey("diagnosis", myDict)
        popKey("oxDiagnosis", myDict)
        popKey("stDiagnosis", myDict)
        popKey("gnDiagnosis", myDict)
        popKey("gnDiagnosis", myDict)
        popKey("clinician", myDict)

        Patient.objects.create(**myDict, clinician_2=user, clinician=username)

        return Response("Data saved successfully")


def popKey(key, dict):
    if key in dict:
        dict.pop(key)
