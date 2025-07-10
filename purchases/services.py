from decimal import Decimal
from typing import List, Dict, Any

from django.db import transaction, models
from django.utils import timezone

from tenants.models import Tenant
from products.models import Product
from suppliers.models import Supplier
from financials.models import AccountPayable, FinancialStatus
from users.models import User
from inventory.services import create_stock_entry, create_stock_adjustment, complete_stock_adjustment, complete_stock_entry
from .models import PurchaseOrder, PurchaseOrderItem, PurchaseOrderStatus


class PurchaseOrderError(Exception):
    """Custom exception for purchase order-related errors."""
    pass


@transaction.atomic
def create_purchase_order(
    *,
    tenant: Tenant,
    supplier: Supplier,
    user: User,
    items_data: List[Dict[str, Any]],
    status_name: str = 'DRAFT',
    expected_delivery_date: timezone.datetime = None,
    notes: str = None
) -> PurchaseOrder:
    """
    Create a purchase order with associated items.
    This function does not create stock entries or financial records.

    Args:
        tenant (Tenant): The tenant associated with the purchase order.
        supplier (Supplier): The supplier for the purchase order.
        user (User): The user creating the purchase order.
        items_data (List[Dict[str, Any]]): List of dictionaries containing item data ('product', 'quantity', 'unit_price').
        status_name (str, optional): Status of the purchase order. Defaults to 'DRAFT'.
        expected_delivery_date (timezone.datetime, optional): Expected delivery date for the purchase order. Defaults to None.
        notes (str, optional): Additional notes for the purchase order. Defaults to None.

    Returns:
        PurchaseOrder: The created purchase order.
    """
    try:
        status = PurchaseOrderStatus.objects.get(
            models.Q(tenant=tenant) | models.Q(tenant__isnull=True),
            name__iexact=status_name
        )
    except PurchaseOrderStatus.DoesNotExist:
        raise PurchaseOrderError(f"Purchase order status '{status_name}' does not exist.")

    purchase_order = PurchaseOrder.objects.create(
        tenant=tenant,
        supplier=supplier,
        created_by=user,
        status=status,
        expected_delivery_date=expected_delivery_date,
        notes=notes
    )

    total_amount = Decimal('0.00')
    for item_data in items_data:
        tenant = purchase_order.tenant
        quantity = Decimal(str(item_data['quantity']))
        unit_price = Decimal(str(item_data['unit_price']))
        item_total = quantity * unit_price

        PurchaseOrderItem.objects.create(
            purchase_order=purchase_order,
            product=item_data['product'],
            quantity=quantity,
            unit_price=unit_price
        )
        total_amount += item_total

    purchase_order.total_amount = total_amount
    purchase_order.save(update_fields=['total_amount'])
    return purchase_order