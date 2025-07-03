from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from tenants.models import Tenant


class ProductCategory(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='product_categories')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product Category'
        verbose_name_plural = 'Product Categories'
        unique_together = ('tenant', 'name')
        ordering = ['name']

    def __str__(self):
        return self.name


class ProductBrand(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='product_brands')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product Brand'
        verbose_name_plural = 'Product Brands'
        unique_together = ('tenant', 'name')
        ordering = ['name']

    def __str__(self):
        return self.name


class Attribute(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='attributes')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Attribute'
        verbose_name_plural = 'Attributes'
        unique_together = ('tenant', 'name')
        ordering = ['name']

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='attribute_values')
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Attribute Value'
        verbose_name_plural = 'Attribute Values'
        unique_together = ('tenant', 'attribute', 'value')
        ordering = ['attribute__name', 'value']

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class Product(models.Model):

    class UnitOfMeasure(models.TextChoices):
        UNIT = 'UN', 'Unidade'
        KILOGRAM = 'KG', 'Quilograma'
        GRAM = 'G', 'Grama'
        TON = 'T', 'Tonelada'
        LITER = 'L', 'Litro'
        MILLILITER = 'ML', 'Mililitro'
        METER = 'M', 'Metro'
        M2 = 'M2', 'Metro quadrado'
        M3 = 'M3', 'Metro cúbico'
        CENTIMETER = 'CM', 'Centímetro'
        MILLIMETER = 'MM', 'Milímetro'
        BOX = 'CX', 'Caixa'
        PACKAGE = 'PC', 'Pacote'
        DOZEN = 'DZ', 'Dúzia'
        UNIT_HOUR = 'H', 'Hora'
        DAY = 'D', 'Dia'
        ROLL = 'RL', 'Rolo'
        SHEET = 'FL', 'Folha'
        BOTTLE = 'BT', 'Garrafa'
        CAN = 'LT', 'Lata'
        TUBE = 'TB', 'Tubo'
        ENVELOPE = 'EN', 'Envelope'
        BAG = 'SC', 'Saco'

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='products')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='variants')
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, blank=True, null=True, related_name='products')
    brand = models.ForeignKey(ProductBrand, on_delete=models.SET_NULL, blank=True, null=True, related_name='products')
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_variant = models.BooleanField(default=False)
    is_composite = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    components = models.ManyToManyField('self', through='ProductComposition', symmetrical=False, related_name='composed_in', blank=True)
    attributes = models.ManyToManyField(AttributeValue, through='ProductAttributeValue', related_name='products', blank=True)
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=3, default=0.0)
    minimum_stock_quantity = models.DecimalField(max_digits=10, decimal_places=3, default=0.0)
    unit_of_measure = models.CharField(max_length=10, choices=UnitOfMeasure.choices, default=UnitOfMeasure.UNIT)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    avg_cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        unique_together = ('tenant', 'sku')
        ordering = ['name']
        constraints = [
            models.CheckConstraint(
                check=~models.Q(id=models.F('parent_id')),
                name='product_cannot_be_its_own_parent'
            )
        ]

    def clean(self):
        super().clean()

        if self.parent and self.parent.id == self.id:
            raise ValidationError("A product cannot be its own parent.")

        if self.is_variant and not self.parent:
            raise ValidationError({
                'is_variant': "A variant product must have a parent product associated.",
                'parent': "This field is required for variants."
            })

        if not self.is_variant and self.parent:
            raise ValidationError({
                'parent': "A product that is not a variant cannot have a parent.",
                'is_variant': "Check this option if this product is a variant."
            })

        if self.pk:
            if not self.is_composite and self.components.exists():
                raise ValidationError("A product that is not composite cannot have components.")

    def __str__(self):
        return self.name

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()

    def restore(self):
        self.deleted_at = None
        self.is_active = True
        self.save()


class ProductComposition(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='composition')
    component = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='composed_of')
    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product Composition'
        verbose_name_plural = 'Product Compositions'
        unique_together = ('product', 'component')


class ProductAttributeValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    attribute_value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product Attribute Value'
        verbose_name_plural = 'Product Attribute Values'
        unique_together = ('product', 'attribute_value')
