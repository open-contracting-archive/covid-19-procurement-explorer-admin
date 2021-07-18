from celery import Celery

from country.models import RedFlag, Tender
from country.red_flag import RedFlags

app = Celery()


@app.task(name="process_redflag")
def process_redflag(id):
    tender = Tender.objects.get(id=id)
    red_flag = RedFlags()
    flag1 = getattr(red_flag, "flag1")(id)
    flag4 = getattr(red_flag, "flag4")(id)
    flag8 = getattr(red_flag, "flag8")(id)
    if flag1:
        flag1_obj = RedFlag.objects.get(function_name="flag1")
        tender.red_flag.add(flag1_obj)
    if flag4:
        flag4_obj = RedFlag.objects.get(function_name="flag4")
        tender.red_flag.add(flag4_obj)
    if flag8:
        flag8_obj = RedFlag.objects.get(function_name="flag8")
        tender.red_flag.add(flag8_obj)
    print(f"end of {id}")
