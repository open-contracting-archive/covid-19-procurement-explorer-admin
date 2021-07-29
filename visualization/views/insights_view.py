from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from content.models import InsightsPage, ResourcesPage
from visualization.helpers.general import page_expire_period


class ViewPaginatorMixin(object):
    min_limit = 1
    max_limit = 10

    def paginate(self, object_list, page=1, limit=10, count=0, **kwargs):
        try:
            page = int(page)
            if page < 1:
                page = 1
        except (TypeError, ValueError):
            page = 1

        try:
            limit = int(limit)
            if limit < self.min_limit:
                limit = self.min_limit
            if limit > self.max_limit:
                limit = self.max_limit
        except (ValueError, TypeError):
            limit = self.max_limit

        paginator = Paginator(object_list, limit)
        try:
            objects = paginator.page(page)
        except PageNotAnInteger:
            objects = paginator.page(1)
        except EmptyPage:
            objects = paginator.page(paginator.num_pages)
        data = {
            "previous_page": objects.has_previous() and objects.previous_page_number() or None,
            "next_page": objects.has_next() and objects.next_page_number() or None,
            "count": count,
            "data": list(objects),
        }
        return data


class InsightsView(ViewPaginatorMixin, APIView):
    @method_decorator(cache_page(page_expire_period()))
    def get(self, request):
        country_code = self.request.GET.get("country", None)
        insight_type = self.request.GET.get("type", None)
        year = self.request.GET.get("year", None)
        order = self.request.GET.get("order", None)
        query = self.request.GET.get("query", None)
        page = self.request.GET.get("page", None)

        result_insight = []
        result_resource = []
        filter_args = {}
        filter_insights_args = {}

        if country_code:
            country_code = str(country_code).upper()
            filter_args["country__country_code_alpha_2"] = country_code

        if insight_type:
            if insight_type in ["News", "Blog"]:
                filter_insights_args["contents_type"] = insight_type

        if year:
            filter_args["published_date__year"] = year

        try:
            if insight_type in ["News", "Blog"] or insight_type is None:
                results_insight = InsightsPage.objects.filter(**filter_args, **filter_insights_args).values(
                    "title", "page_ptr_id", "country__name", "published_date__year", "contents_type"
                )

                for i in results_insight:
                    result_insight.append(
                        {
                            "id": i["page_ptr_id"],
                            "title": i["title"],
                            "country": i["country__name"],
                            "type": i["contents_type"],
                            "year": i["published_date__year"],
                        }
                    )
            if insight_type in ["Resources"] or insight_type is None:
                results_resources = ResourcesPage.objects.filter(**filter_args).values(
                    "title", "page_ptr_id", "country__name", "published_date__year"
                )

                for i in results_resources:
                    result_resource.append(
                        {
                            "id": i["page_ptr_id"],
                            "title": i["title"],
                            "country": i["country__name"],
                            "type": "Resources",
                            "year": i["published_date__year"],
                        }
                    )

            result = result_insight + result_resource
            count = len([ele for ele in result if isinstance(ele, dict)])

            if order is not None:
                if "-" in order:
                    result = sorted(result, key=lambda k: k[order[1:]], reverse=True)
                else:
                    result = sorted(result, key=lambda k: k[order])

            if query is not None:
                result = [i for i in result if i["title"].find(query) != -1]

            return JsonResponse({"data": self.paginate(result, page, count=count)})

        except Exception as e:
            return JsonResponse([{"error": str(e)}], safe=False)
