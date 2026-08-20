"""Rule-based hierarchical classifier for mapping products to Shopify taxonomy categories."""

import re

from taxonomy.models import TaxonomyCategory


class HierarchicalClassifier:
    """Classify products using source-aware keyword rules and Shopify taxonomy paths."""

    # Taxonomy paths
    TAXONOMY = {'sofa': 'Furniture > Sofas',
     'armchair': 'Furniture > Chairs > Armchairs, Recliners & Sleeper Chairs > Armchairs',
     'ottoman': 'Furniture > Ottomans',
     'bar_stool': 'Furniture > Chairs > Table & Bar Stools > Bar Stools',
     'dining_chair': 'Furniture > Chairs > Kitchen & Dining Room Chairs > Dining Chairs',
     'dining_table': 'Furniture > Tables > Kitchen & Dining Room Tables > Dining Tables',
     'office_chair': 'Furniture > Office Furniture > Office Chairs',
     'gaming_chair': 'Furniture > Chairs > Gaming Chairs',
     'storage_cabinet': 'Furniture > Cabinets & Storage > Storage Cabinets & Lockers > Storage '
                    'Cabinets',
     'wall_shelf': 'Furniture > Shelving > Wall Shelves & Ledges',
     'trash_can': 'Home & Garden > Household Supplies > Waste Containment > Trash Cans & Wastebaskets '
              '> Trash Cans',
     'wastebasket': 'Home & Garden > Household Supplies > Waste Containment > Trash Cans & '
                'Wastebaskets > Wastebaskets',
     'pen_holder': 'Office Supplies > Filing & Organization > Desk Organizers > Pen Holders',
     'outdoor_chair': 'Furniture > Outdoor Furniture > Outdoor Seating > Outdoor Chairs',
     'outdoor_rocking_chair': 'Furniture > Outdoor Furniture > Outdoor Seating > Outdoor Chairs > '
                          'Rocking Chairs',
     'outdoor_folding_chair': 'Furniture > Outdoor Furniture > Outdoor Seating > Outdoor Chairs > '
                          'Folding Chairs',
     'outdoor_sofa': 'Furniture > Outdoor Furniture > Outdoor Seating > Outdoor Sofas',
     'outdoor_sectional': 'Furniture > Outdoor Furniture > Outdoor Seating > Outdoor Sofas > Sectional '
                      'Sofas',
     'outdoor_sectional_unit': 'Furniture > Outdoor Furniture > Outdoor Seating > Outdoor Sectional '
                           'Sofa Units',
     'outdoor_loveseat': 'Furniture > Outdoor Furniture > Outdoor Seating > Outdoor Sofas > Loveseat '
                     'Sofas',
     'outdoor_bench': 'Furniture > Outdoor Furniture > Outdoor Seating > Outdoor Benches',
     'outdoor_ottoman': 'Furniture > Outdoor Furniture > Outdoor Ottomans',
     'outdoor_daybed': 'Furniture > Outdoor Furniture > Outdoor Beds > Daybeds',
     'outdoor_chaise': 'Furniture > Chairs > Chaises',
     'outdoor_furniture_set': 'Furniture > Outdoor Furniture > Outdoor Furniture Sets',
     'outdoor_pillow': 'Home & Garden > Decor > Throw Pillows',
     'bathroom_vanity': 'Furniture > Cabinets & Storage > Vanities > Bathroom Vanities > Bathroom '
                    'Vanity Sets',
     'bathroom_sink': 'Hardware > Plumbing > Plumbing Fixtures > Sinks > Bathroom Sinks',
     'outdoor_dining_table': 'Furniture > Outdoor Furniture > Outdoor Tables > Dining Tables',
     'outdoor_dining_chair': 'Furniture > Outdoor Furniture > Outdoor Seating > Outdoor Chairs > '
                         'Outdoor Dining Chairs',
     'outdoor_bar_stool': 'Furniture > Outdoor Furniture > Outdoor Seating > Outdoor Chairs > Outdoor '
                      'Bar & Counter Chairs',
     'outdoor_bar_table': 'Furniture > Outdoor Furniture > Outdoor Tables > Bar Tables',
     'outdoor_coffee_table': 'Furniture > Outdoor Furniture > Outdoor Tables > Coffee Tables',
     'outdoor_side_table': 'Furniture > Outdoor Furniture > Outdoor Tables > Side Tables',
     'outdoor_fire_pit_table': 'Furniture > Outdoor Furniture > Outdoor Tables > Fire Pits > Fire Pit '
                           'Tables',
     'sofa_loveseat': 'Furniture > Sofas > Loveseat Sofas',
     'accent_chair': 'Furniture > Chairs > Armchairs, Recliners & Sleeper Chairs > Armchairs',
     'lounge_chair': 'Furniture > Chairs > Armchairs, Recliners & Sleeper Chairs > Armchairs',
     'swivel_chair': 'Furniture > Chairs > Armchairs, Recliners & Sleeper Chairs > Armchairs',
     'chaise': 'Furniture > Chairs > Chaises',
     'corner_chair': 'Furniture > Chairs > Armchairs, Recliners & Sleeper Chairs > Armchairs',
     'armless_chair': 'Furniture > Chairs > Armchairs, Recliners & Sleeper Chairs > Armchairs',
     'sofa_bumper': 'Furniture > Sofas',
     'living_room_set': 'Furniture > Furniture Sets > Living Room Furniture Sets',
     'loveseat': 'Furniture > Sofas > Loveseat Sofas',
     'counter_stool': 'Furniture > Chairs > Table & Bar Stools > Counter Stools',
     'mirror': 'Home & Garden > Decor > Mirrors',
     'nightstand': 'Furniture > Tables > Nightstands',
     'tv_stand': 'Furniture > Entertainment Centers & TV Stands',
     'display_cabinet': 'Furniture > Cabinets & Storage > China Cabinets & Hutches > Tall Display '
                    'Cabinets',
     'bookcase': 'Furniture > Shelving > Bookcases & Standing Shelves',
     'coat_rack': 'Furniture > Benches > Storage & Entryway Benches > Coat Racks',
     'entertainment_center': 'Furniture > Entertainment Centers & TV Stands',
     'accent_cabinet': 'Furniture > Cabinets & Storage > Storage Cabinets & Lockers > Storage Cabinets',
     'wall_shelves': 'Furniture > Shelving > Wall Shelves & Ledges',
     'coffee_table': 'Furniture > Tables > Accent Tables > Coffee Tables',
     'console_table': 'Furniture > Tables > Accent Tables > Console Tables',
     'end_table': 'Furniture > Tables > Accent Tables > End Tables',
     'nesting_table': 'Furniture > Tables > Accent Tables > Nesting Tables',
     'accent_table': 'Furniture > Tables > Accent Tables',
     'table_bar_stool': 'Furniture > Chairs > Table & Bar Stools',
     'swing_chair': 'Furniture > Outdoor Furniture > Outdoor Seating > Outdoor Chairs > Swing Chairs',
     'chandelier': 'Home & Garden > Lighting > Lighting Fixtures > Chandeliers',
     'pendant_light': 'Home & Garden > Lighting > Lighting Fixtures > Pendant Light Fixtures',
     'ceiling_light': 'Home & Garden > Lighting > Lighting Fixtures > Ceiling Light Fixtures',
     'wall_light': 'Home & Garden > Lighting > Lighting Fixtures > Wall Light Fixtures',
     'bench': 'Furniture > Benches',
     'sideboard': 'Furniture > Cabinets & Storage > Sideboards',
     'outdoor_furniture_cover': 'Furniture > Outdoor Furniture Accessories > Outdoor Furniture Covers',
     'bar_cabinet': 'Furniture > Cabinets & Storage > Wine & Liquor Cabinets',
     'computer_desk': 'Furniture > Office Furniture > Desks > Computer Desks',
     'writing_desk': 'Furniture > Office Furniture > Desks > Writing Desks',
     'file_cabinet': 'Furniture > Cabinets & Storage > File Cabinets',
     'dining_furniture_set': 'Furniture > Furniture Sets > Kitchen & Dining Furniture Sets',
     'kitchen_cart': 'Furniture > Carts & Islands > Carts > Kitchen Carts',
     'table_lamp': 'Home & Garden > Lighting > Lamps > Table Lamps',
     'floor_lamp': 'Home & Garden > Lighting > Lamps > Floor Lamps',
     'throw_pillow': 'Home & Garden > Decor > Throw Pillows'}

    # Source subcategory rules
    SOURCE_MAPPING = {'Sofas and Armchairs': {'sectional sofa': 'sectional',
                         'sectional': 'sectional',
                         'loveseat': 'loveseat',
                         'dining side chair': 'dining_chair',
                         'ottoman': 'ottoman',
                         'sofa': 'sofa',
                         'armchairs': 'armchair',
                         'chaise': 'chaise',
                         'accent chair': 'armchair',
                         'lounge chair': 'armchair',
                         'swivel chair': 'armchair',
                         'corner chair': 'armchair',
                         'armless chair': 'armchair',
                         'armchair': 'armchair',
                         'living room set': 'living_room_set'},
     'Bar and Counter Stools': {'counter bar stool': 'counter_stool',
                            'counter stools': 'counter_stool',
                            'counter stool': 'counter_stool',
                            'bar side stool': 'bar_stool',
                            'bar stools': 'bar_stool',
                            'bar stool': 'bar_stool'},
     'Dining Chairs': {'counter stool': 'counter_stool',
                   'counter stools': 'counter_stool',
                   'dining armchair': 'dining_chair',
                   'dining armchairs': 'dining_chair',
                   'dining side chair': 'dining_chair',
                   'dining side chairs': 'dining_chair',
                   'dining chair': 'dining_chair',
                   'dining chairs': 'dining_chair',
                   'side chair': 'dining_chair'},
     'Bar and Dining Tables': {'dining table': 'dining_table', 'bar table': 'outdoor_bar_table'},
     'Tables': {'coffee table': 'coffee_table',
            'console table': 'console_table',
            'end table': 'end_table',
            'nesting table': 'nesting_table',
            'side table': 'accent_table',
            'backless stool': 'table_bar_stool'},
     'Bar and Dining': {'dining set': 'outdoor_furniture_set',
                    'patio dining set': 'outdoor_furniture_set',
                    'outdoor patio dining set': 'outdoor_furniture_set',
                    'dining set of': 'outdoor_furniture_set',
                    'bar set': 'outdoor_furniture_set',
                    'pub set': 'outdoor_furniture_set',
                    'dining table': 'outdoor_dining_table',
                    'outdoor patio dining table': 'outdoor_dining_table',
                    'outdoor dining table': 'outdoor_dining_table',
                    'dining armchair': 'outdoor_dining_chair',
                    'dining chair': 'outdoor_dining_chair',
                    'side chair': 'outdoor_dining_chair',
                    'dining chairs': 'outdoor_dining_chair',
                    'dining armchairs': 'outdoor_dining_chair',
                    'outdoor patio dining armchair': 'outdoor_dining_chair',
                    'outdoor patio dining chair': 'outdoor_dining_chair',
                    'armless bar stool': 'outdoor_bar_stool',
                    'bar stool': 'outdoor_bar_stool',
                    'bar stools': 'outdoor_bar_stool',
                    'rectangle bar table': 'outdoor_bar_table',
                    'bar table': 'outdoor_bar_table',
                    'outdoor patio bar table': 'outdoor_bar_table',
                    'coffee table': 'outdoor_coffee_table',
                    'outdoor patio coffee table': 'outdoor_coffee_table',
                    'side table': 'outdoor_side_table',
                    'outdoor patio side table': 'outdoor_side_table',
                    'fire pit table': 'outdoor_fire_pit_table',
                    'outdoor patio fire pit table': 'outdoor_fire_pit_table',
                    'outdoor patio armchair': 'outdoor_dining_chair',
                    'outdoor patio wicker armchair': 'outdoor_dining_chair',
                    'dining outdoor patio armchair': 'outdoor_dining_chair',
                    'outdoor patio sunbrella armchair': 'outdoor_dining_chair'},
     'Office Chairs': {'gaming computer chair': 'gaming_chair',
                   'drafting chair': 'office_chair',
                   'office chair': 'office_chair',
                   'office storage cabinet': 'storage_cabinet',
                   'wall-mount shelf': 'wall_shelf',
                   'wall mount shelf': 'wall_shelf'},
     'Decor': {'tv stand': 'tv_stand',
           'media console': 'tv_stand',
           'entertainment center': 'entertainment_center',
           'display cabinet': 'display_cabinet',
           'display stand': 'display_cabinet',
           'bookcase': 'bookcase',
           'bookshelf': 'bookcase',
           'accent cabinet': 'accent_cabinet',
           'storage cabinet': 'accent_cabinet',
           'wall mounted shelves': 'wall_shelves',
           'coat rack': 'coat_rack',
           'trash bin': 'trash_can',
           'trash can': 'trash_can',
           'wastebasket': 'wastebasket',
           'pencil holder': 'pen_holder'},
     'Sofa Sectionals': {'sectional sofa set': 'outdoor_sectional',
                     'sectional sofa': 'outdoor_sectional',
                     'sectional': 'outdoor_sectional',
                     'corner outdoor patio armchair': 'outdoor_chair',
                     'outdoor patio armchair': 'outdoor_chair',
                     'armless outdoor patio chair': 'outdoor_chair',
                     'left-facing armchair': 'outdoor_chair',
                     'right-facing armchair': 'outdoor_chair',
                     'corner chair': 'outdoor_chair',
                     'left-arm chair': 'outdoor_chair',
                     'right-arm chair': 'outdoor_chair',
                     'armless chair': 'outdoor_chair',
                     'armchair': 'outdoor_chair',
                     'rocking lounge chair': 'outdoor_rocking_chair',
                     'rocking chair': 'outdoor_rocking_chair',
                     'folding chair': 'outdoor_folding_chair',
                     'swivel lounge chair': 'outdoor_chair',
                     'lounge chair': 'outdoor_chair',
                     'loveseat': 'outdoor_loveseat',
                     'sofa': 'outdoor_sofa',
                     'outdoor patio chaise': 'outdoor_chaise',
                     'chaise': 'outdoor_chaise',
                     'ottoman': 'outdoor_ottoman',
                     'pillow set': 'outdoor_pillow',
                     'single pillow': 'outdoor_pillow',
                     'pillow': 'outdoor_pillow',
                     'outdoor patio set': 'outdoor_furniture_set',
                     'furniture set': 'outdoor_furniture_set',
                     'set of 2': 'outdoor_furniture_set',
                     'set of 3': 'outdoor_furniture_set',
                     'set of 4': 'outdoor_furniture_set',
                     'set of 5': 'outdoor_furniture_set',
                     'set of 6': 'outdoor_furniture_set',
                     'set of 7': 'outdoor_furniture_set',
                     'set of 8': 'outdoor_furniture_set',
                     'set of 9': 'outdoor_furniture_set',
                     'set of 10': 'outdoor_furniture_set'},
     'Vanities': {'double basin bathroom sink': 'bathroom_sink',
              'single basin bathroom sink': 'bathroom_sink',
              'bathroom sink': 'bathroom_sink',
              'wall-mount bathroom vanity cabinet': 'bathroom_vanity',
              'wall-mount bathroom vanity': 'bathroom_vanity',
              'bathroom vanity cabinet': 'bathroom_vanity',
              'bathroom vanity': 'bathroom_vanity'},
     'Case Goods': {'tv stand': 'entertainment_center',
                'entertainment center': 'entertainment_center',
                'bookcase': 'bookcase',
                'bookshelf': 'bookcase',
                'coat rack': 'coat_rack',
                'mirror': 'mirror',
                'mirrors': 'mirror',
                'nightstand': 'nightstand',
                'nightstands': 'nightstand',
                'end table': 'end_table',
                'end tables': 'end_table'},
     'Daybeds and Lounges': {'daybed': 'outdoor_daybed',
                         'swing chair': 'swing_chair',
                         'patio swing chair': 'swing_chair',
                         'swing outdoor patio lounge chair': 'swing_chair',
                         'hanging chaise lounge outdoor patio swing chair': 'swing_chair'},
     'Ceiling Lamps': {'wall sconce': 'wall_light',
                   'sconce': 'wall_light',
                   'semi-flush': 'ceiling_light',
                   'ceiling fixture': 'ceiling_light',
                   'chandelier': 'chandelier',
                   'pendant light': 'pendant_light',
                   'pendant': 'pendant_light'},
     'Benches and Stools': {'bench': 'bench'},
     '': {'outdoor patio furniture cover': 'outdoor_furniture_cover',
      'furniture cover': 'outdoor_furniture_cover',
      'sideboard': 'sideboard',
      'bar cabinet': 'bar_cabinet',
      'tv stand': 'tv_stand'},
     'Computer Desks': {'desk and file cabinet set': 'computer_desk',
                    'file cabinet': 'file_cabinet',
                    'writing desk': 'writing_desk',
                    'computer office desk': 'computer_desk',
                    'office desk': 'computer_desk',
                    'wall-mount office desk': 'computer_desk',
                    'wall mount office desk': 'computer_desk',
                    'desk': 'computer_desk'},
     'Dining Sets': {'dining table and bench set': 'dining_furniture_set',
                 'dining set': 'dining_furniture_set',
                 'kitchen cart': 'kitchen_cart',
                 'dining stand': 'kitchen_cart',
                 'serving stand': 'kitchen_cart'},
     'Table Lamps': {'table lamp': 'table_lamp'},
     'Floor Lamps': {'floor lamp': 'floor_lamp'},
     'Pillow': {'throw pillow': 'throw_pillow'}}

    def __init__(self):

        # Cache taxonomy categories so we don't query the database
        # repeatedly for every product.

        self.taxonomy_cache = {}

        for taxonomy_key, taxonomy_path in self.TAXONOMY.items():

            category = (
                TaxonomyCategory.objects
                .filter(full_path=taxonomy_path)
                .first()
            )

            self.taxonomy_cache[taxonomy_key] = category

    # NORMALIZE TEXT

    def normalize_text(self, text):

        if not text:
            return ""

        text = str(text).lower()

        # Replace special characters with spaces.
        text = re.sub(r"[^a-z0-9]+", " ", text)

        # Remove duplicate spaces.
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # KEYWORD MATCHING

    def keyword_matches(self, keyword, text):

        keyword = self.normalize_text(keyword)
        text = self.normalize_text(text)

        if not keyword or not text:
            return False

        # Word-boundary matching.
        #
        # Example:
        # "sofa" matches "outdoor sofa"
        #
        # But:
        # "sofa" does not accidentally match a larger word.

        pattern = r"\b" + re.escape(keyword) + r"\b"

        return re.search(pattern, text) is not None

    # TAXONOMY LOOKUP

    def find_category(self, taxonomy_key):

        return self.taxonomy_cache.get(taxonomy_key)

    # BUILD PRODUCT TEXT

    def get_product_text(self, product):

        name = self.normalize_text(
            product.product_name or ""
        )

        description = self.normalize_text(
            product.product_description or ""
        )

        bullets = self.normalize_text(
            product.bullets or ""
        )

        materials = self.normalize_text(
            product.materials or ""
        )

        return {
            "name": name,
            "details": " ".join([
                description,
                bullets,
                materials,
            ]).strip(),
        }

    # RESULT BUILDER

    def build_result(
        self,
        taxonomy_key,
        confidence,
        reason,
    ):

        category = self.find_category(
            taxonomy_key
        )

        # Taxonomy category doesn't exist.
        if category is None:

            return None

        return {
            "category": category.full_path,
            "confidence": confidence,
            "reason": reason,
            "alternatives": [],
            "manual_review": False,
        }

    # SPECIAL RULES FOR SOFA SECTIONALS

    def classify_sofa_sectional(
        self,
        product_name,
        product_details,
    ):

        # 1. PILLOWS

        if self.keyword_matches(
            "pillow",
            product_name
        ):

            return self.build_result(
                "outdoor_pillow",
                0.98,
                "Product name identified as a pillow."
            )

        # 2. SECTIONAL SOFAS

        if self.keyword_matches(
            "sectional sofa",
            product_name
        ):

            return self.build_result(
                "outdoor_sectional",
                0.98,
                "Product name identified as a sectional sofa."
            )

        if self.keyword_matches(
            "sectional",
            product_name
        ):

            return self.build_result(
                "outdoor_sectional",
                0.97,
                "Product name identified as a sectional."
            )

        # 3. ROCKING CHAIRS

        if self.keyword_matches(
            "rocking lounge chair",
            product_name
        ):

            return self.build_result(
                "outdoor_rocking_chair",
                0.98,
                "Product name identified as a rocking lounge chair."
            )

        if self.keyword_matches(
            "rocking chair",
            product_name
        ):

            return self.build_result(
                "outdoor_rocking_chair",
                0.98,
                "Product name identified as a rocking chair."
            )

        # 4. FOLDING CHAIRS

        if self.keyword_matches(
            "folding chair",
            product_name
        ):

            return self.build_result(
                "outdoor_folding_chair",
                0.98,
                "Product name identified as a folding chair."
            )

        # 5. DAYBEDS

        if self.keyword_matches(
            "daybed",
            product_name
        ):

            return self.build_result(
                "outdoor_daybed",
                0.98,
                "Product name identified as a daybed."
            )

        # 6. CHAISES

        if self.keyword_matches(
            "chaise",
            product_name
        ):

            return self.build_result(
                "outdoor_chaise",
                0.98,
                "Product name identified as a chaise."
            )

        # 7. OTTOMANS

        if self.keyword_matches(
            "ottoman",
            product_name
        ):

            return self.build_result(
                "outdoor_ottoman",
                0.98,
                "Product name identified as an outdoor ottoman."
            )

        # 8. BENCHES

        if self.keyword_matches(
            "bench",
            product_name
        ):

            return self.build_result(
                "outdoor_bench",
                0.98,
                "Product name identified as an outdoor bench."
            )

        # 9. LOVESEATS

        if self.keyword_matches(
            "loveseat",
            product_name
        ):

            return self.build_result(
                "outdoor_loveseat",
                0.98,
                "Product name identified as an outdoor loveseat."
            )

        # 10. OUTDOOR FURNITURE SETS
        #
        # Important:
        #
        # "Marina 4 Piece Outdoor Patio Teak Set"
        #
        # does NOT contain the exact phrase:
        #
        # "outdoor patio set"
        #
        # because "teak" occurs between "patio" and "set".
        #
        # Therefore we explicitly detect piece/set patterns.

        piece_set_pattern = re.search(
            r"\b\d+\s*[-]?\s*piece\b.*\bset\b",
            product_name
        )

        set_of_pattern = re.search(
            r"\bset\s+of\s+\d+\b",
            product_name
        )

        if piece_set_pattern or set_of_pattern:

            return self.build_result(
                "outdoor_furniture_set",
                0.96,
                "Product name identified as an outdoor furniture set."
            )

        # 11. ARMCHAIRS / ARMLESS / CORNER / FACING CHAIRS

        chair_patterns = [

            "corner outdoor patio armchair",
            "outdoor patio armchair",
            "armless outdoor patio chair",
            "left-facing armchair",
            "right-facing armchair",
            "left-arm chair",
            "right-arm chair",
            "corner chair",
            "armless chair",
            "armchair",
            "swivel lounge chair",
            "lounge chair",
        ]

        for keyword in chair_patterns:

            if self.keyword_matches(
                keyword,
                product_name
            ):

                return self.build_result(
                    "outdoor_chair",
                    0.95,
                    f"Product name matched '{keyword}'."
                )

        # 12. OUTDOOR SOFA

        if self.keyword_matches(
            "sofa",
            product_name
        ):

            return self.build_result(
                "outdoor_sofa",
                0.95,
                "Product name identified as an outdoor sofa."
            )

        # 13. ARMLESS WITHOUT "CHAIR"
        #
        # Examples:
        #
        # Sojourn Outdoor Patio Fabric Sunbrella Armless
        # Summon Outdoor Patio Sunbrella Armless
        #
        # These appear to represent sectional components.

        if self.keyword_matches(
            "armless",
            product_name
        ):

            return self.build_result(
                "outdoor_chair",
                0.90,
                "Product name contains 'armless' and belongs to the "
                "Sofa Sectionals source category."
            )

        # 14. DETAILS FALLBACK

        if self.keyword_matches(
            "sectional sofa",
            product_details
        ):

            return self.build_result(
                "outdoor_sectional",
                0.90,
                "Product details identified a sectional sofa."
            )

        if self.keyword_matches(
            "sofa",
            product_details
        ):

            return self.build_result(
                "outdoor_sofa",
                0.90,
                "Product details identified an outdoor sofa."
            )

        return None

    # ALTERNATE

    def get_alternative_categories(
        self,
        source_subcategory,
        product_name,
        product_details,
        primary_category,
        limit=3,
    ):
        """Return other plausible taxonomy categories from matching source rules."""

        mappings = self.SOURCE_MAPPING.get(source_subcategory)

        if not mappings:
            return []

        alternatives = []
        seen = {primary_category}

        sorted_mappings = sorted(
            mappings.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        )

        for keyword, taxonomy_key in sorted_mappings:
            matched = (
                self.keyword_matches(keyword, product_name)
                or self.keyword_matches(keyword, product_details)
            )

            if not matched:
                continue

            category = self.find_category(taxonomy_key)

            if category is None:
                continue

            category_path = category.full_path

            if category_path in seen:
                continue

            alternatives.append(category_path)
            seen.add(category_path)

            if len(alternatives) >= limit:
                break

        return alternatives

    # FALLBACK SUGGESTION
    def get_fallback_alternatives(
        self,
        product_name,
        product_details,
        limit=3,
    ):
        """Suggest plausible taxonomy categories for manual-review products."""

        product_text = self.normalize_text(
            f"{product_name} {product_details}"
        )

        if not product_text:
            return []

        product_words = set(product_text.split())

        candidates = []

        for taxonomy_key, taxonomy_path in self.TAXONOMY.items():
            category_text = self.normalize_text(taxonomy_path)
            category_words = set(category_text.split())

            if not category_words:
                continue

            matching_words = (
                product_words.intersection(category_words)
            )

            if not matching_words:
                continue

            score = (
                len(matching_words)
                / len(category_words)
            )

            candidates.append(
                {
                    "taxonomy_key": taxonomy_key,
                    "category": taxonomy_path,
                    "score": score,
                }
            )

        candidates.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        alternatives = []
        seen = set()

        for candidate in candidates:
            category = self.find_category(
                candidate["taxonomy_key"]
            )

            if category is None:
                continue

            if category.full_path in seen:
                continue

            alternatives.append(category.full_path)

            seen.add(category.full_path)

            if len(alternatives) >= limit:
                break

        return alternatives
    
    # MAIN CLASSIFIER

    def classify(self, product):

        text = self.get_product_text(
            product
        )

        product_name = text["name"]
        product_details = text["details"]

        source_subcategory = (
            product.product_sub_category or ""
        ).strip()

        # Specialized sofa-sectional classification

        if source_subcategory == "Sofa Sectionals":

            result = self.classify_sofa_sectional(
                product_name,
                product_details,
            )

            if result is not None:
                return result

        # Source-specific mappings

        mappings = self.SOURCE_MAPPING.get(
            source_subcategory
        )

        if mappings:

            # Longest keyword first.
            sorted_mappings = sorted(
                mappings.items(),
                key=lambda item: len(item[0]),
                reverse=True
            )

            # Match product name first

            for keyword, taxonomy_key in sorted_mappings:

                if self.keyword_matches(
                    keyword,
                    product_name
                ):

                    result = self.build_result(
                        taxonomy_key,
                        0.95,
                        f"Product name matched '{keyword}'."
                    )

                    if result is not None:
                        result["alternatives"] = self.get_alternative_categories(
                            source_subcategory=source_subcategory,
                            product_name=product_name,
                            product_details=product_details,
                            primary_category=result["category"],
                        )
                        return result

            # Fall back to product details

            for keyword, taxonomy_key in sorted_mappings:

                if self.keyword_matches(
                    keyword,
                    product_details
                ):

                    result = self.build_result(
                        taxonomy_key,
                        0.90,
                        f"Product details matched '{keyword}'."
                    )

                    if result is not None:
                        return result

        # Manual review
        alternatives = self.get_fallback_alternatives(
            product_name=product_name,
            product_details=product_details,
        )
        return {
            "category": None,
            "confidence": 0.0,
            "reason": "No reliable taxonomy mapping was found.",
            "alternatives": alternatives,
            "manual_review": True,
        }
