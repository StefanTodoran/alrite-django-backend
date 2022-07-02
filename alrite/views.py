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