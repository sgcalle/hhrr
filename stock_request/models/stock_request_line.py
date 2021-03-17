#-*- coding:utf-8 -*-

from odoo import models, fields, api

class StockRequestLine(models.Model):
    _name = "stock.request.line"
    _description = "Stock Request Line"
    _rec_name = "product_id"

    product_id = fields.Many2one(string="Product",
        comodel_name="product.product",
        required=True,
        domain="[('stock_request_ok','=',True)]")
    uom_id = fields.Many2one(string="UoM",
        comodel_name="uom.uom",
        related="product_id.uom_id")
    quantity = fields.Float(string="Requested Quantity")
    request_id = fields.Many2one(string="Request",
        comodel_name="stock.request",
        required=True,
        ondelete="cascade")
    employee_id = fields.Many2one(string="Employee",
        comodel_name="hr.employee",
        related="request_id.employee_id",
        store=True)
    department_id = fields.Many2one(string="Department",
        comodel_name="hr.department",
        related="request_id.department_id",
        store=True)
    request_create_date = fields.Datetime(string="Date Requested",
        related="request_id.create_date",
        store=True)
    date_required = fields.Date(string="Date Required",
        related="request_id.date_required",
        store=True)
    state = fields.Selection(string="State",
        related="request_id.state",
        store=True)
    stage_id = fields.Many2one(string="Stage",
        comodel_name="stock.request.stage",
        related="request_id.stage_id",
        store=True)
    delivered_quantity = fields.Float(string="Delivered Quantity",
        copy=False,
        compute="_compute_delivered_quantity",
        compute_sudo=True,
        store=True,
        default=0.0)
    move_ids = fields.One2many(string="Moves",
        comodel_name="stock.move",
        inverse_name="stock_request_line_id")
    unit_cost = fields.Float(string="Unit Cost",
        compute="_compute_unit_cost",
        store=True)
    total_cost = fields.Float(string="Total Cost",
        compute="_compute_total_cost",
        store=True)

    @api.model
    def create(self, vals):
        res = super(StockRequestLine, self).create(vals)
        if res.product_id.categ_id.stock_request_cost_method == "upon_request":
            res.unit_cost = res.product_id.standard_price
        return res

    @api.depends("product_id.categ_id.stock_request_cost_method",
        "product_id.standard_price",
        "product_id.categ_id.stock_request_cost_from_valuation")
    def _compute_unit_cost(self):
        for line in self:
            result = line.unit_cost or 0
            if line.product_id.categ_id.stock_request_cost_method == "product_cost":
                result = line.product_id.standard_price
            line.unit_cost = result
    
    @api.depends("unit_cost",
        "product_id.categ_id.stock_request_cost_basis",
        "product_id.categ_id.stock_request_cost_from_valuation",
        "move_ids.stock_valuation_layer_ids")
    def _compute_total_cost(self):
        for line in self:
            if line.product_id.categ_id.stock_request_cost_from_valuation and line.product_id.type == "product":
                total = 0
                for move in line.move_ids:
                    for layer in move.stock_valuation_layer_ids:
                        total += (layer.value * -1)
                line.total_cost = total
                line.unit_cost = total / (line.delivered_quantity or 1)
            else:
                if line.product_id.categ_id.stock_request_cost_basis == "requested":
                    line.total_cost = line.unit_cost * line.quantity
                else:
                    line.total_cost = line.unit_cost * line.delivered_quantity

    def _prepare_procurement_group_vals(self):
        return {
            "name": self.request_id.name,
            "move_type": "direct",
            "stock_request_id": self.request_id.id,
            "partner_id": self.request_id.user_id.partner_id.id,
        }

    def _prepare_procurement_values(self, group_id=False):
        self.ensure_one()
        values = {
            "group_id": group_id,
            "stock_request_line_id": self.id,
            "date_planned": self.request_id.date_required,
            "warehouse_id": self.request_id.warehouse_id,
            "partner_id": self.request_id.user_id.partner_id.id,
            "company_id": self.request_id.company_id,
        }
        return values

    def _action_launch_stock_rule(self):
        procurements = []
        for line in self:
            if line.product_id.categ_id.stock_request_cost_method == "upon_transfer_creation":
                line.unit_cost = line.product_id.standard_price
            group_id = line.request_id.procurement_group_id
            if not group_id:
                group_id = self.env["procurement.group"].create(line._prepare_procurement_group_vals())
                line.request_id.procurement_group_id = group_id
            
            values = line._prepare_procurement_values(group_id=group_id)
            procurements.append(self.env["procurement.group"].Procurement(
                line.product_id, line.quantity, line.uom_id, self.env.ref("stock_request.stock_location_employees"),
                line.product_id.name, line.request_id.name, line.request_id.company_id, values))
        if procurements:
            self.env["procurement.group"].run(procurements)
        return True

    def _get_outgoing_incoming_moves(self):
        outgoing_moves = self.env["stock.move"]
        incoming_moves = self.env["stock.move"]
        for move in self.move_ids.filtered(lambda m: m.state != "cancel" and not m.scrapped and self.product_id == m.product_id):
            if move.location_dest_id.usage == "inventory":
                outgoing_moves |= move
            elif move.location_dest_id.usage != "inventory":
                incoming_moves |= move
        return outgoing_moves, incoming_moves

    @api.depends("move_ids.state", "move_ids.scrapped", "move_ids.product_uom_qty", "move_ids.product_uom")
    def _compute_delivered_quantity(self):
        for line in self:
            qty = 0.0
            outgoing_moves, incoming_moves = line._get_outgoing_incoming_moves()
            for move in outgoing_moves:
                if move.state == "done":
                    qty += move.product_uom._compute_quantity(move.product_uom_qty, line.uom_id, rounding_method="HALF-UP")
            for move in incoming_moves:
                if move.state == "done":
                    qty -= move.product_uom._compute_quantity(move.product_uom_qty, line.uom_id, rounding_method="HALF-UP")
            line.delivered_quantity = qty