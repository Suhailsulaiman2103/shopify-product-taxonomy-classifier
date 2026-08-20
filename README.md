# Shopify Product Taxonomy Classifier

A Django-based product classification system that maps product catalog data to Shopify's hierarchical product taxonomy.

The application imports product data from Excel, classifies products into Shopify taxonomy categories, extracts structured and category-aware attributes, calculates confidence scores, suggests alternative categories, supports manual review and correction, optionally analyzes product images, and provides a web-based review dashboard and REST-style classification API.

---

## Features

- Imports product catalogs from Excel
- Imports Shopify hierarchical taxonomy data
- Classifies products into Shopify taxonomy categories
- Extracts structured product attributes
- Extracts category-specific attributes
- Detects brand information from product titles
- Generates confidence scores
- Suggests alternative categories
- Flags uncertain products for manual review
- Supports optional product image validation and lightweight analysis
- Handles missing or broken images without interrupting processing
- Processes products in configurable batches
- Supports resumable classification
- Supports deliberate reprocessing
- Isolates individual product failures
- Stores classification results in MariaDB
- Exports classified products to CSV
- Provides a web-based classification review dashboard
- Provides REST-style endpoints for classification review
- Supports classification approval
- Supports reverting approved classifications
- Supports manual category correction
- Includes automated tests

---

## Project Results

The application was validated locally using the supplied assessment catalog containing **4,999 products**.

```text
Total products:               4999
Automatically classified:     4999
Manual review:                   0
Classification rate:         100.00%
Failed products:                 0
Automated tests:                13 passing
```

The **100% classification rate represents classification coverage, not independently measured classification accuracy**.

The manual-review workflow was also tested separately using unknown product data to verify that uncertain products can be flagged and provided with alternative category suggestions.

---

## Technology Stack

- Python
- Django
- MariaDB
- Django ORM
- pandas
- openpyxl
- Requests
- Pillow
- HTML
- CSS
- JavaScript
- Shopify Product Taxonomy
- Git & GitHub

MariaDB is used as the relational database for the final prototype. Django ORM provides the database abstraction layer used throughout the application.

---

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
│   ├── management/
│   │   └── commands/
│   │       ├── classify_products.py
│   │       ├── export_classified_products.py
│   │       └── validate_classification.py
│   │
│   ├── templates/
│   │   └── classifier/
│   │       ├── dashboard.html
│   │       └── product_detail.html
│   │
│   └── static/
│       └── classifier/
│           └── styles.css
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
├── .gitignore
└── README.md
```

---

## Classification Pipeline

```text
Product Catalog
      │
      ▼
Product Import
      │
      ▼
Structured Product Data
      │
      ├── Product Name
      ├── Description
      ├── Source Category
      ├── Source Subcategory
      ├── Materials
      ├── Color
      ├── Brand
      └── Optional Images
      │
      ▼
Hierarchical Classifier
      │
      ├── Source-aware rules
      ├── Keyword matching
      ├── Shopify taxonomy lookup
      ├── Confidence scoring
      └── Alternative suggestions
      │
      ▼
Attribute Extraction
      │
      ├── Generic attributes
      ├── Category-specific attributes
      └── Optional image signals
      │
      ▼
Classification Result
      │
      ├── Predicted Category
      ├── Extracted Attributes
      ├── Confidence Score
      ├── Alternative Categories
      ├── Manual Review Flag
      └── Processing Status
      │
      ▼
MariaDB
      │
      ├── Review Dashboard
      ├── Classification API
      └── CSV Export
```

---

## Shopify Product Taxonomy

The application maps products to Shopify's hierarchical product taxonomy.

The taxonomy is stored as parent-child categories so classifications can represent paths such as:

```text
Furniture
    >
Tables
    >
Accent Tables
    >
End Tables
```

The taxonomy import command reads the taxonomy source and stores category identifiers, names, full paths, and parent relationships in MariaDB.

This allows the classifier to work with hierarchical category paths rather than a flat list of labels.

---

## Attribute Extraction

The system extracts structured attributes already available in the product catalog, including:

- Color
- Materials
- Assembly requirement
- Set status
- Stackability
- Collection
- Product type
- Brand

Boolean-like source values are normalized into human-readable values such as:

```text
Y     → Yes
N     → No
true  → Yes
false → No
```

The system also derives category-specific attributes.

### Example: Sofa

```text
Product:
Empress Bonded Leather Sofa

