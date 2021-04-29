from django.http.response import HttpResponseRedirect
from rest_framework.views import APIView


class DataEditView(APIView):
    def get(self, request):
        data_import_id = self.request.GET.get("data_import_id", None)

        return HttpResponseRedirect("/admin/country/tempdataimporttable/?import_batch__id__exact=" + data_import_id)
