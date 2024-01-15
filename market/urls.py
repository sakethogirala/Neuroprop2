from django.urls import path, include
from .views import *

urlpatterns = [
    path("lender-map/", lender_map, name="lender-map"),
    path("lenders/", lenders, name="lenders"),
    path("lenders/search/", lenders_search, name="lenders_search"),
    path("create-lender/", create_lender, name="create_lender"),
    path("render-offcanvas", render_offcanvas, name="render_offcanvas"),
    path("create-outreach", create_outreach, name="create_outreach"),
    path("outreaches/", outreaches, name="outreaches"),
    path("add-note/", add_note, name="add_note"),
    path("delete-lender/<lender_pk>/", delete_lender, name="delete_lender"),
    path("edit-lender/<lender_pk>/", edit_lender, name="edit_lender"),
    path("outreach/<outreach_uid>/", outreach_detail, name="outreach_detail")
]
