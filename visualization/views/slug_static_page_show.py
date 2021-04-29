from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from content.models import StaticPage
from visualization.helpers.general import page_expire_period


class SlugStaticPageShow(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request, *args, **kwargs):
        page_type = self.kwargs["type"]
        result = {}
        try:
            if page_type:
                results = StaticPage.objects.filter(page_type=page_type.title()).values("page_type", "body")
                result["page_type"] = results[0]["page_type"]
                result["body"] = results[0]["body"]

        except Exception:
            result = [{"error": "Content doest not exists"}]

        return JsonResponse(result, safe=False)
