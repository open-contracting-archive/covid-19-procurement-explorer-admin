from django.http import JsonResponse
from rest_framework import status


def custom505(request, exception=None):
    return JsonResponse(
        {"status_code": 500, "error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def custom404(request, exception=None):
    return JsonResponse({"status_code": 404, "error": "The resource was not found"}, status=status.HTTP_404_NOT_FOUND)
