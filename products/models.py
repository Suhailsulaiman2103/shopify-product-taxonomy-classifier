from django.db import models


class Product(models.Model):
    product_number = models.CharField(max_length=100, unique=True)
    model_number = models.CharField(max_length=100, blank=True)

    product_category = models.CharField(max_length=255, blank=True)
    product_sub_category = models.CharField(max_length=255, blank=True)

    collection_name = models.CharField(max_length=255, blank=True)
    color_collection = models.CharField(max_length=255, blank=True)
    product_color = models.CharField(max_length=255, blank=True)

    product_name = models.CharField(max_length=500)
    product_description = models.TextField(blank=True)
    bullets = models.TextField(blank=True)

    set_includes = models.TextField(blank=True)
    product_weight = models.CharField(max_length=100, blank=True)

    materials = models.TextField(blank=True)

    # Changed from CharField to TextField
    product_dimensions = models.TextField(blank=True)

    assembly_required = models.CharField(max_length=100, blank=True)
    is_set = models.CharField(max_length=100, blank=True)
    stackable = models.CharField(max_length=100, blank=True)

    country_of_origin = models.CharField(max_length=255, blank=True)

    item_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    map_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    msrp = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    image_1 = models.URLField(max_length=1000, blank=True)
    image_2 = models.URLField(max_length=1000, blank=True)
    image_3 = models.URLField(max_length=1000, blank=True)
    image_4 = models.URLField(max_length=1000, blank=True)
    image_5 = models.URLField(max_length=1000, blank=True)

    product_url = models.URLField(max_length=1000, blank=True)

    # Shipping information
    shipping_method = models.CharField(max_length=255, blank=True)
    total_box_count = models.CharField(max_length=100, blank=True)
    pallet_count = models.CharField(max_length=100, blank=True)
    shipping_weight = models.CharField(max_length=100, blank=True)
    total_cbm = models.CharField(max_length=100, blank=True)

    # Changed from CharField to TextField
    package_dimensions = models.TextField(blank=True)

    # Classification fields
    predicted_category = models.CharField(
        max_length=500,
        blank=True
    )

    predicted_attributes = models.JSONField(
        default=dict,
        blank=True
    )

    confidence_score = models.FloatField(
        null=True,
        blank=True
    )

    alternative_categories = models.JSONField(
        default=list,
        blank=True
    )

    classification_status = models.CharField(
        max_length=50,
        default="pending"
    )

    manual_review = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.product_name