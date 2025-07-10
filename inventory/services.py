from decimal import Decimal
from typing import Any, Dict, List

from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction

from products.models import Product
from purchases.models import PurchaseOrder
from suppliers.models import Supplier
from tenants.models import Tenant
from users.models import User

from .models import (StockAdjustment, StockAdjustmentItem, StockEntry,
                     StockEntryItem, StockMovement)


class InventoryError(Exception):
    """Custom exception for inventory-related errors."""
    pass


@transaction.atomic
def _create_stock_movement(
    *,
    tenant: Tenant,
    product: Product,
    direction: str,
    quantity: Decimal,
    source_document: models.Model,
    user: User,
    unit_price: Decimal = None,
    notes: str = None
) -> StockMovement:
    """
    Create a stock movement record.

    Args:
        tenant (Tenant): The tenant associated with the stock movement.
        product (Product): The product involved in the stock movement.
        direction (str): The direction of the movement ('IN' or 'OUT').
        quantity (Decimal): The quantity of the product being moved.
        source_document (models.Model): The document that initiated the movement.
        user (User): The user performing the action.
        unit_price (Decimal, optional): The unit price of the product. Defaults to None.
        notes (str, optional): Additional notes for the movement. Defaults to None.

    Returns:
        StockMovement: The created stock movement record.
    """
    if quantity <= 0:
        raise InventoryError("Quantity must be greater than zero.")

    product = Product.objects.select_for_update().get(pk=product.id, tenant=tenant)

    if direction == StockMovement.MovementDirection.IN:
        new_stock = product.stock_quantity + quantity
    elif direction == StockMovement.MovementDirection.OUT:
        if product.stock_quantity < quantity:
            raise InventoryError("Insufficient stock for product {}".format(product.name))
        new_stock = product.stock_quantity - quantity
    else:
        raise InventoryError("Invalid movement direction: {}".format(direction))

    product.stock_quantity = new_stock
    product.save(update_fields=['stock_quantity'])

    content_type = ContentType.objects.get_for_model(source_document)
    movement = StockMovement.objects.create(
        tenant=tenant,
        product=product,
        direction=direction,
        quantity=quantity,
        new_stock=new_stock,
        unit_price=unit_price,
        source_content_type=content_type,
        source_object_id=source_document.id,
        user=user,
        notes=notes
    )

    return movement


@transaction.atomic
def create_stock_entry(
    *,
    tenant: Tenant,
    user: User,
    items_data: List[Dict[str, Any]],
    purchase: PurchaseOrder = None,
    supplier: Supplier = None,
    status: str = StockEntry.StockEntryStatus.DRAFT,
    notes: str = None
) -> StockEntry:
    """
    Create a stock entry with associated items. If the stock entry is approved,
    it will create stock movements for each item.

    Args:
        tenant (Tenant): The tenant associated with the stock entry.
        user (User): The user creating the stock entry.
        items_data (List[Dict[str, Any]]): List of dictionaries containing item data ('product', 'quantity', 'unit_price', 'expiration_date').
        purchase (PurchaseOrder, optional): Associated purchase order. Defaults to None.
        supplier (Supplier, optional): Associated supplier. Defaults to None.
        status (str, optional): Status of the stock entry. Defaults to StockEntryStatus.DRAFT.
        notes (str, optional): Additional notes for the stock entry. Defaults to None.

    Returns:
        StockEntry: The created stock entry.
    """
    stock_entry = StockEntry.objects.create(
        tenant=tenant,
        user=user,
        purchase=purchase,
        supplier=supplier,
        status=StockEntry.StockEntryStatus.DRAFT,
        notes=notes
    )

    for item_data in items_data:
        StockEntryItem.objects.create(
            tenant=tenant,
            stock_entry=stock_entry,
            product=item_data['product'],
            quantity=item_data['quantity'],
            unit_price=item_data['unit_price'],
            expiration_date=item_data.get('expiration_date', None)
        )

        if status == StockEntry.StockEntryStatus.COMPLETED:
            stock_entry = complete_stock_entry(
                tenant=tenant,
                stock_entry=stock_entry,
                user=user
            )

    return stock_entry


