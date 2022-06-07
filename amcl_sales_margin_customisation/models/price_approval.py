# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PriceChangeApproval(models.Model):
    _name = "price.change.approval"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Many2one(
        'res.partner',
        string="Customer",
        required=True,
        readonly=True,
    )
    sale_id = fields.Many2one(
        'sale.order',
        string="Quotation/Order",
        readonly=True,
    )
    sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Line',
        required=True,
        readonly=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        readonly=True,
    )
    price_unit = fields.Float(
        string='Unit Price',
        required=True,
    )
    change_unit = fields.Float(
        string='New Unit Price',
        required=True,
    )
    user_ids = fields.Many2many(
        'res.users',
        string='Approval Users',
        required=True,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('send', 'Waiting for Approval'),
        ('approve', 'Approved'),
        ('cancel', 'Cancel')], string='State',
        default='draft')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company
    )
    sequence_id = fields.Char(
        'Sequence',
    )
    requester_id = fields.Many2one(
        'res.users',
        string='Requested User',
        required=True,
        readonly=True,
    )
    is_approver = fields.Boolean(
        'Approver',
        compute='_get_approver',
    )
    user = fields.Many2one('User', compute='_get_user')

    @api.depends()
    def _get_user(self):
        self.user = self.env.user.id


    @api.depends('state','user')
    def _get_approver(self):
        print('self.user_ids.ids :: ', self.user_ids.ids)
        if self.env.user.id in self.user_ids.ids and self.state == 'send':
            self.is_approver = True
        else:
            self.is_approver = False

    def action_approve(self):
        for approve in self:
            approve.sale_line_id.write({'price_unit': approve.change_unit})
            approve.state = 'approve'

    def action_reject(self):
        for approve in self:
            approve.state = 'cancel'


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
