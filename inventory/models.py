from django.db import models
from django.utils import timezone
from django.conf import settings
from suppliers.models import Supplier
from django.db.models import Sum
import random
import string
from base.stringProcess import StringProcessor
from branches.models import Branch


class Inventory(models.Model):
    UOM_CHOICES = [
        ("PCS", "Pieces"),
        ("LIT", "Liters"),
        ("BOX", "Boxes"),
        ("SET", "Sets"),
        ("PAK", "Packs"),
        ("BAG", "Bags"),
    ]

    company_name = models.CharField(max_length=100)
    part_name = models.CharField(max_length=100)
    part_number = models.CharField(max_length=50, blank=True, null=True)
    barcode = models.CharField(max_length=100, unique=True, blank=True, null=True)
    uom = models.CharField(max_length=100, default="PCS", choices=UOM_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    purchased_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    minimum_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    available_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst = models.DecimalField(max_digits=5, decimal_places=2, default=5)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventories_created_by",
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name="inventories_branch",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.barcode:
            for _ in range(5):
                barcode = "".join(random.choices(string.digits, k=6))
                if not Inventory.objects.filter(barcode=barcode).exists():
                    self.barcode = barcode
                    break

        self.company_name = StringProcessor(self.company_name).title
        self.part_name = StringProcessor(self.part_name).title
        self.part_number = StringProcessor(self.part_number).uppercase
        self.notes = StringProcessor(self.notes).title
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.barcode or 'NoBarcode'} - {self.company_name} - {self.part_name}"

    class Meta:
        verbose_name_plural = "Inventories"
        ordering = ["company_name", "part_name"]

    @property
    def discounted_price(self):
        if self.discount > 0:
            return self.selling_price * (1 - self.discount / 100)
        return self.selling_price

    @property
    def actual_quantity(self):
        session_items_total = (
            self.billing_session_items.filter(
                session__user__branch=self.branch
            ).aggregate(total=Sum("quantity"))["total"]
            or 0
        )

        actual_available = self.available_quantity - session_items_total

        return max(actual_available, 0)

    @property
    def stock_status_badge(self):
        """Returns stock status for badge display"""
        if self.actual_quantity <= 0:
            return "out"
        elif self.actual_quantity <= self.minimum_quantity:
            return "low"
        else:
            return "available"

    def is_quantity_available(self, requested_quantity, exclude_session_item=None):
        """
        Check if requested quantity is available, optionally excluding a specific session item
        """

        actual_available = self.actual_quantity

        # If excluding a specific session item, add its quantity back to available
        if exclude_session_item:
            actual_available += exclude_session_item.quantity

        return actual_available >= requested_quantity


class StockTransaction(models.Model):
    TRANSACTION_TYPES = [
        ("initial", "Initial"),
        ("purchase", "Purchase"),
        ("adjustment", "Adjustment"),
        ("return", "Return"),
        ("damage", "Damage/Loss"),
    ]

    inventory = models.ForeignKey(
        Inventory, on_delete=models.CASCADE, related_name="inventory_transactions"
    )

    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reference_number = models.CharField(
        max_length=50, blank=True, null=True
    )  # For purchase orders, sales orders, etc.
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="stock_transactions_user",
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_transaction_type_display()}"

    def save(self, *args, **kwargs):
        # Normalize notes

        self.notes = StringProcessor(self.notes.strip()).title

        # Normalize quantity sign
        if self.transaction_type in ["initial", "purchase"]:
            self.quantity = abs(self.quantity)
        elif self.transaction_type in ["adjustment", "return", "damage"]:
            self.quantity = -abs(self.quantity)

        super().save(*args, **kwargs)


