"""URL configuration for Django HTTP ORM endpoints.

This module defines the URL patterns that map HTTP requests to the appropriate
view classes for Django ORM operations via REST API.

URL Structure:
    /orm/schema/module/{app_name} - List all models in an app
    /orm/schema/{full_model_name} - Get field info for a specific model  
    /orm/query/{full_model_name}[/{id}] - CRUD operations on model instances
"""
from django.conf.urls import url

from . import views

# URL patterns for the Django HTTP ORM API
urlpatterns = [
    # Model discovery endpoint: /orm/schema/module/myapp
    # Returns list of all Django models in the specified app
    url(r'^orm/schema/module/(?P<path>.{0,50})', views.ModuleSchema.as_view()),
    
    # Model introspection endpoint: /orm/schema/myapp.User
    # Returns detailed field information for the specified model
    url(r'^orm/schema/(?P<path>.{0,50})', views.Schema.as_view()),
    
    # CRUD operations endpoint: /orm/query/myapp.User[/123]
    # Supports GET (filter), POST (create), PUT (update), DELETE operations
    url(r'^orm/query/(?P<path>.{0,50})', views.Query.as_view()),
]
