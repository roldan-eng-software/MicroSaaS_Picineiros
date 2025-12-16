from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule, PeriodicTask
import json


class Command(BaseCommand):
    help = "Cria/atualiza agendamentos do Celery Beat para lembretes e vencimentos"

    def handle(self, *args, **options):
        # Lembretes de agendamento (D-1) às 06:00 todos os dias
        reminder_schedule, _ = CrontabSchedule.objects.get_or_create(
            minute="0", hour="6", day_of_week="*", day_of_month="*", month_of_year="*", timezone="America/Sao_Paulo"
        )
        PeriodicTask.objects.update_or_create(
            name="criar_notificacao_lembrete_agendamento",
            defaults={
                "crontab": reminder_schedule,
                "task": "notificacoes.tasks.criar_notificacao_lembrete_agendamento",
                "enabled": True,
                "kwargs": json.dumps({}),
            },
        )

        # Notificações de vencimentos/vencidos às 07:00 todos os dias
        due_schedule, _ = CrontabSchedule.objects.get_or_create(
            minute="0", hour="7", day_of_week="*", day_of_month="*", month_of_year="*", timezone="America/Sao_Paulo"
        )
        PeriodicTask.objects.update_or_create(
            name="criar_notificacoes_vencimento",
            defaults={
                "crontab": due_schedule,
                "task": "notificacoes.tasks.criar_notificacoes_vencimento",
                "enabled": True,
                "kwargs": json.dumps({}),
            },
        )

        self.stdout.write(self.style.SUCCESS("Agendamentos do Celery Beat configurados."))
