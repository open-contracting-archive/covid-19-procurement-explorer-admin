from django.core.management.base import BaseCommand

from country.tasks.export_summary_report import export_summary_report


class Command(BaseCommand):
    help = "Export overall summary report"

    def handle(self, *args, **kwargs):
        self.stdout.write("Exporting")
        export_summary_report.apply()
        return "Done"
