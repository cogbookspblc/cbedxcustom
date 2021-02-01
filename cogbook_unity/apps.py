"""
Cogbook Unity Application Configuration
"""

from django.apps import AppConfig


class CogBookUnityConfig(AppConfig):
    """
    Application Configuration for Control Panel.
    """
    name = u'openedx.features.cogbook_unity'

    def ready(self):
        """
        Not very sure as to what goes here
        """
        # if settings.FEATURES.get('ENABLE_SPECIAL_EXAMS'):
        #     from .services import InstructorService
        #     set_runtime_service('instructor', InstructorService())
        return True 

