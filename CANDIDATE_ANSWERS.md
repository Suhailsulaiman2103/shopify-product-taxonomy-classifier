# Candidate Questions – Technical Answers

## 1. What approach would you use to automatically identify the Shopify category, attributes, and attribute values? Explain your approach and why you selected it.

For the prototype, I implemented a deterministic hierarchical classification pipeline.
The system uses available product information such as:
- Product title
- Description
- Existing category and subcategory
- Product type
- Brand
- Material
- Color
The data is normalized and passed to the classification layer. The classifier uses source-aware rules and keyword matching to determine an appropriate category and maps the result against the imported Shopify Product Taxonomy.
After category classification, a separate attribute extraction layer extracts generic attributes such as color, material, brand, assembly requirement, collection, and product type. It also derives category-specific attributes, such as upholstery material for sofas and table shape for tables.
The result contains the predicted category, extracted attributes, confidence score, alternative categories, and manual-review status.
I selected this approach for the prototype because it is fast, deterministic, explainable, easy to test, and does not depend on paid external AI services.
For a production implementation covering a wider and more diverse catalog, I would extend this pipeline with semantic embeddings and/or an LLM or multimodal model while validating the final result against the Shopify taxonomy.

---

## 2. How would you handle a product that has a title but no description and no image?
The classifier is designed to work with partial product information.
If only the product title is available, the system can still use words and patterns in the title to identify potential product types and taxonomy categories.
For example, a title containing terms such as:
```text
Round Dining Table
```
provides useful information even without a description or image.
The classifier uses all available fields rather than requiring every field to be present.
If the available information is insufficient to make a reliable classification, the system should reduce the confidence score, provide possible alternative categories, and flag the product for manual review rather than forcing an unreliable result.
---

## 3. How would you use product images to improve classification when an image is available?
In the prototype, image processing is implemented as an optional secondary signal.
The image service:
1. Finds an available product image.
2. Checks whether the image URL is accessible.
3. Downloads the image with a timeout.
4. Verifies that the response contains a valid image.
5. Extracts image dimensions.
6. Calculates a lightweight visual-color signal.
7. Continues processing even when the image is unavailable.
Structured catalog information is treated as the primary source because it is generally more reliable for the provided dataset.
For a production implementation, I would extend the image service using a multimodal vision model. The model could identify visual characteristics such as product type, shape, material, style, and color.
The image prediction would then be combined with the text/structured-data prediction instead of being treated as the only classification source.
---

## 4. How would you design the application to process 10,000+ products efficiently? Explain your approach for batch/background processing.
The prototype already processes products in configurable batches.
For example:
```bash
python manage.py classify_products --batch-size 500
```
This prevents the complete catalog from being treated as one large operation.
The implementation also:
- Skips already processed products
- Supports deliberate reprocessing
- Isolates individual product failures
- Allows limited processing for testing
- Preserves processing status in the database
For production, I would move classification execution to background workers using Celery and Redis.
A production flow could be:
```text
Django Application
        |
        v
Task Queue
        |
        v
Redis
        |
        v
Celery Workers
        |
        +---- Batch 1
        +---- Batch 2
        +---- Batch 3
        |
        v
Classification Service
        |
        v
MariaDB
```
Multiple workers could process separate batches concurrently while the Django application remains responsive.
Retry policies, rate limiting, task status, and failure information would also be maintained.
---

## 5. How would you store the Shopify taxonomy and its category hierarchy in the database?
I store the Shopify taxonomy in a dedicated taxonomy model rather than embedding category names directly into classifier logic.
Each taxonomy record can contain information such as:
- Taxonomy identifier
- Category name
- Full category path
- Parent category
The parent relationship allows the taxonomy to represent hierarchical structures.
For example:
```text
Furniture
    >
Tables
    >
Accent Tables
    >
End Tables
```
The taxonomy is imported into MariaDB using a Django management command.
This approach makes taxonomy lookup reusable and allows the classification layer to work with hierarchical categories rather than a flat list of strings.
It also makes future taxonomy updates easier because taxonomy data can be updated independently of the product classifier.
---

