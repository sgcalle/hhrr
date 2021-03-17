#-*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import MissingError, ValidationError

class StockRequest(models.Model):
    _name = "stock.request"
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin"]
    _description = "Stock Request"

    def _default_stage_id(self):
        company_id = self.env.company.id
        return self.env["stock.request.stage"].search([("company_id","=",company_id)], limit=1).id
    
    def _default_warehouse_id(self):
        company_id = self.env.company.id
        return self.env["stock.warehouse"].search([("company_id","=",company_id)], limit=1).id

    name = fields.Char(string="Name",
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _("New"))
    active = fields.Boolean(string="Active",
        default=True)
    date_required = fields.Date(string="Date Required",
        required=True,
        tracking=True)
    line_ids = fields.One2many(string="Lines",
        comodel_name="stock.request.line",
        inverse_name="request_id")
    stage_id = fields.Many2one(string="Stage",
        comodel_name="stock.request.stage",
        group_expand="_read_group_stage_ids",
        default=_default_stage_id,
        tracking=True)
    approver_ids = fields.Many2many(string="Approvers",
        comodel_name="res.users",
        relation="stock_request_approver_rel",
        compute="_compute_approver_ids",
        store=True)
    employee_id = fields.Many2one(string="Related Employee",
        comodel_name="hr.employee",
        compute="_compute_employee_id",
        store=True,
        tracking=True)
    user_id = fields.Many2one(sting="User",
        comodel_name="res.users",
        required=True,
        tracking=True)
    department_id = fields.Many2one(string="Department",
        comodel_name="hr.department",
        compute="_compute_employee_id",
        store=True,
        tracking=True)
    company_id = fields.Many2one(string="Company",
        comodel_name="res.company",
        required=True,
        index=True,
        default=lambda self: self.env.company)
    state = fields.Selection(string="Status",
        selection=[
            ("pending", "Pending"),
            ("rejected", "Rejected"),
            ("canceled", "Canceled"),
            ("received", "Received")],
        default="pending",
        tracking=True)
    is_approver = fields.Boolean(string="Is Approver",
        compute="_compute_is_approver")
    is_user = fields.Boolean(string="Is Approver",
        compute="_compute_is_user")
    prev_stage_id = fields.Many2one(string="Previous Stage",
        comodel_name="stock.request.stage",
        compute="_compute_adjacent_stages")
    next_stage_id = fields.Many2one(string="Next Stage",
        comodel_name="stock.request.stage",
        compute="_compute_adjacent_stages")
    picking_ids = fields.One2many(string="Transfers",
        comodel_name="stock.picking",
        inverse_name="stock_request_id")
    picking_count = fields.Integer(string="Transfers Count",
        compute="_compute_picking_count")
    procurement_group_id = fields.Many2one(string="Procurement Group",
        comodel_name="procurement.group",
        copy=False)
    warehouse_id = fields.Many2one(string="Warehouse",
        comodel_name="stock.warehouse",
        default=_default_warehouse_id,
        check_company=True)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env["stock.request.stage"].search([])
        return stage_ids

    @api.model
    def create(self, vals):
        if "company_id" in vals:
            vals["name"] = self.env["ir.sequence"].with_context(force_company=vals["company_id"]).next_by_code("stock.request") or _("New")
        else:
            vals["name"] = self.env["ir.sequence"].next_by_code("stock.request") or _("New")
        res = super(StockRequest, self).create(vals)
        return res
    
    def action_approve(self):
        self.ensure_one()
        self.stage_id = self.next_stage_id.id
        if self.stage_id.generate_picking and not self.picking_ids:
            if not self.warehouse_id:
                raise MissingError("Cannot generate transfer because there is no warehouse specified.")
            self.line_ids._action_launch_stock_rule()

    def action_pend(self):
        self.ensure_one()
        self.state = "pending"

    def action_reject(self):
        self.ensure_one()
        self.state = "rejected"
    
    def action_cancel(self):
        self.state = "canceled"
        if self.picking_ids.filtered(lambda p: p.state == "done"):
            raise ValidationError("You cannot cancel a stock request with validated transfers")
        self.picking_ids.action_cancel()

    def action_receive(self):
        self.ensure_one()
        self.state = "received"

    def _compute_access_url(self):
        super(StockRequest, self)._compute_access_url()
        for request in self:
            request.access_url = "/my/stock_request/%s" % (request.id)
    
    @api.depends("stage_id", "employee_id")
    def _compute_approver_ids(self):
        for request in self:
            approvers = request.stage_id.approver_ids
            if request.stage_id.dept_head_as_approver and request.employee_id:
                if request.department_id.manager_id.user_id:
                    approvers |= request.department_id.manager_id.user_id
                else:
                    raise MissingError("Department head does not have a related user.")
            request.approver_ids = approvers.ids
            request.message_subscribe(approvers.partner_id.ids)
    
    def _compute_is_approver(self):
        for request in self:
            if not request.sudo().approver_ids or self.env.uid in request.sudo().approver_ids.ids:
                request.is_approver = True
            else:
                request.is_approver = False
    
    def _compute_is_user(self):
        for request in self:
            request.is_user = (self.env.uid == request.sudo().user_id.id)
    
    def _compute_adjacent_stages(self):
        for request in self:
            next_stage = False
            prev_stage = False
            stage_ids = self.env["stock.request.stage"].search([]).ids
            if stage_ids:
                curr_stage_index = stage_ids.index(request.stage_id.id)
                if curr_stage_index < (len(stage_ids) - 1):
                    next_stage = stage_ids[curr_stage_index + 1]
                if curr_stage_index > 0:
                    prev_stage = stage_ids[curr_stage_index - 1]
            request.next_stage_id = next_stage
            request.prev_stage_id = prev_stage
    
    @api.depends("user_id")
    def _compute_employee_id(self):
        for request in self:
            employee = False
            department = False
            if request.user_id:
                matched_employee = self.env["hr.employee"].search([("user_id","=",request.user_id.id)])
                if not matched_employee:
                    raise MissingError("No employee related to this user.")
                employee = matched_employee.id
                department = matched_employee.department_id.id
            request.employee_id = employee
            request.department_id = department

    def _compute_picking_count(self):
        for request in self.sudo():
            request.picking_count = len(request.picking_ids)

    def get_product_uom(self, product_id=None):
        return self.env["product.product"].sudo().browse(product_id).uom_id.name if product_id else ""