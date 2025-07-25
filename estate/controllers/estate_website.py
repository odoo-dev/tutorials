from odoo import http
from math import ceil


class EstatePropertyWebsite(http.Controller):
    _properties_per_page = 3

    @http.route(
        ["/estate-properties", "/estate-properties/page/<int:page>"],
        type="http",
        auth="public",
        website=True,
    )
    def estate_properties_list(
        self, page=1, state="all", min_price=None, max_price=None, **kwargs
    ):
        properties = http.request.env["estate.property"]
        domain = ["|", ("state", "=", "new"), ("state", "=", "Offer Received")]
        current_domain = list(domain)

        if state in ["new", "Offer Received"]:
            current_domain = [("state", "=", state)]
        else:
            state = "all"

        if min_price:
            try:
                min_price = float(min_price)
                current_domain.append(("expected_price", ">=", min_price))
            except ValueError:
                min_price = None

        if max_price:
            try:
                max_price = float(max_price)
                current_domain.append(("expected_price", "<=", max_price))
            except ValueError:
                max_price = None

        total_properties = properties.search_count(current_domain)

        total_pages = ceil(total_properties / float(self._properties_per_page))

        offset = (page - 1) * self._properties_per_page

        properties = properties.search(
            current_domain, limit=self._properties_per_page, offset=offset
        )

        pager = http.request.website.pager(
            url="/estate-properties",
            total=total_pages,
            page=page,
            step=1,
            scope=6,
            url_args={
                "state": state,
                "min_price": min_price,
                "max_price": max_price,
            },
        )

        return http.request.render(
            "estate.estate_properties_listing_template",
            {
                "properties": properties,
                "pager": pager,
                "total_properties": total_properties,
                "page": page,
                "total_pages": total_pages,
                "state": state,
                "min_price": min_price,
                "max_price": max_price,
            },
        )

    @http.route(
        "/estate-properties/<int:property_id>", type="http", auth="public", website=True
    )
    def estate_property_detail(self, property_id, **kwargs):
        Property = http.request.env["estate.property"]
        property_obj = Property.browse(property_id)

        if not property_obj or property_obj.state not in ["new", "Offer Received"]:
            return http.request.redirect("/estate-properties")

        return http.request.render(
            "estate.estate_property_detail_template",
            {
                "property": property_obj,
            },
        )
