from django.conf import settings


class Settings():
    """Configuration manager for Django HTTP ORM authentication and permissions.
    
    This class loads authentication and permission classes from Django settings
    by dynamically importing them from string paths. This allows for flexible
    configuration without hard-coding specific auth classes.
    
    Attributes:
        DHOM_AUTH_CLASSES: List of authentication class instances
        DHOM_PERM_CLASSES: List of permission class instances
    """
    # Initialize empty lists for auth/permission classes
    DHOM_AUTH_CLASSES = []
    DHOM_PERM_CLASSES = []

    def __init__(self, *args, **kwargs):
        """Initialize settings by loading auth/permission classes from Django settings.
        
        Looks for DHOM_AUTH_CLASSES and DHOM_PERM_CLASSES in Django settings
        and dynamically imports each class from its string path.
        """
        # Load authentication classes from Django settings
        # Example setting: DHOM_AUTH_CLASSES = ['rest_framework.authentication.TokenAuthentication']
        if getattr(settings, 'DHOM_AUTH_CLASSES', False):
            for _class in settings.DHOM_AUTH_CLASSES:
                self.DHOM_AUTH_CLASSES.append(_load_class_from_path(_class))
        
        # Load permission classes from Django settings
        # Example setting: DHOM_PERM_CLASSES = ['rest_framework.permissions.IsAuthenticated']
        if getattr(settings, 'DHOM_PERM_CLASSES', False):
            for _class in settings.DHOM_PERM_CLASSES:
                # BUG FIX: Was incorrectly appending to DHOM_AUTH_CLASSES instead of DHOM_PERM_CLASSES
                self.DHOM_PERM_CLASSES.append(_load_class_from_path(_class))


def _load_class_from_path(path_as_string):
    """Dynamically import a class from its module path string.
    
    This function takes a fully qualified class path (e.g., 'myapp.auth.CustomAuth')
    and returns the actual class object by dynamically importing it.
    
    Args:
        path_as_string: String path to the class (e.g., 'rest_framework.permissions.IsAuthenticated')
        
    Returns:
        class: The imported class object
        
    Example:
        _load_class_from_path('rest_framework.authentication.TokenAuthentication')
        # Returns the TokenAuthentication class
    """
    # Split path into components (e.g., 'myapp.auth.CustomAuth' -> ['myapp', 'auth', 'CustomAuth'])
    components = path_as_string.split('.')
    
    # Import the root module
    module = __import__(components[0])
    
    # Navigate through each component to reach the final class
    # This handles nested modules and classes
    for comp in components[1:]:
        module = getattr(module, comp)
    
    return module


# Global instance of settings used by all views
# This is initialized once when the module is imported
django_http_orm_settings = Settings()
