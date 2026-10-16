from django.urls import path

from .views import (
    AuditLogListView,
    ConsolidatedExcelExportView,
    DashboardView,
    InventoryExportView,
    InventoryReportView,
    RecommendationExportView,
    RecommendationReportView,
    ReturnsExportView,
    ReturnsReportView,
    SalesExportView,
    SalesReportView,
    StaffDetailView,
    StaffListCreateView,
)

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="operations-dashboard"),
    path(
        "reports/export/",
        ConsolidatedExcelExportView.as_view(),
        name="consolidated-report-export",
    ),
    path("reports/sales/", SalesReportView.as_view(), name="sales-report"),
    path("reports/sales/export/", SalesExportView.as_view(), name="sales-report-export"),
    path("reports/inventory/", InventoryReportView.as_view(), name="inventory-report"),
    path(
        "reports/inventory/export/", InventoryExportView.as_view(), name="inventory-report-export"
    ),
    path("reports/returns/", ReturnsReportView.as_view(), name="returns-report"),
    path("reports/returns/export/", ReturnsExportView.as_view(), name="returns-report-export"),
    path(
        "reports/recommendations/", RecommendationReportView.as_view(), name="recommendation-report"
    ),
    path(
        "reports/recommendations/export/",
        RecommendationExportView.as_view(),
        name="recommendation-report-export",
    ),
    path("staff/", StaffListCreateView.as_view(), name="staff-list-create"),
    path("staff/<int:staff_id>/", StaffDetailView.as_view(), name="staff-detail"),
    path("audit-logs/", AuditLogListView.as_view(), name="audit-log-list"),
]
