from odoo import http
from odoo.http import request


class EstatePropertyController(http.Controller):
    @http.route("/estate_website_properties", auth="public", website=True)
    def properties(self, page=1, **kwargs):

        page = max(1, int(page))
        limit = 3
        offset = (page - 1) * limit
        records = (
            request.env["estate.property"]
            .sudo()
            .search(
                [
                    ("active", "=", True),
                    ("state", "in", ["new", "offer_received", "offer_received"]),
                ],
                limit=limit,
                offset=offset,
            )
        )

        total_records = (
            request.env["estate.property"]
            .sudo()
            .search_count(
                [
                    ("active", "=", True),
                    ("state", "in", ["new", "offer_received", "offer_received"]),
                ]
            )
        )
        total_pages = (total_records + limit - 1) // limit

        return request.render(
            "estate.estate_property_website_view_id",
            {
                "records": records,
                "current_page": page,
                "total_pages": total_pages,
            },
        )

    @http.route("/property/<int:property_id>", type="http", auth="public", website=True)
    def property_details(self, property_id, **kwargs):
        property = request.env["estate.property"].sudo().browse(property_id)
        return request.render(
            "estate.estate_property_detail_view_id", {"property": property}
        )
