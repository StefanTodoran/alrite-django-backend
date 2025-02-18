import csv
import datetime
from datetime import timedelta, datetime, timezone
import codecs
import uuid
import base64
import secrets

from django.shortcuts import render
from .serializers import *
from .models import *
from .forms import *
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import make_password
from django.http import Http404
from django.contrib import staticfiles
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
from rest_framework.authtoken.views import ObtainAuthToken
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
import json
from bs4 import BeautifulSoup as bs
from django.db.models import F, Count
from django.db.models import Sum

from . import validation

# Create your views here.

class RegisterView(CreateView):
    template_name = 'registration/register.html'
    form_class = CreateUser
    fields = ['first_name', 'last_name', 'username', 'healthy_facility', 'password']
    success_url = reverse_lazy('clinicians')

    def form_valid(self, form):
        # user = form.save(commit=False)
        #first = form.cleaned_data['first_name']
        #last = form.cleaned_data['last_name']
        #healthy = form.cleaned_data['healthy_facility']
        #password = form.cleaned_data['password']
        #username = first + "_" + last

        #clinician_code = CustomUser.objects.filter(healthy_facility=healthy)

        #if clinician_code.exists():
        #    clinician_code = clinician_code.latest('date_joined').code
        #    new_code = int(clinician_code)
        #    new_code = new_code + 1
        #    code = "0" + str(new_code)
        #else:
        #    code = "01"

        #user = form.save(commit=False)
        #user.username = username
        #user.password = make_password(password)
        #user.is_nurse = True
        #user.code = code

        #user.save()

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
    template_name = 'clinicians_old.html'

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
        writer.writerow([patient.app_version, 'AL{}{}'.format(patient.clinician.healthy_facility.code, patient.clinician.code),
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
    def get(self, request):
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



    









# Workflow related views

class WorkflowsView(LoginRequiredMixin, TemplateView):
    """
    View that displays a table of all the workflows and relevant stats about them.
    Links to workflow info pages for each of them.
    """
    template_name = 'workflows.html'

    def get_context_data(self, **kwargs):
        context = super(WorkflowsView, self).get_context_data(**kwargs)
        workflows = {}
        for entry in Workflow.objects.all():
            workflows.setdefault(entry.workflow_id, [])
            
            workflows[entry.workflow_id].append(dict(
                version = entry.version,
                created_by = entry.created_by,
                time_created = entry.time_created,
                num_patients = entry.get_patients().count(),
                uid = entry.workflow_id + '_' + str(entry.version),
            ))
        
        workflow_list = []
        for workflow_id, all_versions in workflows.items():
            all_versions = sorted(all_versions, key=lambda entry: -entry['version'])
            workflow_list.append(dict(
                workflow_id = workflow_id,
                **all_versions[0],
                all_versions = all_versions,
            ))

        context['workflows'] = workflow_list

        return context

class WorkflowInfoView(LoginRequiredMixin, TemplateView):
    """
    View that displays specific info about a workflow, including
    the previous versions of it, the patient data collected by it,
    and links to edit or delete it.
    """
    template_name = 'workflow_info.html'

    def get_context_data(self, workflow_id, version=None, **kwargs):
        context = super(WorkflowInfoView, self).get_context_data(**kwargs)

        if version is None:
            versions = []
            query = Workflow.objects.filter(workflow_id=workflow_id).order_by('-version')
            if query.count() == 0:
                raise Http404("Workflow does not exist")

            workflow = query[0]

            versions = []
            for entry in query:
                num_changes = len(entry.changes["pages"]) if len(entry.changes.keys()) != 0 else 0

                versions.append(dict(
                    version = entry.version,
                    preview = entry.preview,
                    created_by = entry.created_by,
                    time_created = entry.time_created,
                    num_patients = entry.get_patients().count(),
                    changes = entry.changes,
                    num_changes = num_changes,
                ))
            context['specific_version'] = False
            context['versions'] = versions
        else:
            query = Workflow.objects.filter(workflow_id=workflow_id, version=version)
            if query.count() == 0:
                raise Http404("Workflow does not exist")
            workflow = query[0]

            context['specific_version'] = True

        patients = []
        columns = []
        for entry in query:
            insert_index = 0
            for newcol in entry.get_valueIDs():
                name = newcol.name
                if name in columns:
                    insert_index = columns.index(name)+1
                else:
                    columns.insert(insert_index, name)
                    insert_index += 1

        for entry in query:
            for patient in entry.get_patients():
                data = patient.get_data()
                values = [data.get(col, None) for col in columns]
                patients.append(dict(
                    workflow_version = entry.version,
                    clinician = patient.clinician,
                    time_submitted = patient.time_submitted,
                    values = values,
                ))

        context['patients'] = patients

        context['column_titles'] = columns

        context['workflow'] = dict(
            workflow_id = workflow.workflow_id,
            version = workflow.version,
        )

        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    """ View that summarizes important info about workflows
    and the data collected, meant to be the landing
    page for the backend
    """
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        workflows = {}
        for entry in Workflow.objects.all():
            workflows[entry.workflow_id] = workflows.get(entry.workflow_id, 0) + entry.get_patients().count()
        
        context['workflows'] = [dict(workflow_id=key, num_patients=value) for key,value in workflows.items()]

        users = []
        for user in CustomUser.objects.all():
            if not user.has_usable_password():
                continue

            role = 'Admin' if user.is_admin else 'Doctor' if user.is_doctor else 'Nurse' if user.is_nurse else ''
            users.append(dict(
                name = user.username if user.first_name + user.last_name == '' else user.first_name + ' ' + user.last_name,
                role = role,
                forms = user.forms,
            ))
        context['users'] = users

        patients = []
        for patient in WorkflowPatient.objects.all():
            patients.append(dict(
                id = patient.id,
                workflow_id = patient.workflow.workflow_id,
                workflow_version = patient.workflow.version,
                entry_count = len(patient.get_data()),
            ))
        context['patients'] = patients
        
        return context



class CliniciansView(LoginRequiredMixin, TemplateView):
    """ View that lists all clinicians along with helpful info
    """
    template_name = 'clinicians.html'

    def get_context_data(self, **kwargs):
        context = super(CliniciansView, self).get_context_data(**kwargs)
        
        users = []
        for user in CustomUser.objects.all():
            if not user.has_usable_password():
                continue

            role = 'Admin' if user.is_admin else 'Doctor' if user.is_doctor else 'Nurse' if user.is_nurse else ''
            users.append(dict(
                username = user.username,
                name = user.first_name + ' ' + user.last_name,
                email = user.email,
                role = role,
                forms = user.forms,
            ))

        context['users'] = users
        
        return context


class CreateInviteView(LoginRequiredMixin, TemplateView):
    """ View that deals with invitations of clinicians """
    template_name = "registration/create_invite.html"

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(CreateInviteView, self).get_context_data(**kwargs)

        if self.request.method == "POST":
            form = CreateInviteForm(self.request.POST)

            if form.is_valid():
                token = base64.b32encode(secrets.token_bytes(10)).decode()
                CustomUser.objects.create_user(
                    username = token,
                    is_staff = form.cleaned_data['is_admin'],
                    is_superuser = form.cleaned_data['is_admin'],
                    **form.cleaned_data
                )

                context['success'] = True
                context['url'] = self.request.build_absolute_uri(reverse("accept-invite", kwargs=dict(invitecode=token)))
                return context
        else:
            form = CreateInviteForm()
        
        if self.request.user.is_doctor or self.request.user.is_nurse:
            form.fields['is_admin'].disabled = True

        context['form'] = form
        return context


class AcceptInviteView(TemplateView):
    template_name = "registration/accept_invite.html"
    
    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, invitecode, **kwargs):
        context = super(AcceptInviteView, self).get_context_data(**kwargs)
        
        query = CustomUser.objects.filter(username=invitecode.upper())
        if query.count() == 0:
            raise Http404("Invalid invite link")

        user = query[0]
        if user.has_usable_password():
            raise Http404("Invalid invite link")
        
        if self.request.method == "POST":
            form = AcceptInviteForm(self.request.POST)

            if form.is_valid():
                data = form.cleaned_data
                user.set_password(data.pop('password'))
                for key, val in data.items():
                    setattr(user, key, val)
                user.save()

                context['success'] = True
                return context
        else:
            form = AcceptInviteForm()

        context['form'] = form

        return context

class EditorView(LoginRequiredMixin, View):
    """ View for development that hosts the workflow
    editor at a url (this will be done by the webserver
    once deployed) """
    def get(self, request, workflow_id=None, path="index.html"):
        return staticfiles.views.serve(request, "alrite-workflow-editor/" + path)

class ExportWorkflowCSVView(LoginRequiredMixin, View):
    """ View that exports the data stored in a workflow as csv """
    def get(self, request, workflow_id=None, version=None):
        
        if workflow_id is None:
            query = Workflow.objects.all()
        else:
            query = Workflow.objects.filter(workflow_id=workflow_id).order_by('-version')
            if version is not None:
                query = query.filter(version=version)

        header_columns = ['patient_id', 'clinician', 'workflow_id', 'workflow_version', 'app_version', 'time_submitted']
        columns = []
        for entry in query:
            insert_index = 0
            for newcol in entry.get_valueIDs():
                name = newcol.name
                if name in columns:
                    insert_index = columns.index(name)+1
                else:
                    columns.insert(insert_index, name)
                    insert_index += 1

        response = HttpResponse(content_type='text/csv')
        csvfile = csv.writer(response)
        csvfile.writerow(header_columns + columns)

        for entry in query:
            for patient in entry.get_patients():
                data = patient.get_data()
                values = [
                    patient.id,
                    patient.clinician,
                    patient.workflow.workflow_id,
                    patient.workflow.version,
                    patient.app_version,
                    patient.time_submitted,
                ]
                values = values + [data.get(col, None) for col in columns]
                csvfile.writerow(values)
        
        return response

class PatientsView(LoginRequiredMixin, TemplateView):
    template_name = "patients.html"

    def get_context_data(self, **kwargs):
        context = super(PatientsView, self).get_context_data(**kwargs)

        patients = []
        for patient in WorkflowPatient.objects.all():
            columns = [valueID.name for valueID in patient.workflow.get_valueIDs()]
            data = patient.get_data()
            datalist = [(name, data[name]) for name in columns if name in data]
            patients.append(dict(
                id = patient.id,
                clinician = patient.clinician,
                workflow_id = patient.workflow.workflow_id,
                workflow_version = patient.workflow.version,
                time_submitted = patient.time_submitted,
                data = datalist,
            ))

        context['patients'] = patients

        return context


# API Views

class LoginAPIView(APIView):
    """ API to obtain a token by logging in """

    def post(self, request, *args, **kwargs):
        
        if not request.user.is_anonymous and type(request.user) == CustomUser:
            user = request.user
        else:
            serializer = AuthTokenSerializer(data=request.data)
            #serializer = self.serializer_class(data=request.data, context={'request': request})
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

def debug_reupload_workflows(request):
    for entry in Workflow.objects.all():
        workflow_obj = json.loads(entry.json)
        valueIDs = WorkflowAPIView.extract_valueIDs(None, workflow_obj)
        entry.set_valueIDs(valueIDs)

    return HttpResponse("Success!")

class PostAuthenticator:
    """ Only authenticate for post requests """
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        if hasattr(request.user, 'is_admin'):
            return request.user.is_admin
        return False

class WorkflowAPIView(APIView):
    authentication_classes = [authentication.TokenAuthentication, authentication.SessionAuthentication]
    permission_classes = [PostAuthenticator]

    renderer_classes = [rest_framework.renderers.JSONRenderer]
    parser_classes = [rest_framework.parsers.JSONParser]

    def get(self, request, workflow_id, version=None, preview=False):
        """ GET endpoint to retrieve a workflow
        tries to find a workflow with the given id and version (defaults to most recent)
        If found, the json of the workflow is returned, and if not found a 404 error is
        returned
        """
        if version is None:
            query = Workflow.objects.filter(workflow_id=workflow_id, preview=preview).order_by('-version')
        else:
            query = Workflow.objects.filter(workflow_id=workflow_id, version=version, preview=preview)

        if query.count() == 0:
            return Response({"detail": "Specified workflow does not exist"}, status=status.HTTP_404_NOT_FOUND)
        else:
            json = query[0].json
            return HttpResponse(json, content_type="application/json")
    
    def extract_valueIDs(self, workflow):
        default_types = {
            "TextInput": "text",
            "Counter": "numeric",
            "MultipleChoice": "text",
        }

        mappings = {
            'text': CharValue,
            'alphanumeric': CharValue,
            'any': CharValue,
            'numeric': FloatValue,
        }
        
        valueIDs = []
        for page in workflow['pages']:
            for component in page['content']:
                if 'valueID' in component:
                    typename = "text"
                    if 'type' in component:
                        typename = component['type']
                    elif component['component'] in default_types:
                        typename = default_types[component['component']]

                    valueIDs.append((component['valueID'], mappings.get(typename, CharValue)))

        return valueIDs

    def post(self, request, workflow_id, version=None, preview=False):
        """ POST endpoint to save a workflow
        Expects the body of the post request to be the json of the workflow
        Saves the workflow with the given workflow_id, creating a new version if
        the workflow already exists
        Returns a json object with parameters of the created workflow, including the
        version, api path, time created and author
        If invalid json is passed in a 400 error is returned
        """

        if version is not None:
            return Response("Modifying versions of workflows is not supported",
                    status=status.HTTP_400_BAD_REQUEST)

        jsonobj = request.data

        try:
            errors_obj, valid = validation.validateWorkflow(jsonobj)
        except:
            errors_obj = validation.getBrokenWorkflowErrorArtifact(request.data)
            valid = False

        valueIDs = self.extract_valueIDs(jsonobj)

        if not valid:
            return Response(errors_obj, status=status.HTTP_400_BAD_REQUEST)

        query = Workflow.objects.filter(workflow_id=workflow_id)
        if query.count() == 0:
            next_version = 1
            changes = {}
        else:
            next_version = query.aggregate(models.Max("version"))["version__max"]
            last_entry = query.get(version=next_version)
            if last_entry.preview:
                last_entry.delete()
                query = Workflow.objects.filter(workflow_id=workflow_id).order_by('-version')
                if query.count() == 0:
                    changes = {}
                else:
                    changes = validation.calculateChanges(query[0], jsonobj)
            else:
                next_version += 1
                last_jsonobj = json.loads(last_entry.json)
                changes = validation.calculateChanges(last_jsonobj, jsonobj)

        time_created = datetime.now(timezone.utc)
        user = request.user if request.user.is_authenticated else None

        responseobj = dict(
            version = next_version,
            apipath = reverse('workflow-version-api', kwargs=dict(workflow_id=workflow_id, version=next_version)),
            datapath = reverse('workflow-data-api', kwargs=dict(workflow_id=workflow_id, version=version)),
            time_created = str(time_created),
            created_by = None if user is None else user.username,
        )
        jsonobj['meta'] = responseobj
        jsontxt = json.dumps(jsonobj)

        workflow = Workflow.objects.create(
            workflow_id = workflow_id,
            version = next_version,
            preview = preview,
            time_created = time_created,
            created_by = user,
            json = jsontxt,
            changes = changes,
        )
        workflow.set_valueIDs(valueIDs)
        return Response(responseobj)


class ValidationAPIView(APIView):
    renderer_classes = [rest_framework.renderers.JSONRenderer]
    def post(self, request):
        """ POST endpoint to validate that a workflow has no errors.
        This endpoint returns a error object, described in more detail
        in validation.py. If there are errors in the given workflow,
        a 400 error is returned, otherwise a 200 status is returned.
        """

        # If you are getting "catastrophic error" on the editor
        # it means the except here is triggering. Try commenting the
        # try except out to see the error and fix it in validateWorkflow.
        try:
            errors_obj, valid = validation.validateWorkflow(request.data)
        except:
            errors_obj = validation.getBrokenWorkflowErrorArtifact(request.data)
            valid = False
        
        # print(validation.calculateChanges(request.data, request.data))
        
        if valid:
            return Response(errors_obj)
        else:
            return Response(errors_obj, status=status.HTTP_400_BAD_REQUEST)


class ListWorkflowsAPIView(APIView):
    renderer_classes = [rest_framework.renderers.JSONRenderer]
    def get(self, request):
        """ GET endpoint that returns a json list of all the workflows with
        the id, version, creation time and author.
        """
        workflows = {}
        for entry in Workflow.objects.all():
            workflows.setdefault(entry.workflow_id, dict(
                workflow_id=entry.workflow_id,
                apipath = reverse("workflow-api", kwargs=dict(workflow_id=entry.workflow_id)),
                versions=[],
            ))
            workflows[entry.workflow_id]['versions'].append(dict(
                version = entry.version,
                time_created = entry.time_created,
                created_by = None if entry.created_by is None else entry.created_by.get_username(),
                apipath = reverse("workflow-version-api", kwargs=dict(workflow_id=entry.workflow_id, version=entry.version)),
            ))
        return Response(list(workflows.values()))

class SaveWorkflowPatientAPIView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    renderer_classes = [rest_framework.renderers.JSONRenderer]
    def post(self, request, workflow_id, version):
        """ POST endpoint to upload patient data collected by a workflow
        The data is expected to be in json format, with two fields:
            summary: a dictionary with all valueIDs mapped to the collected value
            diagnoses: a list of the diagnoses that the app decided on """

        query = Workflow.objects.filter(workflow_id=workflow_id, version=version)
        if query.count() == 0:
            return Response({"detail": "Specified workflow does not exist"}, status=status.HTTP_404_NOT_FOUND)

        workflow = query[0]

        errors = {}
        if 'summary' not in request.data:
            errors['summary'] = 'this field is required'
        #if 'diagnoses' not in request.data:
            #errors['diagnoses'] = 'this field is required'
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        valid_keys = [field.name for field in workflow.get_valueIDs()]

        data = {}
        for key, value in request.data['summary'].items():
            if key in valid_keys:
                data[key] = value

        patient = WorkflowPatient.objects.create(
            clinician = request.user if request.user.is_authenticated else None,
            workflow = workflow,
        )
        patient.set_data(data)

        return Response({"data": "sumbittem"})


