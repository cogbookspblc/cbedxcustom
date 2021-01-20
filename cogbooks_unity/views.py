"""
View for Control Panel application
"""
from util.json_request import JsonResponse, expect_json

from django.views.generic import View
from django.http import Http404, HttpResponse, HttpResponseBadRequest

from opaque_keys.edx.asides import AsideUsageKeyV1, AsideUsageKeyV2
from opaque_keys.edx.keys import CourseKey, UsageKey
from opaque_keys.edx.locator import LibraryUsageLocator

from xblock.django.request import django_to_webob_request, webob_to_django_response
from xblock.exceptions import NoSuchHandlerError

from rest_framework.response import Response
from rest_framework.views import APIView
from models.settings.course_grading import CourseGradingModel


from openedx.core.lib.api.view_utils import DeveloperErrorViewMixin, view_auth_classes

from contentstore.views.helpers import create_xblock, usage_key_with_run
from contentstore.views.item import StudioEditModuleRuntime
from contentstore.utils import get_xblock_aside_instance


from xmodule.modulestore.django import modulestore


@view_auth_classes()
class UnityView(DeveloperErrorViewMixin, APIView):
    """
    **Use Cases**

        Retrieve general discussion metadata for a course.

    **Example Requests**:

        GET /api/discussion/v1/courses/course-v1:ExampleX+Subject101+2015

    **Response Values**:

        * id: The identifier of the course

        * blackouts: A list of objects representing blackout periods (during
            which discussions are read-only except for privileged users). Each
            item in the list includes:

            * start: The ISO 8601 timestamp for the start of the blackout period

            * end: The ISO 8601 timestamp for the end of the blackout period

        * thread_list_url: The URL of the list of all threads in the course.

        * topics_url: The URL of the topic listing for the course.
    """
    def get(self, request):
        """Implements the GET method as described in the class docstring."""
        # course_key = CourseKey.from_string(course_id)  # TODO: which class is right?
        return JsonResponse({'success':True})

    def post(self, request):
        if 'duplicate_source_locator' in request.data:
            # parent_usage_key = usage_key_with_run(request.json['parent_locator'])
            # duplicate_source_usage_key = usage_key_with_run(request.json['duplicate_source_locator'])

            # source_course = duplicate_source_usage_key.course_key
            # dest_course = parent_usage_key.course_key
            # if (
            #         not has_studio_write_access(request.user, dest_course) or
            #         not has_studio_read_access(request.user, source_course)
            # ):
            #     raise PermissionDenied()

            # # dest_usage_key = _duplicate_item(
            # #     parent_usage_key,
            # #     duplicate_source_usage_key,
            # #     request.user,
            # #     request.json.get('display_name'),
            # # )
            return JsonResponse({'error': 'Duplicate key found'})
        else:
            parent_locator = request.data['parent_locator']
            usage_key = usage_key_with_run(parent_locator)
            # if not has_studio_write_access(request.user, usage_key.course_key):
            #     raise PermissionDenied()

            category = request.data['category']
            if isinstance(usage_key, LibraryUsageLocator):
                # Only these categories are supported at this time.
                if category not in ['html', 'problem', 'video']:
                    return HttpResponseBadRequest(
                        "Category '%s' not supported for Libraries" % category, content_type='text/plain'
                    )

            created_block = create_xblock(
                parent_locator=parent_locator,
                user=request.user,
                category=category,
                display_name=request.data.get('display_name'),
                boilerplate=request.data.get('boilerplate'),
            )

            if 'graderType' in request.data:
                CourseGradingModel.update_section_grader_type(modulestore().get_item(created_block.location), request.data['graderType'], request.user)
            return JsonResponse(
                {'locator': unicode(created_block.location), 'courseKey': unicode(created_block.location.course_key)}
            )


@view_auth_classes()
class LTIView(DeveloperErrorViewMixin, APIView):
    """
    **Use Cases**

        Retrieve general discussion metadata for a course.

    **Example Requests**:

        GET /api/discussion/v1/courses/course-v1:ExampleX+Subject101+2015

    **Response Values**:

        * id: The identifier of the course

        * blackouts: A list of objects representing blackout periods (during
            which discussions are read-only except for privileged users). Each
            item in the list includes:

            * start: The ISO 8601 timestamp for the start of the blackout period

            * end: The ISO 8601 timestamp for the end of the blackout period

        * thread_list_url: The URL of the list of all threads in the course.

        * topics_url: The URL of the topic listing for the course.
    """
    def get(self, request, usage_key_string):
        """Implements the GET method as described in the class docstring."""
        # course_key = CourseKey.from_string(course_id)  # TODO: which class is right?
        return JsonResponse({'success':True})

    def post(self, request, usage_key_string):
        """
        Dispatch an AJAX action to an xblock

        Args:
            usage_id: The usage-id of the block to dispatch to
            handler (str): The handler to execute
            suffix (str): The remainder of the url to be passed to the handler

        Returns:
            :class:`django.http.HttpResponse`: The response from the handler, converted to a
                django response
        """
        handler = 'submit_studio_edits'
        suffix = ''
        usage_key = UsageKey.from_string(usage_key_string)
        # Let the module handle the AJAX
        req = django_to_webob_request(request)

        asides = []

        try:
            if isinstance(usage_key, (AsideUsageKeyV1, AsideUsageKeyV2)):
                descriptor = modulestore().get_item(usage_key.usage_key)
                aside_instance = get_xblock_aside_instance(usage_key)
                asides = [aside_instance] if aside_instance else []
                resp = aside_instance.handle(handler, req, suffix)
            else:
                descriptor = modulestore().get_item(usage_key)
                descriptor.xmodule_runtime = StudioEditModuleRuntime(request.user)
                resp = descriptor.handle(handler, req, suffix)
        except NoSuchHandlerError:
            raise Http404

        # unintentional update to handle any side effects of handle call
        # could potentially be updating actual course data or simply caching its values
        modulestore().update_item(descriptor, request.user.id, asides=asides)

        return webob_to_django_response(resp)



