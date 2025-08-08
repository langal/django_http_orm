from django.conf import settings


class Settings():
    DHOM_AUTH_CLASSES = []
    DHOM_PERM_CLASSES = []

    def __init__(self, *args, **kwargs):
        # Load in the actual authentication classes from a path-String
        if getattr(settings, 'DHOM_AUTH_CLASSES', False):
            for _class in settings.DHOM_AUTH_CLASSES:
                self.DHOM_AUTH_CLASSES.append(_load_class_from_path(_class))
        
        if getattr(settings, 'DHOM_PERM_CLASSES', False):
            for _class in settings.DHOM_PERM_CLASSES:
                self.DHOM_PERM_CLASSES.append(_load_class_from_path(_class))


def _load_class_from_path(path_as_string):
    components = path_as_string.split('.')
    module = __import__(components[0])
    for comp in components[1:]:
        module = getattr(module, comp)
    return module


django_http_orm_settings = Settings()
