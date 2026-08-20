from django.core.management.base import BaseCommand
from django.db import transaction

from products.models import Product
from classifier.attribute_extractor import AttributeExtractor
from classifier.hierarchical_classifier import HierarchicalClassifier


class Command(BaseCommand):
    help = "Classify products in resumable batches and save results"

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            type=int,
            default=500,
            help="Number of products to process per batch",
        )

        parser.add_argument(
            "--reprocess",
            action="store_true",
            help="Reclassify products that are already classified",
        )

        parser.add_argument(
            "--check-images",
            action="store_true",
            help="Validate product image URLs during classification",
        )

        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Limit the number of products processed",
        )

    def handle(self, *args, **options):
        batch_size = options["batch_size"]
        reprocess = options["reprocess"]
        check_images = options["check_images"]
        limit = options["limit"]

        classifier = HierarchicalClassifier()
        attribute_extractor = AttributeExtractor(check_images=check_images)

        products = Product.objects.all().order_by("id")
        if limit:
            products = products[:limit]

        if not reprocess:
            products = products.exclude(
                classification_status="classified"
            )

        total = products.count()

        if total == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    "No products require classification."
                )
            )
            return

        self.stdout.write(
            f"Products to process: {total}"
        )
        self.stdout.write(
            f"Batch size: {batch_size}"
        )

        classified = 0
        manual_review = 0
        failed = 0

        start = 0

        while start < total:
            batch = list(
                products[
                    start:start + batch_size
                ]
            )

            self.stdout.write(
                f"\nProcessing batch "
                f"{start + 1}-{start + len(batch)}..."
            )

            for product in batch:
                try:
                    result = classifier.classify(product)
                    attributes = attribute_extractor.extract(
                                product,
                                result["category"] or "",
                            )

                    product.predicted_category = (
                        result["category"] or ""
                    )

                    product.predicted_attributes = attributes
                    product.confidence_score = result["confidence"]

                    product.alternative_categories = (
                        result.get("alternatives", [])
                        if result["confidence"] < 0.95
                        else []
                    )

                    product.manual_review = result[
                        "manual_review"
                    ]

                    product.classification_status = (
                        "manual_review"
                        if result["manual_review"]
                        else "classified"
                    )

                    product.save(
                        update_fields=[
                            "predicted_category",
                            "predicted_attributes",
                            "confidence_score",
                            "alternative_categories",
                            "manual_review",
                            "classification_status",
                            "updated_at",
                        ]
                    )

                    if result["manual_review"]:
                        manual_review += 1
                    else:
                        classified += 1

                except Exception as exc:
                    failed += 1

                    product.classification_status = "failed"
                    product.save(
                        update_fields=[
                            "classification_status",
                            "updated_at",
                        ]
                    )

                    self.stdout.write(
                        self.style.WARNING(
                            f"Failed product "
                            f"{product.product_number}: {exc}"
                        )
                    )

            start += batch_size

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Classification completed."
            )
        )

        self.stdout.write(
            f"Classified: {classified}"
        )
        self.stdout.write(
            f"Manual review: {manual_review}"
        )
        self.stdout.write(
            f"Failed: {failed}"
        )