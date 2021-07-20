from django.contrib import messages
from django.http.response import HttpResponseRedirect
from rest_framework.views import APIView

from country.models import ImportBatch
from country.tasks import import_contracts


class DataImportView(APIView):
    def get(self, request):
        country_code = self.request.GET.get("country_code", None)
        data_import_id = self.request.GET.get("data_import_id", None)
        validated = self.request.GET.get("validated", None)

        if validated:
            if data_import_id:
                try:
                    import_batch = ImportBatch.objects.get(data_import_id=data_import_id)
                    import_contracts.apply_async(args=(import_batch.id, country_code), queue="covid19")
                    messages.info(request, "Your import has started!")

                    return HttpResponseRedirect("/admin/content/dataimport")

                except Exception:
                    messages.error(request, "Your import has failed!")
                    return HttpResponseRedirect("/admin/content/dataimport")
            else:
                messages.error(request, "Your import failed!")
                return HttpResponseRedirect("/admin/content/dataimport")
        else:
            messages.error(
                request,
                "Your data import file is not validated, please upload file with all necessary headers and try "
                "importing again.",
            )

            return HttpResponseRedirect("/admin/content/dataimport")
