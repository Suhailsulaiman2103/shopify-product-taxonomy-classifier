from pathlib import Path

from django.core.management.base import BaseCommand
from taxonomy.models import TaxonomyCategory


class Command(BaseCommand):
    help = "Import Shopify Product Taxonomy categories"

    def handle(self, *args, **options):

        file_path = Path("data/categories.txt")

        if not file_path.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"File not found: {file_path}"
                )
            )
            return

        imported = 0
        skipped = 0

        # Read the Shopify taxonomy file
        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            for line_number, line in enumerate(file, start=1):

                line = line.strip()

                # Ignore empty lines
                if not line:
                    continue

                # Ignore comments
                if line.startswith("#"):
                    continue

                try:
                    # IMPORTANT:
                    # Shopify format is:
                    #
                    # gid://shopify/TaxonomyCategory/ap : Animals & Pet Supplies
                    #
                    # We must split on " : " rather than ":"
                    # because the GID itself contains "://".

                    if " : " not in line:
                        skipped += 1
                        continue

                    gid, category_path = line.split(
                        " : ",
                        1
                    )

                    gid = gid.strip()
                    category_path = category_path.strip()

                    # Split hierarchy
                    parts = [
                        part.strip()
                        for part in category_path.split(">")
                    ]

                    if not parts:
                        skipped += 1
                        continue

                    category_name = parts[-1]

                    full_path = " > ".join(parts)

                    # Find the parent category
                    parent = None

                    if len(parts) > 1:

                        parent_path = " > ".join(parts[:-1])

                        parent = (
                            TaxonomyCategory.objects
                            .filter(full_path=parent_path)
                            .first()
                        )

                    # Create or update category
                    TaxonomyCategory.objects.update_or_create(
                        category_id=gid,
                        defaults={
                            "name": category_name,
                            "parent": parent,
                            "full_path": full_path,
                        }
                    )

                    imported += 1

                except Exception as e:

                    skipped += 1

                    self.stdout.write(
                        self.style.WARNING(
                            f"Skipped line {line_number}: {e}"
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Taxonomy import complete: "
                f"{imported} imported, "
                f"{skipped} skipped."
            )
        )