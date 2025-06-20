from django.core.management.base import BaseCommand
from django.utils import timezone
from branches.models import Branch
from customers.models import Member
from users.models import CustomUser
from inventory.models import Inventory


class Command(BaseCommand):
    help = "Creates test data for the application"

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating test data...")
        main_branch, sub_branch = self.create_branches()
        self.create_users(main_branch)
        self.create_members(main_branch, sub_branch)
        self.create_inventory()
        self.stdout.write(self.style.SUCCESS("Test data creation complete!"))

    def create_branches(self):
        main_branch, created = Branch.objects.get_or_create(
            name="Main Branch",
            defaults={
                "code": "MAIN",
                "type": "main",
                "email": "main@example.com",
                "address": "123 Main St",
                "phone": "1234567890",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Successfully created main branch"))
        else:
            self.stdout.write("Main branch already exists")

        sub_branch, created = Branch.objects.get_or_create(
            name="Sub Branch 1",
            defaults={
                "code": "SUB1",
                "type": "sub",
                "parent": main_branch,
                "email": "sub1@example.com",
                "address": "456 Sub St",
                "phone": "0987654321",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Successfully created sub branch"))
        else:
            self.stdout.write("Sub branch 1 already exists")
        return main_branch, sub_branch

    def create_users(self, main_branch):
        if not CustomUser.objects.filter(phone="9876543210").exists():
            CustomUser.objects.create_superuser(
                "9876543210", "password", full_name="Super Admin", role="admin"
            )
            self.stdout.write(self.style.SUCCESS("Successfully created superuser"))
        else:
            self.stdout.write("Superuser already exists")

        if not CustomUser.objects.filter(phone="7022229993").exists():
            CustomUser.objects.create_superuser(
                phone="7022229993",
                password="1234",
                full_name="Chanti",
                role="admin",
                branch=main_branch,
            )
            self.stdout.write(
                self.style.SUCCESS("Successfully created superuser Chanti")
            )
        else:
            self.stdout.write("Superuser Chanti already exists")

        if not CustomUser.objects.filter(phone="9876543211").exists():
            staff_user = CustomUser.objects.create_user(
                phone="9876543211",
                password="password",
                full_name="Staff User",
                role="staff",
                branch=main_branch,
            )
            staff_user.is_staff = True
            staff_user.save()
            self.stdout.write(self.style.SUCCESS("Successfully created staff user"))
        else:
            self.stdout.write("Staff user already exists")

    def create_members(self, main_branch, sub_branch):
        member1, created = Member.objects.get_or_create(
            phone="1112223333",
            defaults={
                "name": "John Doe",
                "address": "1 Test Ave",
            },
        )
        if created:
            member1.branches.add(main_branch)
            self.stdout.write(
                self.style.SUCCESS("Successfully created member John Doe")
            )
        else:
            self.stdout.write("Member John Doe already exists")

        member2, created = Member.objects.get_or_create(
            phone="4445556666",
            defaults={
                "name": "Jane Smith",
                "address": "2 Test St",
            },
        )
        if created:
            member2.branches.add(main_branch, sub_branch)
            self.stdout.write(
                self.style.SUCCESS("Successfully created member Jane Smith")
            )
        else:
            self.stdout.write("Member Jane Smith already exists")

    def create_inventory(self):
        try:
            inventory = Inventory(
                company_name="Test Company",
                part_name="Test Part",
                part_number="1234567890",
                description="Test Description",
                purchased_price=100,
                selling_price=150,
                discount=10,
                quantity=100,
                minimum_quantity=10,
            )
            inventory.save()
            self.stdout.write(self.style.SUCCESS("Successfully created inventory"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating inventory: {e}"))
