from django.core.management.base import BaseCommand
from products.models import Product
from classifier.hierarchical_classifier import HierarchicalClassifier


class Command(BaseCommand):

    help = "Test hierarchical classifier against all products"

    def handle(self, *args, **options):

        classifier = HierarchicalClassifier()

        products = Product.objects.all()

        total = products.count()
        classified = 0
        manual_review = 0

        manual_products = []

        self.stdout.write("")
        self.stdout.write("=" * 70)
        self.stdout.write("TESTING ALL PRODUCTS")
        self.stdout.write("=" * 70)
        self.stdout.write("")

        for product in products:

            result = classifier.classify(product)

            if result["manual_review"]:
                manual_review += 1

                if len(manual_products) < 50:
                    manual_products.append({
                        "name": product.product_name,
                        "category": product.product_category,
                        "subcategory": product.product_sub_category,
                    })

            else:
                classified += 1

        percentage = (
            (classified / total) * 100
            if total > 0
            else 0
        )

        self.stdout.write("")
        self.stdout.write("=" * 70)
        self.stdout.write("RESULTS")
        self.stdout.write("=" * 70)

        self.stdout.write(
            f"Total products       : {total}"
        )

        self.stdout.write(
            f"Automatically classified : {classified}"
        )

        self.stdout.write(
            f"Manual review        : {manual_review}"
        )

        self.stdout.write(
            f"Classification rate  : {percentage:.2f}%"
        )

        self.stdout.write("")
        self.stdout.write("=" * 70)
        self.stdout.write("MANUAL REVIEW EXAMPLES")
        self.stdout.write("=" * 70)

        for item in manual_products:

            self.stdout.write(
                f"\nProduct      : {item['name']}"
            )

            self.stdout.write(
                f"Category     : {item['category']}"
            )

            self.stdout.write(
                f"Subcategory  : {item['subcategory']}"
            )

        self.stdout.write("")
        self.stdout.write("=" * 70)