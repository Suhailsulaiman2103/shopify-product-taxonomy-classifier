import re

from classifier.image_service import ImageService


class AttributeExtractor:
    """Extract common and category-aware attributes from product data."""

    BOOLEAN_MAP = {
        "y": "Yes",
        "yes": "Yes",
        "true": "Yes",
        "1": "Yes",
        "n": "No",
        "no": "No",
        "false": "No",
        "0": "No",
    }

    UPHOLSTERY_KEYWORDS = (
        "velvet",
        "fabric",
        "leather",
        "faux leather",
        "vegan leather",
        "vinyl",
        "boucle",
        "linen",
    )

    TABLE_SHAPES = (
        "round",
        "oval",
        "square",
        "rectangle",
        "rectangular",
    )

    def __init__(self, check_images=False):
        self.check_images = check_images
        self.image_service = ImageService()

    def extract(self, product, predicted_category=""):
        attributes = {}

        # Common product attributes
        self._add_if_present(
            attributes,
            "color",
            product.product_color,
        )

        self._add_if_present(
            attributes,
            "materials",
            product.materials,
        )

        self._add_boolean_attribute(
            attributes,
            "assembly_required",
            product.assembly_required,
        )

        self._add_boolean_attribute(
            attributes,
            "is_set",
            product.is_set,
        )

        self._add_boolean_attribute(
            attributes,
            "stackable",
            product.stackable,
        )

        self._add_if_present(
            attributes,
            "collection",
            product.collection_name,
        )

        self._add_if_present(
            attributes,
            "product_type",
            product.product_sub_category,
        )

        brand = self._detect_brand(
            product.product_name
        )

        if brand:
            attributes["brand"] = brand

        category_attributes = self._extract_category_attributes(
            product,
            predicted_category,
        )

        if category_attributes:
            attributes["category_specific"] = category_attributes

        # Image validation is optional because it requires network access.
        if self.check_images:
            image_analysis = (
                self.image_service.get_image_analysis(
                    product
                )
            )

            attributes["image_status"] = image_analysis

            if (
                not attributes.get("color")
                and image_analysis.get("visual_color")
            ):
                attributes["image_inferred_color"] = (
                    image_analysis["visual_color"]
                )

        return attributes

    def _extract_category_attributes(
        self,
        product,
        predicted_category,
    ):
        attributes = {}

        product_name = (
            product.product_name or ""
        ).lower()

        materials = (
            product.materials or ""
        ).strip()

        category = (
            predicted_category or ""
        ).lower()

        # Sofas and chairs
        if (
            "sofa" in category
            or "chair" in category
            or "stool" in category
        ):
            upholstery = self._detect_upholstery(
                product_name,
                materials,
            )

            if upholstery:
                attributes["upholstery_material"] = upholstery

            quantity = self._detect_set_quantity(
                product_name
            )

            if quantity:
                attributes["set_quantity"] = quantity

        # Tables
        if "table" in category:
            shape = self._detect_table_shape(
                product_name
            )

            if shape:
                attributes["table_shape"] = shape

            quantity = self._detect_set_quantity(
                product_name
            )

            if quantity:
                attributes["set_quantity"] = quantity

        # Bathroom sinks
        if "bathroom sink" in category:
            if "double basin" in product_name:
                attributes["basin_count"] = 2
            elif "single basin" in product_name:
                attributes["basin_count"] = 1

        # Lamps and lighting
        if (
            "lighting" in category
            or "lamp" in category
        ):
            if materials:
                attributes["fixture_material"] = materials

        # Outdoor furniture
        if "outdoor furniture" in category:
            attributes["outdoor_use"] = "Yes"

        return attributes

    def _detect_upholstery(
        self,
        product_name,
        materials,
    ):
        combined = (
            f"{product_name} {materials}"
        ).lower()

        # Check longer phrases first.
        for keyword in sorted(
            self.UPHOLSTERY_KEYWORDS,
            key=len,
            reverse=True,
        ):
            if keyword in combined:
                return keyword.title()

        return None

    @staticmethod
    def _detect_set_quantity(product_name):
        patterns = [
            r"\bset\s+of\s+(\d+)\b",
            r"\b(\d+)\s+piece\b",
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                product_name,
            )

            if match:
                return int(match.group(1))

        return None

    def _detect_table_shape(self, product_name):
        for shape in self.TABLE_SHAPES:
            if re.search(
                rf"\b{re.escape(shape)}\b",
                product_name,
            ):
                if shape == "rectangular":
                    return "Rectangle"

                return shape.title()

        return None

    @staticmethod
    def _add_if_present(
        attributes,
        key,
        value,
    ):
        if value is None:
            return

        value = str(value).strip()

        if value:
            attributes[key] = value

    def _add_boolean_attribute(
        self,
        attributes,
        key,
        value,
    ):
        if value is None:
            return

        value = str(value).strip()

        if not value:
            return

        attributes[key] = self.BOOLEAN_MAP.get(
            value.lower(),
            value,
        )
    @staticmethod
    def _detect_brand(product_name):
        if not product_name:
            return None

        match = re.search(
            r"\bby\s+(.+?)\s*$",
            product_name,
            flags=re.IGNORECASE,
        )

        if match:
            return match.group(1).strip()

        return None