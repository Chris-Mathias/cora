from decimal import Decimal

import pytest
from django.utils import timezone

from inventory.models import (StockAdjustment, StockAdjustmentType, StockEntry,
                              StockMovement)
from inventory.services import (InventoryError, create_stock_adjustment,
                                create_stock_entry)
from products.models import Product
from purchases.models import PurchaseOrder, PurchaseOrderStatus
from suppliers.models import Supplier
from tenants.models import Tenant
from users.models import User


@pytest.fixture
def tenant(db):
    return Tenant.objects.create(name="Tenant Test")


@pytest.fixture
def user(db):
    return User.objects.create_user(email="user@test.com", password="123456", name="User Test")


@pytest.fixture
def product(db, tenant):
    return Product.objects.create(
        tenant=tenant,
        name="Produto Teste",
        stock_quantity=10,
        sku="SKU001",
        price=Decimal("20.00")
    )


@pytest.fixture
def supplier(db, tenant):
    return Supplier.objects.create(
        tenant=tenant,
        name="Fornecedor Teste"
    )


@pytest.fixture
def purchase_order_status(db, tenant):
    return PurchaseOrderStatus.objects.create(
        tenant=tenant,
        name="OPEN",
        label="Aberto",
        sequence_order=1
    )


@pytest.fixture
def purchase_order(db, tenant, supplier, purchase_order_status):
    return PurchaseOrder.objects.create(
        tenant=tenant,
        supplier=supplier,
        status=purchase_order_status,
        expected_delivery_date=timezone.now().date()
    )


@pytest.fixture
def stock_adjustment_type_increase(db, tenant):
    return StockAdjustmentType.objects.create(
        tenant=tenant,
        name="INCREASE",
        label="Aumento",
        direction="IN"
    )


@pytest.fixture
def stock_adjustment_type_decrease(db, tenant):
    return StockAdjustmentType.objects.create(
        tenant=tenant,
        name="DECREASE",
        label="Redução",
        direction="OUT"
    )


def test_create_stock_entry_creates_movement_and_updates_stock(
    tenant, user, product, supplier, purchase_order
):
    items_data = [
        {
            "product": product,
            "quantity": Decimal("5"),
            "unit_price": Decimal("15.00"),
            "expiration_date": timezone.now().date(),
        }
    ]

    stock_entry = create_stock_entry(
        tenant=tenant,
        user=user,
        items_data=items_data,
        purchase=purchase_order,
        supplier=supplier,
        status=StockEntry.StockEntryStatus.COMPLETED,
        notes="Teste entrada estoque"
    )

    product.refresh_from_db()
    assert product.stock_quantity == Decimal("15")
    assert stock_entry.status == StockEntry.StockEntryStatus.COMPLETED
    assert stock_entry.items.count() == 1

    item = stock_entry.items.first()
    movement = StockMovement.objects.get(source_object_id=item.id)
    assert movement.direction == StockMovement.MovementDirection.IN
    assert movement.quantity == Decimal("5")
    assert movement.product == product
    assert movement.user == user
    assert movement.notes is not None


def test_create_stock_adjustment_increase_and_decrease(
    tenant, user, product, stock_adjustment_type_increase, stock_adjustment_type_decrease
):
    items_data_inc = [
        {
            "product": product,
            "adjustment_type": stock_adjustment_type_increase,
            "quantity": Decimal("3"),
            "notes": "Ajuste positivo"
        }
    ]

    adjustment_inc = create_stock_adjustment(
        tenant=tenant,
        user=user,
        items_data=items_data_inc,
        status=StockAdjustment.StockAdjustmentStatus.COMPLETED,
        notes="Ajuste entrada"
    )

    product.refresh_from_db()
    assert adjustment_inc.status == StockAdjustment.StockAdjustmentStatus.COMPLETED
    assert product.stock_quantity == Decimal("13")

    items_data_dec = [
        {
            "product": product,
            "adjustment_type": stock_adjustment_type_decrease,
            "quantity": Decimal("5"),
            "notes": "Ajuste negativo"
        }
    ]

    adjustment_dec = create_stock_adjustment(
        tenant=tenant,
        user=user,
        items_data=items_data_dec,
        status=StockAdjustment.StockAdjustmentStatus.COMPLETED,
        notes="Ajuste saída"
    )

    product.refresh_from_db()
    assert adjustment_dec.status == StockAdjustment.StockAdjustmentStatus.COMPLETED
    assert product.stock_quantity == Decimal("8")


def test_create_stock_adjustment_raises_error_on_insufficient_stock(
    tenant, user, product, stock_adjustment_type_decrease
):
    items_data = [
        {
            "product": product,
            "adjustment_type": stock_adjustment_type_decrease,
            "quantity": Decimal("1000"),
            "notes": "Ajuste saída inválido"
        }
    ]

    with pytest.raises(InventoryError):
        create_stock_adjustment(
            tenant=tenant,
            user=user,
            items_data=items_data,
            status=StockAdjustment.StockAdjustmentStatus.COMPLETED,
            notes="Teste erro"
        )


def test_create_stock_entry_draft_does_not_change_stock(
    tenant, user, product, supplier
):
    items_data = [
        {
            "product": product,
            "quantity": Decimal("7"),
            "unit_price": Decimal("12.00"),
            "expiration_date": timezone.now().date(),
        }
    ]

    stock_entry = create_stock_entry(
        tenant=tenant,
        user=user,
        items_data=items_data,
        supplier=supplier,
        status=StockEntry.StockEntryStatus.DRAFT,
        notes="Rascunho entrada"
    )

    product.refresh_from_db()
    assert product.stock_quantity == Decimal("10")
    assert stock_entry.status == StockEntry.StockEntryStatus.DRAFT


def test_create_stock_adjustment_draft_does_not_change_stock(
    tenant, user, product, stock_adjustment_type_increase
):
    items_data = [
        {
            "product": product,
            "adjustment_type": stock_adjustment_type_increase,
            "quantity": Decimal("5"),
            "notes": "Rascunho ajuste"
        }
    ]

    adjustment = create_stock_adjustment(
        tenant=tenant,
        user=user,
        items_data=items_data,
        status=StockAdjustment.StockAdjustmentStatus.DRAFT,
        notes="Rascunho"
    )

    product.refresh_from_db()
    assert product.stock_quantity == Decimal("10")
    assert adjustment.status == StockAdjustment.StockAdjustmentStatus.DRAFT


def test_create_stock_entry_with_zero_quantity_raises_error(tenant, user, product):
    items_data = [{"product": product, "quantity": Decimal("0"), "unit_price": Decimal("10.00")}]
    with pytest.raises(InventoryError, match="Quantity must be greater than zero."):
        create_stock_entry(
            tenant=tenant,
            user=user,
            items_data=items_data,
            status=StockEntry.StockEntryStatus.COMPLETED
        )