Predicted Category:
Furniture > Sofas

Category-Specific Attribute:
upholstery_material = Leather
```

### Example: Table

```text
Product:
Track Round Dining Table

Category-Specific Attribute:
table_shape = Round
```

The attribute extraction component is separated from the main classifier so additional category-specific extraction rules can be introduced without redesigning the classification pipeline.

---

## Image Handling

Image processing is optional because remote image requests can significantly increase classification time.

When image checking is enabled, the system:

1. Finds an available product image.
2. Validates the image URL.
3. Downloads the image using a request timeout.
4. Verifies that the response contains an image.
5. Reads image dimensions.
6. Calculates a lightweight visual color signal.
7. Continues processing if an image is unavailable or broken.

Example image analysis result:

```json
{
  "available": true,
  "status": "available",
  "width": 2000,
  "height": 2000,
  "visual_color": "Beige"
}
```

Structured catalog attributes take priority over image-derived information. Image analysis is treated as a secondary signal.

For a production implementation, this component could be extended with a multimodal or computer-vision model.

---

## Confidence and Manual Review

Every classification includes a confidence score.

High-confidence rule matches can be classified automatically.

If the classifier cannot determine a reliable taxonomy mapping, the product can be flagged for manual review.

Example:

```json
{
  "category": null,
  "confidence": 0.0,
  "reason": "No reliable taxonomy mapping was found.",
  "alternatives": [
    "Furniture > Sofas",
    "Furniture > Ottomans",
    "Furniture > Outdoor Furniture > Outdoor Seating > Outdoor Chairs"
  ],
  "manual_review": true
}
```

This prevents uncertain classifications from being silently treated as reliable results.

---

## Batch Processing and Failure Recovery

Products can be processed in configurable batches.

Example:

```bash
python manage.py classify_products --batch-size 500
```

Products that have already been processed are skipped during normal execution, allowing an interrupted classification run to resume without starting from the beginning.

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

If an individual product fails during processing, the failure is isolated so the remaining products can continue.

This provides lightweight resumable batch processing for the prototype.

---

## Review Dashboard

The project includes a Django-based web interface for reviewing classification results.

The dashboard provides:

- Total product count
- Classified product count
- Approved product count
- Manual-review count
- Failed-product count
- Product search
- Status filtering
- Pagination
- Product images
- Source categories
- Predicted Shopify categories
- Confidence scores
- Classification status
- Individual product review pages

### Product Review

The product review page displays:

- Product image
- Product number
- Source category
- Source subcategory
- Materials
- Color
- Predicted Shopify category
- Confidence score
- Extracted attributes
- Category-specific attributes
- Image-analysis information
- Alternative category suggestions

The reviewer can also:

- Approve a classification
- Revert an approval back to classified
- Manually correct a predicted taxonomy category

---

## Classification API

Start the development server:

```bash
python manage.py runserver
```

### List Classifications

```http
GET /api/classifications/
```

Optional status filtering:

```http
GET /api/classifications/?status=classified
```

### View a Classification

```http
GET /api/classifications/<product_id>/
```

### Approve a Classification

```http
POST /api/classifications/<product_id>/approve/
```

### Revert an Approval

```http
POST /api/classifications/<product_id>/revert/
```

### Update a Classification

```http
POST /api/classifications/<product_id>/update/
```

Example request:

```json
{
  "predicted_category": "Furniture > Sofas"
}
```

The API supports viewing, approving, reverting, and manually correcting classification results.

---

# Setup

## 1. Clone the Repository

```bash
git clone <repository-url>
cd shopify-product-taxonomy-classifier
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux

```bash
python -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure MariaDB

Create a MariaDB database:

```sql
CREATE DATABASE shopify_classifier
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Create a dedicated application user:

```sql
CREATE USER 'shopify_app'@'localhost'
IDENTIFIED BY 'your-password';
```

Grant access:

```sql
GRANT ALL PRIVILEGES
ON shopify_classifier.*
TO 'shopify_app'@'localhost';

FLUSH PRIVILEGES;
```

---

## 5. Configure Environment Variables

Create a `.env` file in the project root.

