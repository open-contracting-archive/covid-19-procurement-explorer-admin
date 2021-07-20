from django.contrib import messages
from django.http.response import HttpResponseRedirect
from rest_framework.views import APIView

from country.tasks.validate_and_store_contracts import validate_and_store_contracts


class DataValidateView(APIView):
    def get(self, request):
        data_import_id = self.request.GET.get("data_import_id", None)
        if data_import_id is not None:
            try:
                result = validate_and_store_contracts.apply_async(args=(data_import_id,), queue="covid19")
                if result:
                    messages.info(
                        request,
                        "Validation is in progress!! Please see the details page for more information about it!",
                    )
                    return HttpResponseRedirect("/admin/content/dataimport")
                else:
                    messages.error(
                        request, "Your import has failed. Please see the details page for more information about it!"
                    )
                return HttpResponseRedirect("/admin/content/dataimport")
            except Exception as e:
                messages.error(
                    request,
                    f"Your import has failed.. Please see the details page for more information about it! + {e}",
                )
                return HttpResponseRedirect("/admin/content/dataimport")
        else:
            # messages.error(request, 'Your import failed because it only supports .xlsx and .xls file!')
            messages.error(request, "Your import failed !!")
            return HttpResponseRedirect("/admin/content/dataimport")
