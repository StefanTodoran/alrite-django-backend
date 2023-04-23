import csv
import datetime
from datetime import timedelta, datetime
import codecs

from django.shortcuts import render
from .serializers import *
from .models import *
from .forms import *
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import make_password
import rest_framework
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
from django.db.models import F, Count
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

    study_id = Patient.objects.filter(clinician=user).values('study_id')
    study_id = list(study_id)

    if len(study_id) == 0:
        st = 1
    else:
        li = []
        for i in study_id:
            if i['study_id'].startswith('AL'):
                last = i['study_id'][-2:]
                li.append(last)
        st = int(max(li)) + 1

    return Response({
        'user_info': {
            'code': user.code,
            'healthy_facility': user.healthy_facility.code,
            'study_id': st
        },
        'token': token
    })


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):

        # patient = Patient.objects.all()
        my_list = patients_data("none", "none", 20)

        context = super(HomePageView, self).get_context_data(**kwargs)

        context.update({
            "data": my_list
        })

        return context

    def post(self, request):
        if request.method == 'POST':
            if request.POST.get('action') == "date-filter":
                day1 = request.POST.get('day1')
                day2 = request.POST.get('day2')

                my_list = patients_data(day1, day2, 1)

                my_context = {
                    "data": my_list,
                }

            elif request.POST.get('action') == "date-reset":
                my_list = patients_data("none", "none", 20)

                my_context = {
                    "data": my_list,
                }

            else:
                health = request.POST.get('health')
                data = request.FILES.get('data')
                name = request.POST.get('name')

                json_data = json.load(data)

                my_list = sort_function(health, json_data, name)

                my_context = {
                    "data": my_list,
                }

            return HttpResponse(json.dumps(my_context, indent=4, sort_keys=True, default=str),
                                content_type='application/json')


def sort_function(value, data, key):
    print(data)
    key_val_list = [value]
    expected_result = [d for d in data if d[key] in key_val_list]
    print(expected_result)
    return expected_result


def get_data(date1, date2, value):
    if date1 == "none" and date2 == "none":
        if value == 20:
            patients = Patient.objects.order_by('-end_date')[:value].values('age2', 'weight', 'muac', 'symptoms', 'difficulty_breathing', 'days_with_breathing_difficulties',
                        'temperature', 'blood_oxygen_saturation', 'respiratory_rate', 'stridor', 'nasal_flaring',
                        'wheezing', 'chest_indrawing', 'duration', 'clinician__healthy_facility__name', 'gender',
                        'diagnosis_1', 'diagnosis_2', 'diagnosis_3', 'diagnosis_4', 'diagnosis_5', 'diagnosis_6',
                        'diagnosis_7', 'diagnosis_8', 'diagnosis_9', 'diagnosis_10', 'diagnosis_11', 'hiv_status',
                        'breathing_rate')
        else:
            patients = Patient.objects.all() \
                .values('age2', 'weight', 'muac', 'symptoms', 'difficulty_breathing', 'days_with_breathing_difficulties',
                        'temperature', 'blood_oxygen_saturation', 'respiratory_rate', 'stridor', 'nasal_flaring',
                        'wheezing', 'chest_indrawing', 'duration', 'clinician__healthy_facility__name', 'gender',
                        'diagnosis_1', 'diagnosis_2', 'diagnosis_3', 'diagnosis_4', 'diagnosis_5', 'diagnosis_6',
                        'diagnosis_7', 'diagnosis_8', 'diagnosis_9', 'diagnosis_10', 'diagnosis_11', 'hiv_status',
                        'breathing_rate')
    else:
        patients = Patient.objects.filter(end_date__gte=date1, end_date__lte=date2) \
            .values('age2', 'weight', 'muac', 'symptoms', 'difficulty_breathing',
                    'days_with_breathing_difficulties', 'temperature', 'blood_oxygen_saturation',
                    'respiratory_rate', 'stridor', 'nasal_flaring', 'wheezing', 'chest_indrawing', 'duration',
                    'clinician__healthy_facility__name', 'gender', 'diagnosis_1', 'diagnosis_2', 'diagnosis_3',
                    'diagnosis_4', 'diagnosis_5', 'diagnosis_6', 'diagnosis_7', 'diagnosis_8', 'diagnosis_9',
                    'diagnosis_10', 'diagnosis_11', 'hiv_status', 'breathing_rate')

    patients = list(patients)
    for i in patients:
        for k, v in i.items():
            if v is None:
                i[k] = "none"

    return patients


