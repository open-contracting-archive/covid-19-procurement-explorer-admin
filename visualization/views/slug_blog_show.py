from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from content.models import InsightsPage
from visualization.helpers.general import page_expire_period


class SlugBlogShow(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request, *args, **kwargs):
        content_type = self.kwargs["type"]
        slug = self.kwargs["slug"]
        result = {}
        try:
            if content_type:
                results = InsightsPage.objects.filter(contents_type=content_type.title(), slug=slug).values(
                    "title", "published_date", "body", "author", "country_id", "featured", "content_image_id"
                )
                result["title"] = results[0]["title"]
                result["published_date"] = results[0]["published_date"]
                result["body"] = results[0]["body"]
                result["author"] = results[0]["author"]
                result["featured"] = results[0]["featured"]
                result["country_id"] = results[0]["country_id"]
                result["content_image_id"] = results[0]["content_image_id"]

        except Exception:
            result = [{"error": "Content doest not exists"}]
        return JsonResponse(result, safe=False)
