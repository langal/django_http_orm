import json
import inspect
from django_enumfield.enum import Value as EnumValue
from django.http import JsonResponse, HttpResponse
from django.apps import apps
from django.core import serializers
from django.db.models import Model
from django.db.models.fields.related import ForeignObjectRel
from django.db.models.fields.related import ForeignKey
from rest_framework.views import APIView
from .settings import django_http_orm_settings


class ModuleSchema(APIView):
    """API endpoint that lists all Django models in a specified app.
    
    This view provides introspection capabilities by returning a list of all
    Django model classes found within a given Django application module.
    
    URL pattern: /orm/schema/module/{APP_NAME}
    HTTP method: GET
    
    Example:
        curl https://your.server.com/orm/schema/module/myapp
    
    Returns:
        JSON array of model objects, each containing:
        - name: Full module path + class name (e.g., "myapp.models.User")
    """

    # Apply configurable authentication and permission classes
    authentication_classes = django_http_orm_settings.DHOM_AUTH_CLASSES
    permission_classes = django_http_orm_settings.DHOM_PERM_CLASSES
    def get(self, request, *args, **kwargs):
        """Retrieve all Django models from the specified app module.
        
        Args:
            request: HTTP request object
            **kwargs: URL parameters containing 'path' (app name)
            
        Returns:
            JsonResponse: List of model definitions with their full names
        """
        # Extract app name from URL path parameter
        module_name = kwargs.get('path')
        
        # Import the Django app module and access its models submodule
        app = __import__(module_name)
        module = app.__dict__['models']
        
        # Recursively discover all Model classes in the module
        all_models = _get_all_models(module)
        
        # Build response list with model names
        model_list = []
        for model in all_models:
            a_cls = {}
            # Create fully qualified model name (module.ClassName)
            a_cls['name'] = model.__module__ + "." + model.__name__
            model_list.append(a_cls)

        return JsonResponse(model_list, safe=False)

def _get_all_models(module):
    """Recursively discover all Django Model classes within a module.
    
    This function traverses a module and its submodules to find all classes
    that inherit from Django's Model base class. It only includes models
    that belong to the specified module namespace to avoid external dependencies.
    
    Args:
        module: Python module object to inspect
        
    Returns:
        list: List of Django Model class objects
    """
    # Get all members (classes, functions, modules, etc.) of the current module
    members = inspect.getmembers(module)
    all_models = []
    
    for member in members:
        # Check if member is a class that inherits from Django Model
        # and belongs to the current module namespace
        if (inspect.isclass(member[1]) and 
            issubclass(member[1], Model) and 
            member[1].__module__.startswith(module.__name__)):
            all_models.append(member[1])
        # Recursively search submodules that belong to the same namespace
        elif (inspect.ismodule(member[1]) and 
              member[1].__name__.startswith(module.__name__)):
            all_models = all_models + _get_all_models(member[1])
    
    return all_models


class Schema(APIView):
    """API endpoint that returns detailed field information for a specific Django model.
    
    This view provides model introspection by analyzing Django model fields,
    their types, relationships, constraints, and choices. It's useful for
    dynamically building forms, validation, or API documentation.
    
    URL pattern: /orm/schema/{FULL_MODEL_NAME}
    HTTP method: GET
    
    Example:
        curl https://your.server.com/orm/schema/myapp.User
    
    Returns:
        JSON array of field objects, each containing:
        - name: Field name
        - type: Django field class name
        - nullable: Whether field accepts null values
        - auto_created: Whether field is auto-generated
        - has_default: Whether field has a default value
        - choices: Available choices for choice fields
        - from: Related model name for foreign keys
        - external_relation: Whether it's a reverse foreign key
    """

    # Apply configurable authentication and permission classes
    authentication_classes = django_http_orm_settings.DHOM_AUTH_CLASSES
    permission_classes = django_http_orm_settings.DHOM_PERM_CLASSES
    def get(self, request, *args, **kwargs):
        """Retrieve detailed field information for the specified model.
        
        Args:
            request: HTTP request object
            **kwargs: URL parameters containing 'path' (full model name)
            
        Returns:
            JsonResponse: Array of field definitions with metadata
        """
        # Extract model identifier from URL path
        path = kwargs.get('path')
        
        # Parse the full model name (e.g., "myapp.User" -> app="myapp", model="User")
        parts = str(path).split('.')
        app_label = parts[0]  # First part is the Django app name
        model_name = parts[-1]  # Last part is the model class name
        
        # Load the Django model class using Django's app registry
        _class = apps.get_model(app_label=app_label, model_name=model_name)

        # Initialize list to hold field definitions
        fields = []

        # Iterate through all fields defined on the model (including relationships)
        for _field in _class._meta.get_fields():
            a_field = {}
            a_field["name"] = str(_field.name)
            a_field["type"] = str(_field.__class__.__name__)  # Django field type
            
            # Handle reverse foreign key relationships (e.g., user.posts)
            if isinstance(_field, ForeignObjectRel):
                a_field["from"] = str(_field.related_model.__module__ + "." + _field.related_model.__name__)
                a_field["external_relation"] = "true"  # Indicates reverse relationship
            # Handle forward foreign key relationships
            elif isinstance(_field, ForeignKey):
                a_field["from"] = str(_field.related_model.__module__ + "." + _field.related_model.__name__)
                a_field["nullable"] = str(_field.null).lower()
            # Handle regular model fields (CharField, IntegerField, etc.)
            else:
                a_field["nullable"] = str(_field.null).lower()
                a_field["auto_created"] = str(_field.auto_created).lower()  # e.g., auto-generated PKs
                # Check if field has a default value (not just None/empty)
                a_field["has_default"] = "true" if _field.__dict__.get('default', False) else "false"

            # Process choice fields (fields with predefined options)
            if getattr(_field, '_choices', False):
                choices = []
                for choice in _field._choices:
                    value = choice[0]  # The stored value
                    label = ""
                    # Handle Django Enum fields specially
                    if isinstance(choice[1], EnumValue):
                        label = choice[1].name  # Use enum name
                    else:
                        label = choice[1]  # Use display label
                    choices.append({label: value})
                a_field['choices'] = choices

            fields.append(a_field)

        return JsonResponse(fields, safe=False)


