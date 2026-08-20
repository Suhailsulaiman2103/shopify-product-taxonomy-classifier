import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from products.models import Product
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

def dashboard(request):
    """Display classification results in a review dashboard."""

    products = Product.objects.all().order_by("id")

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        products = products.filter(
            product_name__icontains=search
        )

    if status:
        products = products.filter(
            classification_status=status
        )

    paginator = Paginator(products, 25)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search": search,
        "status": status,

        "total_products": Product.objects.count(),

        "classified_count": Product.objects.filter(
            classification_status="classified"
        ).count(),

        "approved_count": Product.objects.filter(
            classification_status="approved"
        ).count(),

        "manual_review_count": Product.objects.filter(
            manual_review=True
        ).count(),

        "failed_count": Product.objects.filter(
            classification_status="failed"
        ).count(),
    }

    return render(
        request,
        "classifier/dashboard.html",
        context,
    )


def product_review(request, product_id):
    """Display one product and its classification details."""

    product = get_object_or_404(
        Product,
        id=product_id,
    )

    return render(
        request,
        "classifier/product_detail.html",
        {
            "product": product,
        },
    )

@require_GET
def classification_list(request):
    """Return classification results with optional status filtering."""

    status = request.GET.get("status")

    products = Product.objects.all().order_by("id")

    if status:
        products = products.filter(classification_status=status)

    data = [
        {
            "id": product.id,
            "product_number": product.product_number,
            "product_name": product.product_name,
            "source_category": product.product_category,
            "source_subcategory": product.product_sub_category,
            "predicted_category": product.predicted_category,
            "predicted_attributes": product.predicted_attributes,
            "confidence_score": product.confidence_score,
            "alternative_categories": product.alternative_categories,
            "classification_status": product.classification_status,
            "manual_review": product.manual_review,
        }
        for product in products[:100]
    ]

    return JsonResponse(
        {
            "count": products.count(),
            "results": data,
        }
    )


@require_GET
def classification_detail(request, product_id):
    """Return classification information for one product."""

    product = get_object_or_404(
        Product,
        id=product_id,
    )

    return JsonResponse(
        {
            "id": product.id,
            "product_number": product.product_number,
            "product_name": product.product_name,
            "predicted_category": product.predicted_category,
            "predicted_attributes": product.predicted_attributes,
            "confidence_score": product.confidence_score,
            "alternative_categories": product.alternative_categories,
            "classification_status": product.classification_status,
            "manual_review": product.manual_review,
        }
    )


@csrf_exempt
@require_POST
def approve_classification(request, product_id):
    """Approve the current classification for a product."""

    product = get_object_or_404(
        Product,
        id=product_id,
    )

    product.classification_status = "approved"
    product.manual_review = False

    product.save(
        update_fields=[
            "classification_status",
            "manual_review",
            "updated_at",
        ]
    )

    return JsonResponse(
        {
            "message": "Classification approved.",
            "product_id": product.id,
            "classification_status": product.classification_status,
        }
    )

@csrf_exempt
@require_POST
def update_classification(request, product_id):
    """Update a product classification during manual review."""

    product = get_object_or_404(
        Product,
        id=product_id,
    )

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON body."},
            status=400,
        )

    category = payload.get("predicted_category")

    if not category:
        return JsonResponse(
            {"error": "predicted_category is required."},
            status=400,
        )

    product.predicted_category = category
    product.classification_status = "approved"
    product.manual_review = False

    product.save(
        update_fields=[
            "predicted_category",
            "classification_status",
            "manual_review",
            "updated_at",
        ]
    )

    return JsonResponse(
        {
            "message": "Classification updated.",
            "product_id": product.id,
            "predicted_category": product.predicted_category,
            "classification_status": product.classification_status,
        }
    )

@csrf_exempt
@require_POST
def revert_classification(request, product_id):
    """Revert an approved classification back to classified."""

    product = get_object_or_404(
        Product,
        id=product_id,
    )

    product.classification_status = "classified"
    product.manual_review = False

    product.save(
        update_fields=[
            "classification_status",
            "manual_review",
            "updated_at",
        ]
    )

    return JsonResponse(
        {
            "message": "Classification reverted.",
            "product_id": product.id,
            "classification_status": product.classification_status,
        }
    )