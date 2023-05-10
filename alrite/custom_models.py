from django.db import models, connection
from django.contrib import admin

from .models import AbstractPatient, Workflow

def addDefaults(Class, **defaults):
    def newClass(**kwargs):
        for name, value in defaults.items():
            kwargs.setdefault(name, value)
        return Class(**kwargs)
    return newClass

def schema_to_model(name, schema):
    class Meta:
        managed = False

    attrs = {"__module__": "alrite.models", "Meta": Meta}
    for field_params in schema:
        model_class = getattr(models, field_params['type'])
        #model_class = field_types[field_params['type']]
        attrs[field_params['name']] = model_class(**field_params.get('params', {}))

    model = type(name, (models.Model,), attrs)
    return model

def workflow_to_model(entry):
    modelname = 'Workflow_{}_{}'.format(entry.workflow_id, entry.version)
    model = schema_to_model(modelname, entry.schema)
    return model

def register_model(model):
    #admin.site.register(model, {})
    pass

def has_table(entry):
    modelname = 'Workflow_{}_{}'.format(entry.workflow_id, entry.version)
    return modelname in connection.introspection.table_names()

def create_model(model):
    # test if table has been created
    if model._meta.db_table not in connection.introspection.table_names():
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(model)
