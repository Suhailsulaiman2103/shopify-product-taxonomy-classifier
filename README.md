# Shopify Product Taxonomy Classifier

A Django-based product classification system that maps product catalog data to Shopify's hierarchical product taxonomy.

The system imports product data from Excel, classifies products into Shopify taxonomy categories, extracts product and category-aware attributes, calculates confidence scores, suggests alternative categories, supports manual review, optionally analyzes product images, and exposes classification results through a review API.

## Features

- Imports product catalogs from Excel
- Imports Shopify hierarchical taxonomy data
- Classifies products into Shopify taxonomy categories
- Extracts structured product attributes
- Extracts category-aware attributes
- Detects brand information from product titles
- Generates confidence scores
- Suggests alternative categories
- Flags uncertain products for manual review
- Supports optional product image validation and lightweight analysis
- Handles missing or broken images without interrupting processing
- Processes products in configurable batches
- Supports resumable classification
- Isolates individual product failures
- Stores classification results in the database
- Exports classified products to CSV
- Provides REST-style endpoints for reviewing classifications
- Supports manual approval and category correction
- Includes automated tests

## Project Results

The supplied product catalog contains 4,999 products.

Current validation results:

```text
Total products:              4999
Automatically classified:    4999
Manual review:               0
Classification rate:         100.00%
Failed products:             0
Automated tests:             13 passing
```

The manual-review workflow was also tested separately using unknown product data to verify that uncertain products can be flagged and provided with alternative category suggestions.

## Technology Stack

- Python
- Django
- SQLite
- pandas
- openpyxl
- Requests
- Pillow
- Shopify Product Taxonomy

SQLite is used for the prototype. Because database access is handled through the Django ORM, the application can be migrated to MariaDB or another supported relational database for production deployment.

## Project Structure

```text
shopify_product_classifier/
│
├── classifier/
│   ├── attribute_extractor.py
│   ├── hierarchical_classifier.py
│   ├── image_service.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   │
│   └── management/
│       └── commands/
│           ├── classify_products.py
│           ├── export_classified_products.py
│           └── validate_classification.py
│
├── products/
│   ├── models.py
│   └── management/
│       └── commands/
│           └── import_products.py
│
├── taxonomy/
│   ├── models.py
│   └── management/
│       └── commands/
│           └── import_taxonomy.py
│
├── config/
│   ├── settings.py
│   └── urls.py
│
├── data/
│   └── categories.txt
│
├── manage.py
├── requirements.txt
└── README.md
```

## Classification Pipeline

```text
Product Catalog
      │
      ▼
Product Import
      │
      ▼
Text + Structured Product Data
      │
      ├── Product Name
      ├── Description
      ├── Source Category
      ├── Source Subcategory
      ├── Materials
      ├── Color
      ├── Brand
      └── Optional Image
      │
      ▼
Hierarchical Classifier
      │
      ├── Source-aware keyword rules
      ├── Shopify taxonomy lookup
      ├── Confidence scoring
      └── Alternative suggestions
      │
      ▼
Attribute Extraction
      │
      ├── Generic attributes
      ├── Category-aware attributes
      └── Optional image signal
      │
      ▼
Classification Result
      │
      ├── Predicted Category
      ├── Attributes
      ├── Confidence Score
      ├── Alternative Categories
      ├── Manual Review Flag
      └── Processing Status
      │
      ▼
Database / Review API / CSV Export
```

## Attribute Extraction

The system extracts structured attributes already available in the catalog, including:

- Color
- Materials
- Assembly requirement
- Set status
- Stackability
- Collection
- Product type
- Brand

It also derives category-aware attributes.

Examples:

```text
Empress Bonded Leather Sofa
Category: Furniture > Sofas

Category-specific attribute:
upholstery_material = Leather
```

```text
Track Round Dining Table
Category: Furniture > Tables > Dining Tables

Category-specific attribute:
table_shape = Round
```

The attribute extraction layer is extensible so additional category-specific rules can be added without modifying the primary classifier.

## Image Handling

Image processing is optional because remote image requests increase classification time.

When enabled, the system:

1. Finds the first available product image.
2. Validates the image URL.
3. Downloads the image safely with a timeout.
4. Verifies that the response contains an image.
5. Reads image dimensions.
6. Calculates a lightweight visual color signal.
7. Continues classification even if the image is missing or inaccessible.

Example:

```json
{
  "available": true,
  "status": "available",
  "width": 2000,
  "height": 2000,
  "visual_color": "Beige"
}
```

