# coding=utf-8
import sys
from djcelery.models import PeriodicTask, CrontabSchedule
from django.core.management.base import BaseCommand


__author__ = "chenzhaohui@cloudin.kmail.com"


class Command(BaseCommand):
    def handle(self, *args, **options):
        # collect_data task
        collect_data_cs, _ = CrontabSchedule.objects.get_or_create(
            minute="00", hour="16", day_of_week="*", day_of_month="*", month_of_year="*"
        )  # 北京时间0点的utc时间是16点
        PeriodicTask.objects.update_or_create(name="report_collect_data", defaults={
            "task": "console.finance.report.tasks.collect_data",
            "crontab": collect_data_cs,
        })

        # # send_day_report task
        # send_day_report_cs, _ = CrontabSchedule.objects.get_or_create(
        #     minute="00", hour="07", day_of_week="*", day_of_month="*", month_of_year="*"
        # )
        # PeriodicTask.objects.get_or_create(name="send_day_report", defaults={
        #     "task": "console.finance.report.send_day_report",
        #     "crontab": send_day_report_cs,
        # })
        #
        # # send_week_report task
        # send_week_report_cs, _ = CrontabSchedule.objects.get_or_create(
        #     minute="00", hour="07", day_of_week="0", day_of_month="*", month_of_year="*"
        # )
        # PeriodicTask.objects.get_or_create(name="send_week_report", defaults={
        #     "task": "console.finance.report.send_week_report",
        #     "crontab": send_week_report_cs,
        # })
        sys.stdout.write('import report crontab tasks success.')
