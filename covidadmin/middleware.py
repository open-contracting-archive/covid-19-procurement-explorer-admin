import json

from django.conf import settings
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin


class NonHtmlDebugToolbarMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        debug = request.GET.get("debug", "UNSET")

        if debug != "UNSET" and settings.DEBUG:
            if response["Content-Type"] == "application/octet-stream":
                new_content = "<html><body>Binary Data, " "Length: {}</body></html>".format(len(response.content))
                response = HttpResponse(new_content)
            elif response["Content-Type"] != "text/html":
                content = response.content
                try:
                    json_ = json.loads(content)
                    content = json.dumps(json_, sort_keys=True, indent=2)
                except ValueError:
                    pass
                response = HttpResponse("<html><body><pre>{}" "</pre></body></html>".format(content))

        return response
