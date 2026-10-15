"""Refresh and print this month's costs; warn when over MONTHLY_BUDGET_USD.

Run it by hand, or let .github/workflows/scheduled-tasks.yml run it daily.
"""

from django.conf import settings
from django.core.mail import mail_admins
from django.core.management.base import BaseCommand

from core import costs


class Command(BaseCommand):
    help = "Refresh the monthly cost records and check them against the budget."

    def add_arguments(self, parser):
        parser.add_argument("--period", help="YYYY-MM (default: this month)")
        parser.add_argument(
            "--notify", action="store_true", help="Email OWNER_EMAIL if over budget"
        )

    def handle(self, *args, period=None, notify=False, **options):
        records = costs.run_all(period)
        self.stdout.write(f"Costs for {records[0].period}")
        for record in records:
            self.stdout.write(
                f"  {record.service:<8} ${record.amount_usd:>7}  [{record.source}]  {record.note}"
            )
        over, total = costs.over_budget(records)
        self.stdout.write(f"  {'TOTAL':<8} ${total:>7}  (budget ${settings.MONTHLY_BUDGET_USD})")
        if over:
            message = f"Monthly spend ${total} is over the ${settings.MONTHLY_BUDGET_USD} budget."
            self.stdout.write(self.style.WARNING(message))
            if notify:
                mail_admins("Cost alert", message)