class ProductAssembly(models.Model):
    """
    Represents a product assembly (Bill of Materials) that consists of multiple inventory items.
    Example: A drone assembly that includes battery, propellers, frame, etc.
    """
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True)
    barcode = models.CharField(max_length=100, unique=True, blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        related_name="product_assemblies",
        null=True,
        blank=True,
        help_text="Optional: Branch where assembly was created. Assemblies are shared across all branches."
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="assemblies_created",
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Generate barcode if not provided
        if not self.barcode:
            for _ in range(5):
                barcode = "".join(random.choices(string.digits, k=6))
                if not ProductAssembly.objects.filter(barcode=barcode).exists():
                    self.barcode = barcode
                    break
        
        self.name = StringProcessor(self.name).title
        self.description = StringProcessor(self.description).title
        self.notes = StringProcessor(self.notes).title
        self.sku = StringProcessor(self.sku).uppercase
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.barcode or 'NoBarcode'} - {self.name}"

    class Meta:
        verbose_name_plural = "Product Assemblies"
        ordering = ["name"]

    def get_total_component_cost(self):
        """Calculate total cost of all components"""
        total = 0
        for component in self.components.all():
            total += component.inventory_item.purchased_price * component.quantity_required
        return total

    def get_total_amount(self):
        """Calculate total selling amount of all components"""
        total = 0
        for component in self.components.all():
            if component.selling_price > 0:
                component_price = float(component.selling_price)
            else:
                component_price = float(component.inventory_item.discounted_price)
            component_total = component_price * float(component.quantity_required)
            total += component_total
        return round(total, 2)

    def check_components_availability(self, quantity=1, branch=None, use_branch_inventory=False):
        """
        Check if all components are available in sufficient quantities
        Returns: (is_available: bool, missing_items: list)
        
        Args:
            quantity: Quantity of assemblies needed
            branch: Branch to check availability for
            use_branch_inventory: If True, check BranchInventory for staff users instead of Inventory.branch
        """
        from inventoryManage.models import BranchInventory
        
        missing_items = []
        for component in self.components.all():
            inventory_item = component.inventory_item
            required_qty = component.quantity_required * quantity
            
            if branch and use_branch_inventory:
                # For staff users, check BranchInventory
                branch_inventory = BranchInventory.objects.filter(
                    branch=branch, inventory=inventory_item
                ).first()
                
                if not branch_inventory:
                    missing_items.append({
                        'item': inventory_item,
                        'required': required_qty,
                        'available': 0,
                        'reason': 'Item not in branch'
                    })
                else:
                    actual_available = branch_inventory.actual_quantity
                    if actual_available < required_qty:
                        missing_items.append({
                            'item': inventory_item,
                            'required': required_qty,
                            'available': actual_available,
                            'reason': 'Insufficient stock'
                        })
            elif branch and inventory_item.branch != branch:
                # For admin users, check if item is in the branch
                missing_items.append({
                    'item': inventory_item,
                    'required': required_qty,
                    'available': 0,
                    'reason': 'Item not in branch'
                })
            elif inventory_item.actual_quantity < required_qty:
                # Check inventory quantity
                missing_items.append({
                    'item': inventory_item,
                    'required': required_qty,
                    'available': inventory_item.actual_quantity,
                    'reason': 'Insufficient stock'
                })
        
        return len(missing_items) == 0, missing_items

    def is_fully_available_for_branch(self, branch, use_branch_inventory=True):
        """
        Check if all components are available in the specified branch
        For staff users, this should use BranchInventory (use_branch_inventory=True)
        For admin users, this checks Inventory.branch (use_branch_inventory=False)
        """
        is_available, _ = self.check_components_availability(
            quantity=1, branch=branch, use_branch_inventory=use_branch_inventory
        )
        return is_available

    def get_max_assemblies_possible(self, branch=None, use_branch_inventory=False):
        """
        Calculate the maximum number of assemblies that can be made with current inventory.
        Returns the minimum number based on all components' availability.
        
        Args:
            branch: Branch to check inventory for (required for staff users)
            use_branch_inventory: If True, check BranchInventory for staff users (default: False for admin)
                                 If False, check Inventory.branch for admin users
        
        Returns:
            dict with:
                - max_assemblies: Maximum number of assemblies that can be made (int)
                - limiting_component: The component that limits production (AssemblyComponent or None)
                - component_details: List of dicts with details for each component
        """
        from inventoryManage.models import BranchInventory
        from decimal import Decimal
        
        if not self.components.exists():
            return {
                'max_assemblies': 0,
                'limiting_component': None,
                'component_details': [],
                'message': 'No components defined for this assembly'
            }
        
        max_assemblies = None
        limiting_component = None
        component_details = []
        
        for component in self.components.all():
            inventory_item = component.inventory_item
            quantity_required = component.quantity_required
            
            # Get available quantity based on user type
            if branch and use_branch_inventory:
                # For staff users, check BranchInventory
                branch_inventory = BranchInventory.objects.filter(
                    branch=branch, inventory=inventory_item
                ).first()
                
                if not branch_inventory:
                    available_qty = Decimal('0')
                    reason = 'Item not in branch'
                else:
                    available_qty = Decimal(str(branch_inventory.actual_quantity))
                    reason = 'Available' if available_qty > 0 else 'Out of stock'
            elif branch and inventory_item.branch != branch:
                # For admin users, check if item is in the branch
                available_qty = Decimal('0')
                reason = 'Item not in branch'
            else:
                # For admin users, check inventory quantity
                available_qty = Decimal(str(inventory_item.actual_quantity))
                reason = 'Available' if available_qty > 0 else 'Out of stock'
            
            # Calculate how many assemblies can be made with this component
            if quantity_required > 0:
                assemblies_possible = int(available_qty / quantity_required)
            else:
                assemblies_possible = float('inf')  # If no quantity required, it's not limiting
            
            component_details.append({
                'component': component,
                'inventory_item': inventory_item,
                'quantity_required': quantity_required,
                'available_quantity': float(available_qty),
                'assemblies_possible': assemblies_possible if assemblies_possible != float('inf') else 'unlimited',
                'reason': reason,
                'is_limiting': False  # Will be set later
            })
            
            # Track the limiting component (lowest assemblies_possible)
            if assemblies_possible != float('inf'):
                if max_assemblies is None or assemblies_possible < max_assemblies:
                    max_assemblies = assemblies_possible
                    limiting_component = component
        
        # Mark the limiting component
        if limiting_component:
            for detail in component_details:
                if detail['component'] == limiting_component:
                    detail['is_limiting'] = True
                    break
        
        return {
            'max_assemblies': max_assemblies if max_assemblies is not None else 0,
            'limiting_component': limiting_component,
            'component_details': component_details,
            'message': f'Can make {max_assemblies if max_assemblies is not None else 0} assembly(ies)' if max_assemblies is not None else 'Cannot make any assemblies'
        }


class AssemblyComponent(models.Model):
    """
    Represents a component (inventory item) that is part of a product assembly.
    Each component can have its own selling price when sold as part of an assembly.
    """
    assembly = models.ForeignKey(
        ProductAssembly,
        on_delete=models.CASCADE,
        related_name="components"
    )
    inventory_item = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name="used_in_assemblies"
    )
    quantity_required = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1,
        help_text="Quantity of this component needed for one assembly"
    )
    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Selling price for this component when sold as part of the assembly"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.assembly.name} - {self.inventory_item.part_name} ({self.quantity_required})"

    class Meta:
        ordering = ["assembly", "inventory_item"]
        unique_together = [["assembly", "inventory_item"]]

    def save(self, *args, **kwargs):
        self.notes = StringProcessor(self.notes).title
        super().save(*args, **kwargs)