def patients_data(date1, date2, value):
    if date1 == "none" and date2 == "none":
        patients = get_data(date1, date2, value)

        clinicians = CustomUser.objects.filter(is_nurse=True).count()
        forms = Patient.objects.all().count()
        complete = Patient.objects.filter(incomplete="complete").count()
        severe = Patient.objects.filter(diagnosis_1="Severe Pneumonia OR very Severe Disease").count()
        brochodilator = Patient.objects.filter(bronchodilator="Bronchodialtor Given")
        eligible = brochodilator.count()
        reassessed = brochodilator.filter(after_bronchodilator__isnull=False).count()

        # counter details
        app_opening = (Counter.objects.aggregate(Sum('app_opening_count')))['app_opening_count__sum']
        rr_counter = (Counter.objects.aggregate(Sum('rr_counter_count')))['rr_counter_count__sum']
        learn = (Counter.objects.aggregate(Sum('learn_opening_count')))['learn_opening_count__sum']
        active_users = Patient.objects.values('clinician').distinct().count()

    else:
        patients = get_data(date1, date2, value)
        pat = Patient.objects.filter(end_date__gte=date1, end_date__lte=date2)
        clinicians = CustomUser.objects.filter(is_nurse=True).count()
        forms = pat.count()
        complete = pat.filter(incomplete="complete").count()
        severe = pat.filter(diagnosis_1="Severe Pneumonia OR very Severe Disease").count()
        brochodilator = pat.filter(bronchodilator="Bronchodialtor Given")
        eligible = brochodilator.count()
        reassessed = brochodilator.filter(after_bronchodilator__isnull=False).count()

        # counter details
        counter = Counter.objects.filter(date__gte=date1, date__lte=date2)
        app_opening = (counter.aggregate(Sum('app_opening_count')))['app_opening_count__sum']
        app_opening = value_none(app_opening)
        rr_counter = (counter.aggregate(Sum('rr_counter_count')))['rr_counter_count__sum']
        rr_counter = value_none(rr_counter)
        learn = (counter.aggregate(Sum('learn_opening_count')))['learn_opening_count__sum']
        learn = value_none(learn)
        active_users = pat.values('clinician').distinct().count()

    my_list = {
        "patients": patients,
        "clinicians": clinicians,
        "forms": forms,
        "complete": complete,
        "severe": severe,
        "eligible": eligible,
        "reassessed": reassessed,
        "app_opening": app_opening,
        "rr_counter": rr_counter,
        "learn": learn,
        "active_users": active_users,
    }

    return my_list


def value_none(value):
    if value is None:
        value = 0
    else:
        value = value

    return value


class CliniciansPageView(LoginRequiredMixin, TemplateView):
    template_name = 'clinicians.html'

    def get_context_data(self, **kwargs):
        clinicians = CustomUser.objects.filter(is_nurse=True)

        # clinicinas = get_weekly_data()

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
            # if "incomplete" in myDict:
            incomplete = myDict['incomplete']
            if incomplete == "incomplete":
                CustomUser.objects.filter(username=username) \
                    .update(forms=F("forms") + 1, incomplete_forms=F("incomplete_forms") + 1)
            else:
                CustomUser.objects.filter(username=username) \
                    .update(forms=F("forms") + 1, completed_forms=F("completed_forms") + 1)

        else:
            username = CustomUser.objects.get(username="chodrine")

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

        Patient.objects.create(**myDict, clinician_2=user, clinician=username)

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

class SaveWorkflowView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [rest_framework.renderers.JSONRenderer]
    parser_classes = [rest_framework.parsers.JSONParser]
    def post(self, request, workflow_id):
        query = Workflow.objects.filter(workflow_id=workflow_id)
        if query.count() == 0:
            next_version = 1
        else:
            next_version = query.aggregate(models.Max("version"))["version__max"] + 1

        jsonobj = request.data
        jsontxt = json.dumps(jsonobj)
        Workflow.objects.create(
            workflow_id=workflow_id,
            version=next_version,
            json=jsontxt,
        )
        return Response("Sucessfully saved workflow")

class ListWorkflowsView(APIView):
    renderer_classes = [rest_framework.renderers.JSONRenderer]
    def get(self, request):
        result = []
        for entry in Workflow.objects.all():
            result.append(dict(
                workflow_id=entry.workflow_id,
                version=entry.version,
                time_created=entry.time_created,
                created_by=entry.created_by.get_username(),
            ))
        return Response(result)

