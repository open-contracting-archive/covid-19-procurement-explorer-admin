from django.contrib import messages
from django.core import management
from django.http.response import HttpResponseRedirect
from rest_framework.views import APIView

from country.models import ImportBatch


class DataImportView(APIView):
    def get(self, request):
        country = self.request.GET.get("country", None)
        # filename =  self.request.GET.get('filename',None)
        data_import_id = self.request.GET.get("data_import_id", None)
        validated = self.request.GET.get("validated", None)

        if validated:
            if data_import_id:
                try:
                    import_batch_instance = ImportBatch.objects.get(data_import_id=data_import_id)
                    batch_id = import_batch_instance.id
                    # management.call_command('import_tender_excel', country, file_path)
                    management.call_command("import_tender_from_id", country, batch_id)
                    messages.info(request, "Your import has started!")
                    return HttpResponseRedirect("/admin/content/dataimport")

                except Exception:
                    messages.error(request, "Your import has failed!")
                    return HttpResponseRedirect("/admin/content/dataimport")
            else:
                # messages.error(request, 'Your import failed because it only supports .xlsx and .xls file!')
                messages.error(request, "Your import failed!")
                return HttpResponseRedirect("/admin/content/dataimport")
        else:
            messages.error(
                request,
                "Your data import file is not validated, please upload file with all necessary headers and try "
                "importing again.",
            )

            return HttpResponseRedirect("/admin/content/dataimport")