```text
DB_NAME=shopify_classifier
DB_USER=shopify_app
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306

DJANGO_SECRET_KEY=your-django-secret-key
DEBUG=True
```

The `.env` file is excluded from Git and should never be committed.

A Django secret key can be generated with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 6. Run Database Migrations

```bash
python manage.py migrate
```

---

## 7. Import Shopify Taxonomy

```bash
python manage.py import_taxonomy
```

---

## 8. Import Products

The original assessment product catalog is intentionally not included in this repository.

Place the supplied Excel product file in the project root as:

```text
Product List.xlsx
```

Then run:

```bash
python manage.py import_products
```

---

## 9. Classify Products

```bash
python manage.py classify_products
```

For configurable batch processing:

```bash
python manage.py classify_products --batch-size 500
```

---

## 10. Validate Classification

```bash
python manage.py validate_classification
```

---

## 11. Run the Web Application

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

## 12. Export Results

```bash
python manage.py export_classified_products
```

The generated output is:

```text
classified_products.csv
```

The generated classification export is excluded from Git.

---

## Testing

Run the complete automated test suite:

```bash
python manage.py test
```

Current validated result:

```text
Found 13 test(s).
.............
----------------------------------------------------------------------
Ran 13 tests

OK
```

The tests cover core classification behavior, classification API operations, attribute extraction, and image failure handling.

---

## Dataset

The original product catalog used for this assessment is **not included in this repository** because it was supplied specifically for evaluation purposes.

The application was validated locally using the supplied catalog containing:

```text
4,999 products
```

To evaluate the project using the original assessment data, place the supplied Excel file in the project root as:

```text
Product List.xlsx
```

Then run:

```bash
python manage.py import_products
python manage.py classify_products
python manage.py validate_classification
```

Generated classification exports and local databases are also excluded from version control.

---

## Security

Sensitive configuration is loaded through environment variables rather than being hardcoded in the source code.

The following files are excluded from Git:

```text
.env
Product List.xlsx
classified_products.csv
db.sqlite3
db.sqlite3.backup
venv/
```

Database credentials and the Django secret key should never be committed to the repository.

---

## Design Decisions

The prototype uses deterministic hierarchical rules as its primary classification mechanism.

This approach was selected because it provides:

- Predictable behavior
- Explainable classifications
- Fast local execution
- No dependency on paid AI APIs
- Straightforward debugging
- Easy addition of domain-specific rules

The classifier, attribute extractor, image service, persistence layer, API, and user interface are separated so individual components can be extended without redesigning the complete application.

Django ORM is used for persistence, with MariaDB providing the relational database for the final implementation.

---

## Scalability

The prototype processes products in resumable batches and isolates failures at the individual-product level.

For larger production workloads involving external AI services, a possible architecture would be:

```text
Django Application
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
       ├── Product Batch 1
       ├── Product Batch 2
       ├── Product Batch 3
       └── ...
       │
       ▼
Classification Service
       │
       ▼
MariaDB
```

This would allow classification workloads to be processed asynchronously while supporting retries, progress tracking, and multiple workers.

---

## Future Improvements

Potential production improvements include:

- Celery and Redis background processing
- Multimodal image classification
- Semantic embedding-based taxonomy matching
- Authentication and authorization for review endpoints
- Bulk approval workflows
- Detailed audit history for manual corrections
- Monitoring and retry dashboards
- Automated Shopify taxonomy synchronization
- More comprehensive automated test coverage
- Production deployment configuration

---

## Taxonomy Source

The classification system uses Shopify Product Taxonomy data as the taxonomy source.

The taxonomy is imported into the application and represented hierarchically using parent-child relationships.

---

## Summary

This project demonstrates an end-to-end product taxonomy classification workflow including:

- Product ingestion
- Shopify taxonomy mapping
- Hierarchical classification
- Structured attribute extraction
- Category-aware attribute extraction
- Confidence scoring
- Alternative category suggestions
- Manual-review fallback
- Optional image analysis
- Resumable batch processing
- Failure isolation
- MariaDB persistence
- REST-style classification APIs
- Web-based review dashboard
- Approval and correction workflows
- CSV export
- Automated testing

The result is a functional prototype designed to demonstrate both the classification workflow and how it could evolve into a larger production system.