from odoo import _, http
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.http import request


class LibraryController(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "book_rentals" in counters:
            Rentals = request.env["library.rental"]
            rentals_count = 0
            if Rentals.check_access_rights("read", raise_exception=False):
                rentals_count = Rentals.search_count(
                    [("customer_id", "=", request.env.user.partner_id.id)]
                )
            values["book_rentals"] = rentals_count
        return values

    @http.route("/my/books", type="http", auth="user", website=True)
    def portal_my_books(
        self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw
    ):
        values = self._prepare_portal_layout_values()

        partner = request.env.user.partner_id
        Rentals = request.env["library.rental"]

        domain = [
            ("customer_id", "=", partner.id),
        ]

        searchbar_sortings = {
            "date": {"label": _("Rental Date"), "order": "rental_date desc"},
            "stage": {"label": _("Stage"), "order": "state"},
        }

        # default sortby order
        if not sortby:
            sortby = "date"
        sort_order = searchbar_sortings[sortby]["order"]

        if date_begin and date_end:
            domain += [
                ("create_date", ">", date_begin),
                ("create_date", "<=", date_end),
            ]

        # count for pager
        rentals_count = Rentals.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/books",
            url_args={"date_begin": date_begin, "date_end": date_end, "sortby": sortby},
            total=rentals_count,
            page=page,
            step=self._items_per_page,
        )
        rentals = Rentals.search(
            domain, order=sort_order, limit=self._items_per_page, offset=pager["offset"]
        )
        request.session["my_rentals_history"] = rentals.ids[:100]

        values.update(
            {
                "date": date_begin,
                "rentals": rentals.sudo(),
                "page_name": "books",
                "pager": pager,
                "default_url": "/my/books",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return request.render("library.portal_my_books", values)