class Query(APIView):
    """API endpoint that provides full CRUD operations on Django models via HTTP.
    
    This view maps HTTP methods to Django ORM operations:
    - GET: Query/filter model instances
    - POST: Create new model instances
    - PUT: Update existing model instances
    - DELETE: Remove model instances
    
    URL pattern: /orm/query/{FULL_MODEL_NAME}[/{id}]
    
    Examples:
        # Filter records by query parameters
        curl https://your.server.com/orm/query/myapp.User?email=john@example.com
        
        # Create a new record
        curl -X POST https://your.server.com/orm/query/myapp.User \
             -d '{"first_name": "John", "email": "john@example.com"}'
        
        # Update existing record
        curl -X PUT https://your.server.com/orm/query/myapp.User/123 \
             -d '{"first_name": "Jane"}'
        
        # Delete record
        curl -X DELETE https://your.server.com/orm/query/myapp.User/123
    
    Security Note:
        This provides direct database access via HTTP. Ensure proper
        authentication and permission classes are configured.
    """

    # Apply configurable authentication and permission classes
    authentication_classes = django_http_orm_settings.DHOM_AUTH_CLASSES
    permission_classes = django_http_orm_settings.DHOM_PERM_CLASSES

    def get(self, request, *args, **kwargs):
        """Query model instances using URL query parameters as filters.
        
        Args:
            request: HTTP request object with query parameters
            **kwargs: URL parameters containing 'path' (full model name)
            
        Returns:
            HttpResponse: JSON serialized Django model instances or 405 if no filters
        """
        # Parse model name from URL path
        path = kwargs.get('path')
        parts = str(path).split('.')
        app_label = parts[0]
        model_name = parts[-1]
        
        # Load the Django model class
        _class = apps.get_model(app_label=app_label, model_name=model_name)
        
        # Extract query parameters from URL (e.g., ?name=John&email=john@example.com)
        query = request.GET.dict()
        
        if query:
            # Apply filters and return all matching records as JSON
            # Uses Django's built-in serialization for consistent format
            return HttpResponse(serializers.serialize("json", _class.objects.filter(**query).all()))
        else:
            # Return 405 Method Not Allowed if no query parameters provided
            # This prevents accidental retrieval of all records
            return HttpResponse(status=405)

    def put(self, request, *args, **kwargs):
        """Update an existing model instance by ID.
        
        Args:
            request: HTTP request object with JSON body containing field updates
            **kwargs: URL parameters containing 'path' (model name + ID)
            
        Returns:
            HttpResponse: JSON serialized updated model instance
        """
        # Parse model name and record ID from URL path
        path = kwargs.get('path')
        path, id = str(path).split('/')  # Split "myapp.User/123" -> ["myapp.User", "123"]
        parts = str(path).split('.')
        app_label = parts[0]
        model_name = parts[-1]
        
        # Load the Django model class
        _class = apps.get_model(app_label=app_label, model_name=model_name)
        
        # Get queryset for the specific record (using filter for bulk update)
        instance = _class.objects.filter(pk=id)
        
        # Parse JSON request body to get field updates
        query_dict = json.loads(request.body)
        
        # Apply updates to the record
        instance.update(**query_dict)
        
        # Return the updated record as JSON
        return HttpResponse(serializers.serialize("json", _class.objects.filter(pk=id).all()))

    def post(self, request, *args, **kwargs):
        """Create a new model instance.
        
        Args:
            request: HTTP request object with JSON body containing field values
            **kwargs: URL parameters containing 'path' (full model name)
            
        Returns:
            HttpResponse: JSON serialized newly created model instance
        """
        # Parse model name from URL path
        path = kwargs.get('path')
        parts = str(path).split('.')
        app_label = parts[0]
        model_name = parts[-1]
        
        # Load the Django model class
        _class = apps.get_model(app_label=app_label, model_name=model_name)
        
        # Parse JSON request body to get field values
        query_dict = json.loads(request.body)
        
        # Create new model instance with provided field values
        instance = _class(**query_dict)
        
        # Save to database (triggers validation and auto-generated fields)
        instance.save()
        
        # Return the newly created record as JSON
        return HttpResponse(serializers.serialize("json", _class.objects.filter(pk=instance.pk).all()))

    def delete(self, request, *args, **kwargs):
        """Delete a model instance by ID.
        
        Args:
            request: HTTP request object
            **kwargs: URL parameters containing 'path' (model name + ID)
            
        Returns:
            HttpResponse: Empty response with 200 status on successful deletion
        """
        # Parse model name and record ID from URL path
        path = kwargs.get('path')
        path, id = str(path).split('/')  # Split "myapp.User/123" -> ["myapp.User", "123"]
        parts = str(path).split('.')
        app_label = parts[0]
        model_name = parts[-1]
        
        # Load the Django model class
        _class = apps.get_model(app_label=app_label, model_name=model_name)
        
        # Find the specific record to delete
        instance = _class.objects.filter(pk=id).first()
        
        # Delete the record from database
        # Note: This will cascade delete related objects based on model relationships
        instance.delete()
        
        # Return empty response indicating successful deletion
        return HttpResponse()
