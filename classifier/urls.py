from django.urls import path

from . import views


urlpatterns = [
    # Frontend
    path(
        "",
        views.dashboard,
        name="dashboard",
    ),

    path(
        "products/<int:product_id>/",
        views.product_review,
        name="product-review",
    ),

    # API
    path(
        "api/classifications/",
        views.classification_list,
        name="classification-list",
    ),

    path(
        "api/classifications/<int:product_id>/",
        views.classification_detail,
        name="classification-detail",
    ),

    path(
        "api/classifications/<int:product_id>/approve/",
        views.approve_classification,
        name="classification-approve",
    ),

    path(
        "api/classifications/<int:product_id>/update/",
        views.update_classification,
        name="classification-update",
    ),

    path(
    "api/classifications/<int:product_id>/revert/",
    views.revert_classification,
    name="classification-revert",
    ),
]