@transaction.atomic
def complete_stock_entry(
    *,
    tenant: Tenant,
    stock_entry: StockEntry,
    user: User
) -> StockEntry:
    """
    Complete a stock entry, changing its status to COMPLETED and creating stock movements.
    """
    if stock_entry.status != StockEntry.StockEntryStatus.DRAFT:
        raise InventoryError("Only draft stock entries can be completed.")

    for item in stock_entry.items.all():
        _create_stock_movement(
            tenant=tenant,
            product=item.product,
            direction=StockMovement.MovementDirection.IN,
            quantity=item.quantity,
            source_document=item,
            user=user,
            unit_price=item.unit_price,
            notes=f"Entrada de estoque #{stock_entry.id} - {item.product.name}"
        )

    stock_entry.status = StockEntry.StockEntryStatus.COMPLETED
    stock_entry.save(update_fields=['status'])
    return stock_entry


@transaction.atomic
def create_stock_adjustment(
    *,
    tenant: Tenant,
    user: User,
    items_data: List[Dict[str, Any]],
    status: str = StockAdjustment.StockAdjustmentStatus.DRAFT,
    notes: str = None,
) -> StockAdjustment:
    """
    Create a stock adjustment with associated items. If the adjustment is approved,
    it will create stock movements for each item.

    Args:
        tenant (Tenant): The tenant associated with the stock adjustment.
        user (User): The user creating the stock adjustment.
        items_data (List[Dict[str, Any]]): List of dictionaries containing item data ('product', 'adjustment_type', 'quantity', 'notes').
        status (str, optional): Status of the stock adjustment. Defaults to StockAdjustmentStatus.DRAFT.
        notes (str, optional): Additional notes for the stock adjustment. Defaults to None.

    Returns:
        StockAdjustment: The created stock adjustment.
    """
    stock_adjustment = StockAdjustment.objects.create(
        tenant=tenant,
        user=user,
        status=status,
        notes=notes
    )

    for item_data in items_data:
        adjustment_type = item_data['adjustment_type']
        item = StockAdjustmentItem.objects.create(
            tenant=tenant,
            stock_adjustment=stock_adjustment,
            product=item_data['product'],
            adjustment_type=adjustment_type,
            quantity=item_data['quantity'],
            notes=item_data.get('notes', None)
        )

        if status == StockAdjustment.StockAdjustmentStatus.COMPLETED:
            _create_stock_movement(
                tenant=tenant,
                product=item.product,
                direction=adjustment_type.direction,
                quantity=item.quantity,
                source_document=item,
                user=user,
                notes=item.notes or f"Ajuste de estoque #{stock_adjustment.id} - {item.product.name}"
            )

    return stock_adjustment


@transaction.atomic
def complete_stock_adjustment(
    *,
    tenant: Tenant,
    stock_adjustment: StockAdjustment,
    user: User
) -> StockAdjustment:
    """
    Complete a stock adjustment, changing its status to COMPLETED and creating stock movements.
    """
    if stock_adjustment.status != StockAdjustment.StockAdjustmentStatus.DRAFT:
        raise InventoryError("Only draft stock adjustments can be completed.")

    for item in stock_adjustment.items.all():
        _create_stock_movement(
            tenant=tenant,
            product=item.product,
            direction=item.adjustment_type.direction,
            quantity=item.quantity,
            source_document=item,
            user=user,
            notes=f"Ajuste de estoque #{stock_adjustment.id} - {item.product.name}"
        )

    stock_adjustment.status = StockAdjustment.StockAdjustmentStatus.COMPLETED
    stock_adjustment.save(update_fields=['status'])
    return stock_adjustment
