from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SalePriceApproval(models.Model):
    _name = 'sale.price.approval'

    name = fields.Char('Name', required=True)
    line_id = fields.One2many('sale.price.approval.line', 'approval_id', 'Approval Line')
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

    _sql_constraints = [
        ('company_uniq', 'unique (company_id)', 'No duplicate is allowed.'),
    ]


class SalePriceApprovalLine(models.Model):
    _name = 'sale.price.approval.line'

    name = fields.Selection(
        [('normal', 'Normal Sales User'), ('senior', 'Senior Salesman'), ('manager', 'Branch Manager'),
         ('owner', 'Owner')], 'Approval Type', required=True)
    approval_id = fields.Many2one('sale.price.approval', 'Approvals')
    user_ids = fields.Many2many('res.users', string='Allowed Users')
    company_id = fields.Many2one('res.company', related='approval_id.company_id', store=True)
    condition = fields.Selection(
        [('normal', 'Can not edit the sales price'),
         ('senior', 'Can cell above cost, but not equal to cost'),
         ('manager', 'Can cell equal to cost'),
         ('owner', 'Full access')], 'Approval Condition', required=True)

    _sql_constraints = [
        ('name_company_uniq', 'unique (name, company_id)', 'No duplicate type is allowed.'),
    ]

    @api.onchange('name')
    def onchange_type(self):
        if self.name:
            if self.name == 'normal':
                self.condition = 'normal'
            elif self.name == 'senior':
                self.condition = 'senior'
            elif self.name == 'manager':
                self.condition = 'manager'
            elif self.name == 'owner':
                self.condition = 'owner'
