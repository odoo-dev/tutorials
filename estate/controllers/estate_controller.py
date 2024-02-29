from odoo import http
from datetime import datetime


class EstateController(http.Controller):

    @http.route(
        ["/properties", "/properties/page/<int:page>"],
        type="http",
        auth="public",
        website=True,
    )
    def properties(self, page=1, listed_after=None, **kw):
        domain = [("state", "in", ['new','offer_recieved'])]
        if listed_after:
            listed_after = datetime.strptime(listed_after, "%Y-%m-%d").date()
            domain.append(("create_date", ">=", listed_after))

        # searching proiperties that satisfy both the domains
        total_properties = http.request.env["estate.property"].search_count(domain)
        items_per_page = 6
        order = "create_date desc"
        
        # Pager
        pager = http.request.website.pager(
            url="/properties",
            total=total_properties,
            page=page,
            step=items_per_page,
            url_args={"listed_after": listed_after},
        )

        # Load data as per pager
        properties = http.request.env["estate.property"].search(
            domain, order=order, limit=items_per_page, offset=pager["offset"]
        )

        return http.request.render(
            "estate.estate_properties_web_page",
            {"properties": properties, "pager": pager},
        )

    @http.route("/property/<int:property_id>", auth="public", website=True)
    def property_detail(self, property_id, **kw):
        property = http.request.env["estate.property"].browse(property_id)
        return http.request.render(
            "estate.property_detail_page", {"property": property}
        )
