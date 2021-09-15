import datetime

from celery import Celery

from country.tasks import (
    clear_cache_table,
    country_contract_excel,
    delete_unused_buyers,
    delete_unused_suppliers,
    evaluate_contract_equity,
    evaluate_contract_red_flag,
    evaluate_country_buyer,
    evaluate_country_supplier,
    export_summary_report,
    summarize_country_contracts,
)


class ScheduleRunner:
    def __init__(self):
        self.app = Celery()
        self.instance = self.app.control.inspect()
        self.scheduled_list = self.instance.scheduled()
        self.scheduled_machine = list(self.scheduled_list.keys())[0]
        # task_list = self.instance.registered_tasks()[self.scheduled_machine]
        self.celery_task_list = {
            "evaluate_country_supplier": evaluate_country_supplier,
            "evaluate_country_buyer": evaluate_country_buyer,
            "country_contract_excel": country_contract_excel,
            "export_summary_report": export_summary_report,
            "summarize_country_contracts": summarize_country_contracts,
            "delete_unused_suppliers": delete_unused_suppliers,
            "delete_unused_buyers": delete_unused_buyers,
            "evaluate_contract_red_flag": evaluate_contract_red_flag,
            "evaluate_contract_equity": evaluate_contract_equity,
            "clear_cache_table": clear_cache_table,
        }
        self.datetime_now = datetime.datetime.now()

    def every_hour(self, interval):
        dt = self.datetime_now
        dt_start_of_hour = dt.replace(minute=0, second=0, microsecond=0)
        dt = dt_start_of_hour + datetime.timedelta(hours=int(interval))
        return dt

    def round_minute(self, interval):
        minute = self.datetime_now.minute
        base_number = int(str(minute)[0] + "0")
        tmp = base_number
        interval_list = []

        while tmp <= minute <= 60:
            tmp += interval
            interval_list.append(tmp)

        dt = self.datetime_now
        dt_start_of_hour = dt.replace(minute=0, second=0, microsecond=0)

        return dt_start_of_hour + datetime.timedelta(minutes=interval_list[-1])

    def task_scheduler(self, task_name, interval_name, interval, country_alpha_code=None):
        function_name = getattr(ScheduleRunner, interval_name)
        nearest_hour = function_name(self, interval)

        if bool(self.scheduled_list):
            if len(self.scheduled_list[self.scheduled_machine]) == 0:
                print(f"Task created for time :{nearest_hour}  {self.celery_task_list[task_name]}")
                if country_alpha_code:
                    self.celery_task_list[task_name].apply_async(
                        args=(country_alpha_code,), queue="covid19", eta=nearest_hour
                    )
                else:
                    self.celery_task_list[task_name].apply_async(queue="covid19", eta=nearest_hour)
                return "Done"
            else:
                country = [country_alpha_code]
                user_data = {"task": task_name, "country": country}
                task_list = []

                for task in self.scheduled_list[self.scheduled_machine]:
                    task_name = task["request"]["name"]
                    country = task["request"]["args"]
                    data = {"task": task_name, "country": country}

                    if data not in task_list:
                        task_list.append(data)

                if user_data not in task_list:
                    print(f"Task created for time :{nearest_hour} {self.celery_task_list[task_name]}")

                    if country_alpha_code:
                        self.celery_task_list[task_name].apply_async(
                            args=(country_alpha_code,), queue="covid19", eta=nearest_hour
                        )
                    else:
                        self.celery_task_list[task_name].apply_async(
                            args=(country_alpha_code,), queue="covid19", eta=nearest_hour
                        )

                    return "Done"
                else:
                    print("Already in queue")

                    return "Exited"
        else:
            print("Celery queue not executed!!")

            return "Error"
