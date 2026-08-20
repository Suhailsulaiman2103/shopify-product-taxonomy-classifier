import csv

from django.core.management.base import BaseCommand

from products.models import Product


class Command(BaseCommand):
    help = "Export classified products to CSV"

    def handle(self, *args, **options):
        filename = "classified_products.csv"

        products = Product.objects.all().order_by("id")

        with open(filename, "w", newline="", encoding="utf-8-sig") as csvfile:
            writer = csv.writer(csvfile)

            writer.writerow([
                "product_number",
                "product_name",
                "product_category",
                "product_sub_category",
                "predicted_category",
                "confidence_score",
                "classification_status",
                "manual_review",
            ])

            for product in products:
                writer.writerow([
                    product.product_number,
                    product.product_name,
                    product.product_category,
                    product.product_sub_category,
                    product.predicted_category,
                    product.confidence_score,
                    product.classification_status,
                    product.manual_review,
                ])

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS("Export completed!")
        )
        self.stdout.write(f"File: {filename}")
        self.stdout.write(f"Products exported: {products.count()}")