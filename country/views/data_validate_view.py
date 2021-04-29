from django.contrib import messages
from django.http.response import HttpResponseRedirect
from rest_framework.views import APIView

from country.tasks import store_in_temp_table


class DataValidateView(APIView):
    def get(self, request):
        instance_id = self.request.GET.get("data_import_id", None)
        if instance_id is not None:
            try:
                store_in_temp_table.apply_async(args=(instance_id,), queue="covid19")
                messages.info(request, "Validation is in progress!! Please wait for a while")
                return HttpResponseRedirect("/admin/content/dataimport")

            except Exception:
                messages.error(request, "Your import has failed!")
                return HttpResponseRedirect("/admin/content/dataimport")
        else:
            # messages.error(request, 'Your import failed because it only supports .xlsx and .xls file!')
            messages.error(request, "Your import failed !!")
            return HttpResponseRedirect("/admin/content/dataimport")
