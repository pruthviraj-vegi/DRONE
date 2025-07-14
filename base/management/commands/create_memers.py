from django.core.management.base import BaseCommand
from branches.models import Branch
from customers.models import Member
import random


class Command(BaseCommand):
    help = "Creates test data for the application"

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating test data...")
        self.create_members()
        self.stdout.write(self.style.SUCCESS("Test data creation complete!"))

    def create_members(self):
        self.stdout.write("Creating members...")
        for i in range(50):
            phone = f"{random.randint(10**9, 10**10 - 1)}"
            member = Member.objects.create(
                name=f"Member_{i+1}",
                phone=phone,
                address=f"123 Main St{i+1}",
            )
            member.branches.add(Branch.objects.first())
