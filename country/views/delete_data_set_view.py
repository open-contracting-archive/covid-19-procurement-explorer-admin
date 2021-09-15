from django.contrib import messages
from django.http.response import HttpResponseRedirect
from rest_framework.views import APIView

from content.models import DataImport


class DeleteDataSetView(APIView):
    def get(self, request):
        try:
            data_import_id = self.request.GET.get("data_import_id", None)

            if data_import_id is not None:
                data_import = DataImport.objects.get(page_ptr_id=data_import_id)
                data_import.delete()
                messages.info(request, "Your dataset has been successfully deleted from the system !!")

                return HttpResponseRedirect("/admin/content/dataimport")
            else:
                messages.error(request, "Invalid data import id !!")

                return HttpResponseRedirect("/admin/content/dataimport")
        except Exception:
            messages.error(request, "Invalid data import id !!")

            return HttpResponseRedirect("/admin/content/dataimport")