class GetWorkflowView(APIView):
    renderer_classes = [rest_framework.renderers.JSONRenderer]
    def get(self, request, workflow_id, version=None):
        if version is None:
            query = Workflow.objects.filter(workflow_id=workflow_id).order_by('-version')
        else:
            query = Workflow.objects.filter(workflow_id=workflow_id, version=version)

        if query.count() == 0:
            return Response("Invalid workflow id or version", status=status.HTTP_404_NOT_FOUND)
        elif query.count() == 1:
            json = query[0].json
            return HttpResponse(json, content_type="application/json")

def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Alrite_Dataset_' + str(datetime.now()) + '.csv'

    writer = csv.writer(response)
    writer.writerow(
        ['app_version', 'clinician', 'date', 'patient_study_id', 'age(months)', 'gender', 'weight', 'muac', 'symptoms',
         'difficulty_breathing', 'days_with_breathing_difficulties', 'hiv_status', 'child_in_hiv_care',
         'temperature', 'febrile_to_touch', 'blood_oxygen_saturation', 'respiratory_rate', 'breathing_rate',
         'respiratory_rate_score', 'stridor', 'nasal_flaring', 'wheezing', 'stethoscope_used',
         'chest_indrawing', 'bronchodilator', 'bronchodilator_not_given_reason', 'duration', 'diagnosis_1',
         'diagnosis_2', 'diagnosis_3', 'diagnosis_4', 'diagnosis_5', 'diagnosis_6', 'diagnosis_7',
         'diagnosis_8', 'diagnosis_9', 'diagnosis_10',
         'diagnosis_11', 'respiratory_rate_2', 'breathing_rate_2', 'respiratory_rate_score_2',
         'wheezing_2', 'chest_indrawing_2', 'wheezing_before_this_illness', 'child_breathless',
         'breathing_difficulties_last_year', 'child_ever_had_eczema', 'child_parents_with_allergies',
         'smoke_tobacco', 'use_kerosene', 'clinician_diagnosis', 'clinician_treatment' 'incomplete'])

    patients = Patient.objects.all()

    for patient in patients:
        writer.writerow([patient.app_version, 'AL' + patient.clinician.healthy_facility.code + patient.clinician.code,
                         patient.end_date, patient.study_id, patient.age, patient.gender,
                         patient.weight, patient.muac, patient.symptoms, patient.difficulty_breathing,
                         patient.days_with_breathing_difficulties,
                         patient.hiv_status, patient.child_in_hiv_care, patient.temperature, patient.febrile_to_touch,
                         patient.blood_oxygen_saturation, patient.respiratory_rate, patient.breathing_rate,
                         patient.respiratory_rate_score,
                         patient.stridor, patient.nasal_flaring, patient.wheezing, patient.stethoscope_used,
                         patient.chest_indrawing,
                         patient.bronchodilator, patient.bronchodilator_not_given_reason, patient.duration,
                         patient.diagnosis_1,
                         patient.diagnosis_2, patient.diagnosis_3, patient.diagnosis_4, patient.diagnosis_5,
                         patient.diagnosis_6,
                         patient.diagnosis_7, patient.diagnosis_8, patient.diagnosis_9, patient.diagnosis_10,
                         patient.diagnosis_11,
                         patient.respiratory_rate_2, patient.breathing_rate_2, patient.respiratory_rate_score_2,
                         patient.wheezing_2, patient.chest_indrawing_2, patient.wheezing_before_this_illness,
                         patient.child_breathless, patient.breathing_difficulties_last_year,
                         patient.child_ever_had_eczema,
                         patient.child_parents_with_allergies, patient.smoke_tobacco, patient.use_kerosene,
                         patient.clinician_diagnosis,
                         patient.clinician_treatment, patient.incomplete])

    return response

class ExportCSVView(LoginRequiredMixin, View):
    def get(request):
        return export_csv(request)

def get_weekly_data():
    # week_start = datetime.now()
    week_start = Patient.objects.latest('start_date').start_date
    week_start -= timedelta(days=week_start.weekday())
    week_end = week_start + timedelta(days=7)

    patients = Patient.objects.filter(start_date__gte=week_start, start_date__lt=week_end) \
        .values_list('clinician__username').annotate(count=Count('clinician'))
    patients = list(patients)
    patients = convertListToDict2(patients)
    print(patients)

    all_patients = Patient.objects.all().values_list('clinician__username').annotate(count=Count('clinician'))
    all_patients = list(all_patients)
    all_patients = convertListToDict2(all_patients)
    print(all_patients)

    return [patients, all_patients]


def convertListToDict2(li):
    tur = tuple(li)
    dic = dict((x, y) for x, y in tur)

    # dic = dict(sorted(dic.items(), key=lambda x: x[1], reverse=True))
    return dic
