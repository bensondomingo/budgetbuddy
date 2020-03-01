from django.apps import AppConfig


class BudgetplannerConfig(AppConfig):
    name = 'budgetplanner'

    def ready(self):
        import budgetplanner.signals
        return super().ready()
