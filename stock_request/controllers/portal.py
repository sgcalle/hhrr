# -*- coding: utf-8 -*-

import pytz
from collections import OrderedDict
from dateutil import parser

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.osv.expression import OR

class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        values["stock_request_count"] = request.env["stock.request"].search_count(
            ["|",("message_partner_ids","in",[request.env.user.partner_id.id]),"|",("user_id","=",request.env.uid),("approver_ids","in",[request.env.uid])])
        values["user"] = request.env.user
        return values

    def _stock_request_get_page_view_values(self, stock_request, access_token, **kwargs):
        products = request.env["product.product"].sudo().search([("stock_request_ok","=",True)])
        values = {
            "stock_request": stock_request,
            "user": request.env.user,
            "products": products,
        }
        if stock_request:
            values["products"] |= stock_request.line_ids.mapped("product_id")
        return self._get_page_view_values(stock_request, access_token, values, "my_stock_requests_history", True, **kwargs)

    @http.route(["/my/stock_request/", "/my/stock_request/page/<int:page>"], type="http", auth="user", website=True)
    def portal_my_stock_requests(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in="name", **kw):
        values = self._prepare_portal_layout_values()
        stock_request_obj = request.env["stock.request"]
        domain = []

        if not any(request.env.user.employee_ids.mapped("stock_request_portal_access")):
            raise AccessError("You are not allowed to use the stock request portal!")

        archive_groups = self._get_archive_groups("stock.request", domain)
        if date_begin and date_end:
            domain += [("create_date",">",date_begin),("create_date","<=",date_end)]
    
        searchbar_sortings = {
            "date": {"label": _("Newest"), "order": "create_date desc"},
            "name": {"label": _("Name"), "order": "name"},
        }
        if not sortby:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]

        default_domain = ["|",("message_partner_ids","in",[request.env.user.partner_id.id]),"|",("user_id","=",request.env.uid),("approver_ids","in",[request.env.uid])]
        searchbar_filters = {
            "all": {"label": _("All"), "domain": default_domain},
            "pending": {"label": _("Pending"), "domain": [("state","=","pending")] + default_domain},
            "rejected": {"label": _("Rejected"), "domain": [("state","=","rejected")] + default_domain},
            "canceled": {"label": _("Canceled"), "domain": [("state","=","canceled")] + default_domain},
            "received": {"label": _("Received"), "domain": [("state","=","received")] + default_domain},
            "to_approve": {"label": _("To Approve"), "domain": [("state","=","pending"),("approver_ids","in",[request.env.uid])]},
        }
        if not filterby:
            filterby = "all"
        domain += searchbar_filters[filterby]['domain']

        searchbar_inputs = {
            "name": {"input": "name", "label": _("Search in Name")},
        }
        if search and search_in:
            search_domain = []
            if search_in == "name":
                search_domain = OR([search_domain, [("name","ilike",search)]])
            domain += search_domain

        stock_request_count = stock_request_obj.search_count(domain)
        pager = portal_pager(
            url="/my/stock_request",
            url_args={"date_begin": date_begin, "date_end": date_end, "sortby": sortby},
            total=stock_request_count,
            page=page,
            step=self._items_per_page
        )

        stock_requests = stock_request_obj.search(domain, order=order, limit=self._items_per_page, offset=pager["offset"])
        request.session["my_stock_requests_history"] = stock_requests.ids[:100]

        values.update({
            "date": date_begin,
            "date_end": date_end,
            "stock_requests": stock_requests,
            "page_name": "stock_request",
            "archive_groups": archive_groups,
            "default_url": "/my/stock_request",
            "pager": pager,
            "searchbar_sortings": searchbar_sortings,
            "sortby": sortby,
            "searchbar_filters": OrderedDict(sorted(searchbar_filters.items())),
            "filterby": filterby,
            "searchbar_inputs": searchbar_inputs,
            "search_in": search_in,
            "search": search,
        })
        return request.render("stock_request.portal_my_stock_requests", values)

    @http.route(["/my/stock_request/<int:request_id>"], type="http", auth="user", website="True")
    def portal_my_stock_request(self, request_id=None, access_token=None, **kw):
        stock_request = request.env["stock.request"].browse(request_id)
        values = self._stock_request_get_page_view_values(stock_request, access_token, **kw)
        values["readonly"] = True
        return request.render("stock_request.portal_my_stock_request", values)
    
    @http.route(["/my/stock_request/<int:request_id>/edit"], type="http", auth="user", website="True")
    def portal_my_stock_request_edit(self, request_id=None, access_token=None, **kw):
        stock_request = request.env["stock.request"].browse(request_id)
        values = self._stock_request_get_page_view_values(stock_request, access_token, **kw)
        return request.render("stock_request.portal_my_stock_request", values)
    
    @http.route(["/my/stock_request/create"], type="http", auth="user", website="True")
    def portal_my_stock_request_create(self, request_id=None, access_token=None, **kw):
        stock_request = request.env["stock.request"].browse(request_id)
        values = self._stock_request_get_page_view_values(stock_request, access_token, **kw)
        values["create_stock_request"] = True
        return request.render("stock_request.portal_my_stock_request", values)
    
    @http.route(["/my/stock_request/<int:request_id>/pend"], type="http", auth="user", website="True")
    def portal_my_stock_request_pend(self, request_id=None, access_token=None, **kw):
        stock_request = request.env["stock.request"].browse(request_id)
        stock_request.action_pend()
        values = self._stock_request_get_page_view_values(stock_request, access_token, **kw)
        return request.redirect("/my/stock_request/" + str(stock_request.sudo().id))

    @http.route(["/my/stock_request/<int:request_id>/reject"], type="http", auth="user", website="True")
    def portal_my_stock_request_reject(self, request_id=None, access_token=None, **kw):
        stock_request = request.env["stock.request"].browse(request_id)
        stock_request.action_reject()
        values = self._stock_request_get_page_view_values(stock_request, access_token, **kw)
        return request.redirect("/my/stock_request/" + str(stock_request.sudo().id))

    @http.route(["/my/stock_request/<int:request_id>/cancel"], type="http", auth="user", website="True")
    def portal_my_stock_request_cancel(self, request_id=None, access_token=None, **kw):
        stock_request = request.env["stock.request"].browse(request_id)
        stock_request.sudo().action_cancel()
        values = self._stock_request_get_page_view_values(stock_request, access_token, **kw)
        return request.redirect("/my/stock_request/" + str(stock_request.sudo().id))

    @http.route(["/my/stock_request/<int:request_id>/receive"], type="http", auth="user", website="True")
    def portal_my_stock_request_receive(self, request_id=None, access_token=None, **kw):
        stock_request = request.env["stock.request"].browse(request_id)
        stock_request.action_receive()
        values = self._stock_request_get_page_view_values(stock_request, access_token, **kw)
        return request.redirect("/my/stock_request/" + str(stock_request.sudo().id))
    
    @http.route(["/my/stock_request/<int:request_id>/approve"], type="http", auth="user", methods=["POST"], website="True")
    def portal_my_stock_request_approve(self, request_id=None, access_token=None, **kw):
        if kw.get("date_required"):
            self.portal_my_stock_request_save(access_token=access_token, **kw)
        stock_request = request.env["stock.request"].browse(request_id)
        stock_request.sudo().action_approve()
        values = self._stock_request_get_page_view_values(stock_request, access_token, **kw)
        return request.redirect("/my/stock_request/")
    
    @http.route(["/my/stock_request/save"], type="http", auth="user", methods=["POST"], website="True")
    def portal_my_stock_request_save(self, access_token=None, **kw):
        line_ids = []
        existing_line_ids = []
        for key, value in kw.items():
            if "product_id_" in key:
                number = key.replace("product_id_", "")
                product_id = int(kw.get(key))
                quantity = float(kw.get("quantity_" + number))
                line_id = int(kw.get("line_id_" + number))
                if line_id:
                    existing_line_ids.append(line_id)
                    line_vals = (1, line_id, {
                        "product_id": product_id,
                        "quantity": quantity,
                    })
                else:
                    line_vals = (0, 0, {
                        "product_id": product_id,
                        "quantity": quantity,
                    })
                line_ids.append(line_vals)
        vals = {
            "date_required": kw.get("date_required"),
            "line_ids": line_ids,
        }
        res_obj = request.env["stock.request"]
        if kw.get("id"): # edit
            res = res_obj.browse(int(kw.get("id"))).sudo()
            deleted_line_ids = set(res.line_ids.ids) - set(existing_line_ids)
            for line_id in deleted_line_ids:
                vals["line_ids"].append((2, line_id))
            res.write(vals)
        else: # create
            vals["user_id"] = request.env.uid
            res = res_obj.sudo().create(vals)
        approver_ids = res.approver_ids and res.approver_ids.ids
        return request.redirect("/my/stock_request/" + str(res.sudo().id))