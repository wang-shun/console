# coding=utf-8
import datetime

from django.core.management.base import BaseCommand, CommandError
from console.finance.report.tasks import collect_data_by_date

__author__ = "chenzhaohui@cloudin.kmail.com"


class Command(BaseCommand):
    help = "collect report data, usage: collect_report_data --date=20171008 (default is yesterday)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            default=None,
            help='the date collected. format is %%Y%%m%%d',
        )

    def handle(self, *args, **options):
        if options["date"]:
            try:
                date = datetime.datetime.strptime(options["date"], "%Y%m%d")
            except ValueError:
                raise CommandError("date %s unavailable")
        else:
            now = datetime.datetime.now()
            date = datetime.datetime(now.year, now.month, now.day) - datetime.timedelta(days=1)
        collect_data_by_date(date)
