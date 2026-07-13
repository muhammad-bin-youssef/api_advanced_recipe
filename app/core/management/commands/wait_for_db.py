from django.core.management.commands.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options): ...
