from django.core.management.base import BaseCommand
from django.utils import timezone
from branches.models import Branch
from customers.models import Member
from users.models import CustomUser
from inventory.models import Inventory, StockTransaction


class Command(BaseCommand):
    help = "Creates test data for the application"

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating test data...")
        main_branch, sub_branch = self.create_branches()
        self.create_users(main_branch)
        self.create_members(main_branch, sub_branch)
        self.create_inventory(main_branch)
        self.stdout.write(self.style.SUCCESS("Test data creation complete!"))

    def create_branches(self):
        main_branch, created = Branch.objects.get_or_create(
            name="Hunsagi",
            defaults={
                "code": "HUN",
                "type": "main",
                "email": "hunsagi@example.com",
                "address": "123 Main St",
                "phone": "1234567890",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Successfully created main branch"))
        else:
            self.stdout.write("Main branch already exists")

        sub_branch, created = Branch.objects.get_or_create(
            name="Kadapa",
            defaults={
                "code": "KAD",
                "type": "sub",
                "parent": main_branch,
                "email": "kadapa@example.com",
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

        if not CustomUser.objects.filter(phone="9945485444").exists():
            CustomUser.objects.create_superuser(
                phone="9945485444",
                password="1234",
                full_name="vamsi Krishna",
                role="admin",
                branch=main_branch,
            )
            self.stdout.write(
                self.style.SUCCESS("Successfully created superuser vamsi")
            )
        else:
            self.stdout.write("Superuser vamsi already exists")

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
                "name": "Raghavendra",
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
                "name": "Rajesh",
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

    def create_inventory(self, main_branch):

        try:
            self.stdout.write(self.style.SUCCESS("Successfully created inventory"))
            inventory = Inventory(
                company_name="Test Company",
                part_name="Test Part",
                part_number="1234567890",
                uom="PCS",
                notes="Test Notes",
                purchased_price=100,
                selling_price=150,
                discount=10,
                minimum_quantity=10,
                gst=5,
                is_active=True,
                branch=main_branch,
                created_by=CustomUser.objects.get(phone="7022229993"),
            )
            inventory.save()
            self.stdout.write(self.style.SUCCESS("Successfully created inventory"))
            branch_inventory = StockTransaction(
                inventory=inventory,
                transaction_type="initial",
                quantity=100,
                notes="Test Notes",
                created_by=CustomUser.objects.get(phone="7022229993"),
            )
            branch_inventory.save()
            self.stdout.write(
                self.style.SUCCESS("Successfully created stock transaction")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating inventory: {e}"))
