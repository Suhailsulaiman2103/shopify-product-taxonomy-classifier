import pandas as pd

from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = "Import products from Excel file"

    def handle(self, *args, **options):

        file_path = "Product List.xlsx"

        df = pd.read_excel(file_path)

        self.stdout.write(
            f"Found {len(df)} products."
        )

        imported = 0
        skipped = 0

        for _, row in df.iterrows():

            try:
                product_number = str(
                    row["Product Number"]
                ).strip()

                if not product_number:
                    skipped += 1
                    continue

                Product.objects.update_or_create(
                    product_number=product_number,
                    defaults={
                        "model_number": self.clean_value(
                            row["Model Number"]
                        ),

                        "product_category": self.clean_value(
                            row["Product Category"]
                        ),

                        "product_sub_category": self.clean_value(
                            row["Product Sub Category"]
                        ),

                        "collection_name": self.clean_value(
                            row["Collection Name"]
                        ),

                        "color_collection": self.clean_value(
                            row["Color Collection"]
                        ),

                        "product_color": self.clean_value(
                            row["Product Color"]
                        ),

                        "product_name": self.clean_value(
                            row["Product Name"]
                        ),

                        "product_description": self.clean_value(
                            row["Product Description "]
                        ),

                        "bullets": self.clean_value(
                            row["Bullets"]
                        ),

                        "set_includes": self.clean_value(
                            row["Set Includes"]
                        ),

                        "product_weight": self.clean_value(
                            row["Product Weight"]
                        ),

                        "materials": self.clean_value(
                            row["Materials"]
                        ),

                        "product_dimensions": self.clean_value(
                            row["Product Dimensions"]
                        ),

                        "assembly_required": self.clean_value(
                            row["Assembly Required"]
                        ),

                        "is_set": self.clean_value(
                            row["Is a Set"]
                        ),

                        "stackable": self.clean_value(
                            row["Stackable"]
                        ),

                        "country_of_origin": self.clean_value(
                            row["Country Of Origin"]
                        ),

                        "item_cost": self.clean_number(
                            row["Item Cost"]
                        ),

                        "map_price": self.clean_number(
                            row["MAP"]
                        ),

                        "msrp": self.clean_number(
                            row["MSRP"]
                        ),

                        "image_1": self.clean_value(
                            row["Image 1"]
                        ),

                        "image_2": self.clean_value(
                            row["Image 2"]
                        ),

                        "image_3": self.clean_value(
                            row["Image 3"]
                        ),

                        "image_4": self.clean_value(
                            row["Image 4"]
                        ),

                        "image_5": self.clean_value(
                            row["Image 5"]
                        ),

                        "product_url": self.clean_value(
                            row["Product URL"]
                        ),

                        "shipping_method": self.clean_value(
                            row["Shipping Method"]
                        ),

                        "total_box_count": self.clean_value(
                            row["Total Box Count"]
                        ),

                        "pallet_count": self.clean_value(
                            row["Pallet Count"]
                        ),

                        "shipping_weight": self.clean_value(
                            row["Shipping Weight"]
                        ),

                        "total_cbm": self.clean_value(
                            row["Total CBM"]
                        ),

                        "package_dimensions": self.clean_value(
                            row["Package Dimensions"]
                        ),
                    }
                )

                imported += 1

            except Exception as e:

                skipped += 1

                self.stdout.write(
                    self.style.WARNING(
                        f"Skipped row: {e}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete: {imported} imported, "
                f"{skipped} skipped."
            )
        )

    @staticmethod
    def clean_value(value):

        if pd.isna(value):
            return ""

        return str(value).strip()

    @staticmethod
    def clean_number(value):

        if pd.isna(value):
            return None

        try:
            return float(value)

        except (ValueError, TypeError):
            return None