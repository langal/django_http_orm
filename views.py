# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
# pylint: disable=E1101
import json
import inspect
import logging
from rest_framework.views import APIView
from django_enumfield.enum import Value as EnumValue
from django.http import JsonResponse, HttpResponse
from django.apps import apps
from django.core import serializers
from django.db.models import Model
from django.db.models.fields.related import ForeignObjectRel
from django.db.models.fields.related import ForeignKey

logger = logging.getLogger('django')

class ModuleSchema(APIView):

    authentication_classes = []
    permission_classes = []

    """This endpoint loads up the DB Model schemas.

    eg.  curl https://your.server.com/api/thing/schema/module/app"""
    def get(self, request, *args, **kwargs):
        module_name = kwargs.get('path')
        app =  __import__(module_name)
        module = app.__dict__['models']
        all_models = _get_all_models(module)
        model_list = []
        for model in all_models:
            a_cls = {}
            a_cls['name'] = model.__module__ + "." + model.__name__
            model_list.append(a_cls)

        return JsonResponse(model_list, safe=False)

def _get_all_models(module):
    members = inspect.getmembers(module)
    all_models = []
    for member in members:
        if inspect.isclass(member[1]) and issubclass(member[1], Model) and member[1].__module__.startswith(module.__name__):
            all_models.append(member[1])
        elif inspect.ismodule(member[1]) and member[1].__name__.startswith(module.__name__):
            all_models = all_models + _get_all_models(member[1])
    return all_models


class Schema(APIView):

    authentication_classes = []
    permission_classes = []

    """This endpoint gets a full Model name from the last element of the request PATH
    and basically loads up the matching Class and corresponding fields.

    eg.
    curl https://your.server.com/api/thing/schema/app.models.user.User"""
    def get(self, request, *args, **kwargs):
        path = kwargs.get('path')
        parts = str(path).split('.')
        app_label = parts[0]
        model_name = parts[-1]
        _class = apps.get_model(app_label=app_label, model_name=model_name)

        fields = []

        for _field in _class._meta.get_fields():
            a_field = {}
            a_field["name"] = str(_field.name)
            a_field["type"] = str(_field.__class__.__name__)
            if isinstance(_field, ForeignObjectRel):
                a_field["from"] = str(_field.related_model.__module__ + "." + _field.related_model.__name__)
                a_field["external_relation"] = "true"
            elif isinstance(_field, ForeignKey):
                a_field["from"] = str(_field.related_model.__module__ + "." + _field.related_model.__name__)
                a_field["nullable"] = str(_field.null).lower()
            else:
                a_field["nullable"] = str(_field.null).lower()
                a_field["auto_created"] = str(_field.auto_created).lower()
                a_field["has_default"] = "true" if _field.__dict__.get('default', False) else "false"

            if getattr(_field, '_choices', False):
                choices = []
                for choice in _field._choices:
                    value = choice[0]
                    label = ""
                    if isinstance(choice[1], EnumValue):
                        label = choice[1].name
                    else:
                        label = choice[1]
                    choices.append({label: value})
                a_field['choices'] = choices

            fields.append(a_field)

        return JsonResponse(fields, safe=False)


class Query(APIView):

    """This endpoint loads up a Django Model Class object from thr request path
    and performs a query on the request query parameters.

    example GET:
    curl https://your.server.com/api/thing/query/[FULL MODEL NAME]?email=[...]

    example PUT:
    curl -X PUT https://your.server.com/api/thing/query/[FULL MODEL NAME]/[id] -d '{"first_name": "randi"}'

    example DELETE:
    curl -X DELETE https://your.server.com/api/thing/query/[FULL MODEL NAME]/[id]

    example POST:
    CURL -X POST https://your.server.com/api/thing/query/[FULL MODEL NAME] - d '{"first_name" ...}'
    """
    def get(self, request, *args, **kwargs):
        path = kwargs.get('path')
        parts = str(path).split('.')
        app_label = parts[0]
        model_name = parts[-1]
        _class = apps.get_model(app_label=app_label, model_name=model_name)
        query = request.GET.dict()
        if query:
            return HttpResponse(serializers.serialize("json", _class.objects.filter(**query).all()))
        else:
            return HttpResponse(status=405)

    def put(self, request, *args, **kwargs):
        path = kwargs.get('path')
        path, id = str(path).split('/')
        parts = str(path).split('.')
        app_label = parts[0]
        model_name = parts[-1]
        _class = apps.get_model(app_label=app_label, model_name=model_name)
        instance = _class.objects.filter(pk=id)
        query_dict = json.loads(request.body)
        instance.update(**query_dict)
        return HttpResponse(serializers.serialize("json", _class.objects.filter(pk=id).all()))

    def post(self, request, *args, **kwargs):
        path = kwargs.get('path')
        parts = str(path).split('.')
        app_label = parts[0]
        model_name = parts[-1]
        _class = apps.get_model(app_label=app_label, model_name=model_name)
        query_dict = json.loads(request.body)
        instance = _class(**query_dict)
        instance.save()
        return HttpResponse(serializers.serialize("json", _class.objects.filter(pk=instance.pk).all()))

    def delete(self, request, *args, **kwargs):
        path = kwargs.get('path')
        path, id = str(path).split('/')
        parts = str(path).split('.')
        app_label = parts[0]
        model_name = parts[-1]
        _class = apps.get_model(app_label=app_label, model_name=model_name)
        instance = _class.objects.filter(pk=id).first()
        instance.delete()
        return HttpResponse()