Structured catalog attributes take priority over image-derived values. Visual information is treated as a secondary signal.

For a production system, the image service can be extended with a multimodal or vision model for richer image-based classification.

## Confidence and Manual Review

Each classification includes a confidence score.

High-confidence rule matches are classified automatically.

If the classifier cannot determine a reliable category, the product is marked for manual review:

```json
{
  "category": null,
  "confidence": 0.0,
  "alternatives": [
    "Furniture > Sofas",
    "Furniture > Ottomans",
    "Furniture > Outdoor Furniture > Outdoor Seating > Outdoor Chairs"
  ],
  "manual_review": true
}
```

This prevents uncertain classifications from being silently accepted.

## Batch Processing and Failure Recovery

Products are processed in configurable batches.

Example:

```bash
python manage.py classify_products --batch-size 500
```

Already classified products are skipped during normal execution, allowing interrupted classification jobs to resume without starting from the beginning.

To deliberately reprocess existing products:

```bash
python manage.py classify_products --batch-size 500 --reprocess
```

To process only a limited number of products:

```bash
python manage.py classify_products --reprocess --limit 50
```

Image validation can be enabled when required:

```bash
python manage.py classify_products --check-images --reprocess --limit 10
```

If one product fails, it is marked with a failed status while the remaining products continue processing.

This provides a lightweight resumable processing design for the prototype.

For production workloads involving slow external AI APIs, the same classification service can be executed through background workers such as Celery with Redis.

## API

Start the Django development server:

```bash
python manage.py runserver
```

### List classifications

```text
GET /api/classifications/
```

Optional status filtering:

```text
GET /api/classifications/?status=classified
```

### View one classification

```text
GET /api/classifications/<product_id>/
```

### Approve a classification

```text
POST /api/classifications/<product_id>/approve/
```

### Update a classification

```text
POST /api/classifications/<product_id>/update/
```

Example JSON request:

```json
{
  "predicted_category": "Furniture > Sofas"
}
```

The prototype API allows classification results to be viewed, approved, and manually corrected.

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd shopify_product_classifier
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Import Shopify taxonomy

```bash
python manage.py import_taxonomy
```

### 6. Import products

Place the supplied Excel product file in the project root as:

```text
Product List.xlsx
```

Then run:

```bash
python manage.py import_products
```

### 7. Classify products

```bash
python manage.py classify_products
```

### 8. Validate classifications

```bash
python manage.py validate_classification
```

### 9. Export results

```bash
python manage.py export_classified_products
```

The generated file is:

```text
classified_products.csv
```

## Testing

Run:

```bash
python manage.py test
```

Current result:

```text
Found 13 test(s).
.............
OK
```

Tests cover core classification behavior, classification API operations, and image failure handling.

## Scalability

The prototype processes products in resumable batches and isolates failures at the individual-product level.

For a production-scale implementation involving 10,000+ products and external AI requests, the recommended architecture would be:

```text
Django API
    │
    ▼
Task Queue
    │
    ▼
Redis
    │
    ▼
Celery Workers
    │
    ├── Product batch 1
    ├── Product batch 2
    ├── Product batch 3
    └── ...
    │
    ▼
Classification Service
    │
    ▼
MariaDB
```

This allows multiple batches to be processed concurrently while preserving retry, progress, and failure information.

## Design Decisions

The classifier uses deterministic hierarchical rules as its primary classification mechanism.

This approach was selected for the prototype because it provides:

- Predictable results
- Explainable classifications
- Fast execution
- No dependency on paid AI APIs
- Easy debugging
- Easy addition of domain-specific rules

The classifier is separated from image processing and attribute extraction so these components can later be replaced or extended with machine-learning or multimodal models without redesigning the rest of the application.

## Future Improvements

Potential production improvements include:

- Celery and Redis background processing
- MariaDB deployment
- Multimodal image classification
- Semantic embedding-based taxonomy matching
- Authentication and authorization for review endpoints
- Pagination for classification results
- Bulk approval workflow
- Detailed audit history for manual corrections
- Monitoring and retry dashboards
- Automated taxonomy synchronization

## Dataset

The original product catalog used for this assessment is not included in this repository because it was provided for evaluation purposes.

To run the project with the supplied assessment dataset, place the Excel file in the project root as:

```text
Product List.xlsx

## Summary

This project demonstrates an end-to-end product taxonomy classification workflow including product ingestion, Shopify taxonomy mapping, structured and category-aware attribute extraction, confidence scoring, alternative suggestions, manual review, image handling, resumable batch processing, persistence, export, automated testing, and classification review APIs.