## 6. How would you calculate or determine the confidence score for a classification?
In the prototype, confidence is based on the strength and specificity of deterministic classification signals.
A strong category-specific rule receives a higher confidence than a weak or generic match.
Signals can include:
- Product title matches
- Source category/subcategory
- Product type
- Specific keywords
- Agreement between multiple available fields
- Specificity of the matched taxonomy rule
A strong match can therefore be automatically classified, while an uncertain match receives a lower confidence.
For a production ML/AI implementation, I would calibrate confidence using model probabilities or similarity scores together with agreement between text, structured attributes, and image predictions.
Confidence should represent how reliable the classification appears to be; it should not be presented as measured classification accuracy unless it has been validated against labeled ground-truth data.
---

## 7. What would you do when the system cannot confidently identify a single category?
The system should not force a category when the available evidence is insufficient.
The prototype supports a manual-review fallback.
An uncertain result can contain:
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
This allows the system to:
- Avoid silently accepting unreliable classifications
- Provide useful candidate categories
- Route the product to a human reviewer
- Allow the reviewer to manually correct the category
The corrected result can then be stored in the database.
---

## 8. How would you handle a broken or inaccessible product image without stopping the complete batch?
Image processing is isolated from the main classification workflow.
The image service uses request timeouts and validates the response before processing it.
If an image is missing, inaccessible, invalid, or cannot be decoded, the service returns an image status describing the failure instead of terminating the classification process.
The classifier then continues using the available text and structured product information.
Failures are handled at the individual-product level, so a problem with one image does not stop the remaining products in the batch.
This behavior is also covered by automated tests.
---

## 9. How would you design the API and database structure for this application?
I separated the application into three primary Django components:
```text
products
taxonomy
classifier
```

### Products
Stores the imported source product information and classification results.
Classification-related data includes:
- Predicted category
- Extracted attributes
- Confidence score
- Alternative categories
- Classification status
- Manual-review flag

### Taxonomy
Stores the Shopify taxonomy and its hierarchy.

### Classifier
Contains the classification logic, attribute extraction, image processing, batch commands, API endpoints, and review interface.
The prototype provides endpoints such as:
```text
GET  /api/classifications/
GET  /api/classifications/<product_id>/
POST /api/classifications/<product_id>/approve/
POST /api/classifications/<product_id>/revert/
POST /api/classifications/<product_id>/update/
```
The frontend uses the same classification data to provide a review dashboard.
MariaDB is used for relational persistence, while Django ORM provides the database abstraction layer.
For production, I would additionally introduce authentication, authorization, API versioning, audit history, and stricter request validation.
---

## 10. If the application needs to process 10,000 products and each external AI/API request takes approximately 2 seconds, how would you optimize the processing time?
Processing sequentially would require approximately:
```text
10,000 × 2 seconds
= 20,000 seconds
≈ 5.56 hours
```
Therefore, I would avoid processing external requests sequentially.
I would use background workers with controlled concurrency.
For example:
```text
10,000 products
      |
      v
Batch creation
      |
      v
Redis queue
      |
      +---- Celery Worker 1
      +---- Celery Worker 2
      +---- Celery Worker 3
      +---- ...
```
The main optimizations would include:
- Multiple concurrent workers
- Configurable batch sizes
- Connection reuse where supported
- API batching if the provider supports batch requests
- Caching repeated results
- Avoiding external requests when deterministic classification is already sufficiently confident
- Request timeouts
- Retry with exponential backoff
- API rate-limit enforcement
- Saving results incrementally
The theoretical processing time decreases with concurrency, but production concurrency must respect the external provider's rate limits and infrastructure capacity.
For example, 10 workers do not automatically guarantee exactly one-tenth of the processing time because network latency, API throttling, retries, and database operations also contribute to the total duration.
---

## 11. How would you design the system so that if processing fails after 6,000 products, it can resume from the remaining products instead of starting again?
Processing status is stored for each product.
During a normal classification run, products that have already been successfully classified are skipped.
Therefore, if processing stops after 6,000 products, a subsequent run can query only products that still require classification.
Conceptually:
```text
10,000 products
      |
      +---- 6,000 completed
      |
      +---- 4,000 pending
                |
                v
             Resume
```
The prototype already supports this behavior.
It also provides a `--reprocess` option when previously processed products intentionally need to be classified again.
For production background processing, the same principle would be extended using persistent task states, retry counters, task identifiers, and worker acknowledgements.
---

## 12. What technologies/frameworks would you choose for this application, and why?
For the prototype I selected:

### Python
Python provides strong support for data processing, web development, machine learning, and AI integrations.

### Django
Django provides:
- ORM
- Routing
- Database migrations
- Admin capabilities
- Security middleware
- Template rendering
- Testing tools
It allowed the classification prototype, API, database layer, and review interface to be implemented within one structured application.

