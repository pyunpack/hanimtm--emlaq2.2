# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class SaleType(models.Model):
    _name = 'sale.type'
    _description = 'Sale Type'

    name = fields.Char(string='Sales Type')
    income_account = fields.Many2one('account.account', string='Income Account', index=True, ondelete="cascade")
    expense_account = fields.Many2one('account.account', string='Expense Account',
                                      index=True, ondelete="cascade")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    allowed_users = fields.Many2many('res.users', string='Allowed Users')
    ext_id = fields.Integer(string='Ext ID')
    auto_reservation = fields.Boolean(default=False)

    _sql_constraints = [
        ('uniq_name', 'unique(ext_id)', "This ext id already exists with this name . ext id name must be unique!"),
    ]






