import json

from django.test import TestCase
from django.urls import reverse

from products.models import Product

from taxonomy.models import TaxonomyCategory

from classifier.hierarchical_classifier import HierarchicalClassifier
from classifier.image_service import ImageService



class HierarchicalClassifierTests(TestCase):

    def setUp(self):
        # Create only the taxonomy categories required by these tests
        TaxonomyCategory.objects.create(
            name="Table Lamps",
            full_path="Home & Garden > Lighting > Lamps > Table Lamps",
            category_id="test-table-lamps"
        )

        TaxonomyCategory.objects.create(
            name="Floor Lamps",
            full_path="Home & Garden > Lighting > Lamps > Floor Lamps",
            category_id="test-floor-lamps"
        )

        TaxonomyCategory.objects.create(
            name="Throw Pillows",
            full_path="Home & Garden > Decor > Throw Pillows",
            category_id="test-throw-pillows"
        )

        self.classifier = HierarchicalClassifier()

    def test_table_lamp_classification(self):
        product = Product(
            product_name="Inspect Table Lamp by Modway",
            product_sub_category="Table Lamps"
        )

        result = self.classifier.classify(product)

        self.assertEqual(
            result["category"],
            "Home & Garden > Lighting > Lamps > Table Lamps"
        )
        self.assertFalse(result["manual_review"])

    def test_floor_lamp_classification(self):
        product = Product(
            product_name="Journey Standing Floor Lamp by Modway",
            product_sub_category="Floor Lamps"
        )

        result = self.classifier.classify(product)

        self.assertEqual(
            result["category"],
            "Home & Garden > Lighting > Lamps > Floor Lamps"
        )
        self.assertFalse(result["manual_review"])

    def test_throw_pillow_classification(self):
        product = Product(
            product_name='Enhance 24" Performance Velvet Throw Pillow by Modway',
            product_sub_category="Pillow"
        )

        result = self.classifier.classify(product)

        self.assertEqual(
            result["category"],
            "Home & Garden > Decor > Throw Pillows"
        )
        self.assertFalse(result["manual_review"])

    def test_counter_bar_stool_priority(self):
        TaxonomyCategory.objects.create(
            name="Counter Stools",
            full_path="Furniture > Chairs > Table & Bar Stools > Counter Stools",
            category_id="test-counter-stools"
        )

        self.classifier = HierarchicalClassifier()

        product = Product(
            product_name="Baronet Upholstered Fabric Counter Bar Stool Set of 2 by Modway",
            product_sub_category="Bar and Counter Stools"
        )

        result = self.classifier.classify(product)

        self.assertEqual(
            result["category"],
            "Furniture > Chairs > Table & Bar Stools > Counter Stools"
        )

    def test_desk_file_cabinet_set_priority(self):
        TaxonomyCategory.objects.create(
            name="Computer Desks",
            full_path="Furniture > Office Furniture > Desks > Computer Desks",
            category_id="test-computer-desks"
        )

        TaxonomyCategory.objects.create(
            name="File Cabinets",
            full_path="Furniture > Cabinets & Storage > File Cabinets",
            category_id="test-file-cabinets"
        )

        self.classifier = HierarchicalClassifier()

        product = Product(
            product_name="Render Wood Desk and File Cabinet Set by Modway",
            product_sub_category="Computer Desks"
        )

        result = self.classifier.classify(product)

        self.assertEqual(
            result["category"],
            "Furniture > Office Furniture > Desks > Computer Desks"
        )

    def test_sideboard_tv_stand_priority(self):
        TaxonomyCategory.objects.create(
            name="Sideboards",
            full_path="Furniture > Cabinets & Storage > Sideboards",
            category_id="test-sideboards"
        )

        TaxonomyCategory.objects.create(
            name="TV Stands",
            full_path="Furniture > Entertainment Centers & TV Stands",
            category_id="test-tv-stands"
        )

        self.classifier = HierarchicalClassifier()

        product = Product(
            product_name='Render 63" Sideboard Buffet Table or TV Stand by Modway',
            product_sub_category=""
        )

        result = self.classifier.classify(product)

        self.assertEqual(
            result["category"],
            "Furniture > Cabinets & Storage > Sideboards"
        )

    def test_chandelier_over_pendant_priority(self):
        TaxonomyCategory.objects.create(
            name="Chandeliers",
            full_path="Home & Garden > Lighting > Lighting Fixtures > Chandeliers",
            category_id="test-chandeliers"
        )

        TaxonomyCategory.objects.create(
            name="Pendant Lights",
            full_path="Home & Garden > Lighting > Lighting Fixtures > Pendant Light Fixtures",
            category_id="test-pendant-lights"
        )

        self.classifier = HierarchicalClassifier()

        product = Product(
            product_name="Peak Brass Cone and Glass Globe Cluster Pendant Chandelier by Modway",
            product_sub_category="Ceiling Lamps"
        )

        result = self.classifier.classify(product)

        self.assertEqual(
            result["category"],
            "Home & Garden > Lighting > Lighting Fixtures > Chandeliers"
        )

class ClassificationAPITests(TestCase):

    def setUp(self):
        self.product = Product.objects.create(
            product_number="TEST-001",
            product_name="Test Sofa",
            product_category="Living Room",
            product_sub_category="Sofas and Armchairs",
            predicted_category="Furniture > Sofas",
            predicted_attributes={
                "color": "White",
            },
            confidence_score=0.95,
            alternative_categories=[],
            classification_status="classified",
            manual_review=False,
        )

    def test_classification_list(self):
        response = self.client.get(
            reverse("classification-list")
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(data["count"], 1)
        self.assertEqual(
            data["results"][0]["product_number"],
            "TEST-001",
        )

    def test_classification_detail(self):
        response = self.client.get(
            reverse(
                "classification-detail",
                args=[self.product.id],
            )
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(
            data["predicted_category"],
            "Furniture > Sofas",
        )

    def test_approve_classification(self):
        response = self.client.post(
            reverse(
                "classification-approve",
                args=[self.product.id],
            )
        )

        self.assertEqual(response.status_code, 200)

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.classification_status,
            "approved",
        )

        self.assertFalse(
            self.product.manual_review
        )

    def test_update_classification(self):
        new_category = (
            "Furniture > Sofas > Loveseat Sofas"
        )

        response = self.client.post(
            reverse(
                "classification-update",
                args=[self.product.id],
            ),
            data=json.dumps({
                "predicted_category": new_category,
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.predicted_category,
            new_category,
        )

        self.assertEqual(
            self.product.classification_status,
            "approved",
        )

class ImageServiceTests(TestCase):

    def test_missing_image_is_handled(self):
        product = Product(
            product_number="IMG-001",
            product_name="Product Without Image",
        )

        service = ImageService()

        result = service.get_image_analysis(
            product
        )

        self.assertFalse(
            result["available"]
        )

        self.assertEqual(
            result["status"],
            "missing",
        )

    def test_invalid_image_url_is_handled(self):
        product = Product(
            product_number="IMG-002",
            product_name="Invalid Image Product",
            image_1="not-a-valid-url",
        )

        service = ImageService()

        result = service.get_image_analysis(
            product
        )

        self.assertFalse(
            result["available"]
        )

        self.assertEqual(
            result["status"],
            "invalid",
        )