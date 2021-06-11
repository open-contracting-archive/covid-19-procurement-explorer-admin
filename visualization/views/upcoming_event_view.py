import datetime

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from content.models import EventsPage
from visualization.helpers.general import page_expire_period


class UpcomingEventView(APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        result = {}
        today = datetime.datetime.now()
        results = EventsPage.objects.filter(event_date__gte=today).values(
            "title", "description", "event_date", "time_from", "time_to", "location", "event_image_id"
        )
        result["title"] = results[0]["title"]
        result["description"] = results[0]["description"]
        result["event_date"] = results[0]["event_date"]
        result["time_from"] = results[0]["time_from"]
        result["time_to"] = results[0]["time_to"]
        result["location"] = results[0]["location"]

        return JsonResponse(result, safe=False)