### MariaDB
MariaDB is used as the relational database and aligns with the preferred technology stack in the assignment.
It provides stronger production-oriented relational database capabilities than using a local SQLite database.

### pandas and openpyxl
These libraries are used for importing and processing Excel product data.

### Requests
Used for controlled HTTP access to product images.

### Pillow
Used for lightweight image validation and analysis.

### HTML/CSS/JavaScript
Used to implement the review dashboard without introducing an unnecessary separate frontend framework for the prototype.

### Git and GitHub
Used for version control and source-code delivery.
For a larger production system, I would consider adding:
- Celery
- Redis
- Docker
- Production application server/reverse proxy
- Monitoring/logging platform
- LLM/embedding service
- Multimodal vision model
These would be introduced when the production workload justifies the additional infrastructure.
---

## 13. Provide a high-level architecture/design for the complete application.
The implemented prototype follows this architecture:

```text
                  Product Excel File
                         |
                         v
                 Product Import Layer
                         |
                         v
                      MariaDB
                         |
                         v
                Classification Service
                /        |         \
               /         |          \
              v          v           v
        Text/Rules   Taxonomy    Image Service
              \          |           /
               \         |          /
                \        |         /
                         v
                Classification Result
                         |
             +-----------+-----------+
             |                       |
             v                       v
      Review Dashboard        REST-style API
             |
             v
     Approve / Correct /
     Revert Classification
```

For a production system with slow external AI services, I would extend it to:

```text
Web / API
    |
    v
Django
    |
    +----------------------+
    |                      |
    v                      v
MariaDB                Redis Queue
                           |
                           v
                     Celery Workers
                           |
                  +--------+--------+
                  |                 |
                  v                 v
             Text/LLM API      Vision API
                  |                 |
                  +--------+--------+
                           |
                           v
                        MariaDB
```
This separates interactive web requests from expensive background classification tasks.
---

## 14. Provide a realistic development effort estimation in hours, including a task-wise breakdown for developing this as a production-ready application. Mention your assumptions and major dependencies/risks.
A production-ready implementation would require significantly more work than the prototype.
A realistic initial estimate for one developer would be:
| Task | Estimated Hours |
|---|---:|
| Requirement analysis and taxonomy study | 8–12 |
| Database and data-model design | 8–12 |
| Product import and data validation | 10–14 |
| Shopify taxonomy ingestion/synchronization | 10–16 |
| Classification engine | 30–45 |
| Attribute extraction | 20–30 |
| Confidence and alternative-category logic | 12–18 |
| Image/vision integration | 20–30 |
| Batch processing / Celery / Redis | 18–26 |
| API development | 16–24 |
| Review dashboard | 20–30 |
| Authentication and authorization | 10–16 |
| Failure handling and retry mechanisms | 12–18 |
| Logging, monitoring and audit history | 14–20 |
| Automated testing | 24–36 |
| Performance testing and optimization | 16–24 |
| Docker/deployment configuration | 14–20 |
| Documentation and handover | 8–12 |
| **Estimated total** | **290–403 hours** |
For one developer working approximately 40 hours per week, this represents roughly **7–10 weeks**, depending on integrations, quality requirements, and deployment environment.

### Assumptions
- Shopify taxonomy data is available in a consistent format.
- The product input schema is reasonably stable.
- Required external AI/vision services and credentials are available.
- The external APIs support the required request volume.
- MariaDB and deployment infrastructure are available.
- Product classification requirements and review rules are clearly defined.

### Major Risks and Dependencies
**Taxonomy ambiguity:** Some products may reasonably fit multiple Shopify categories.
**Incomplete product data:** Missing descriptions, product types, brands, or images can reduce classification confidence.
**Image quality:** Images may be unavailable, broken, low quality, or unrelated to the product.
**External API latency and rate limits:** AI and vision services may become the main processing bottleneck.
**Classification accuracy:** Production accuracy must be measured against a labeled validation dataset rather than inferred from classification coverage.
**Taxonomy changes:** Shopify taxonomy updates may require synchronization and potentially reclassification.
**Scale and concurrency:** Worker count must be balanced against database capacity and external API rate limits.
**Security:** Production review APIs require authentication, authorization, secure secret management, and audit logging.
The estimate should be refined after confirming the production accuracy target, deployment environment, expected request volume, AI provider, taxonomy update strategy, and review workflow.