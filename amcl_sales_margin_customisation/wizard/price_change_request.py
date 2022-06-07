# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import uuid

class PriceChangeRequest(models.TransientModel):
    _name = "price.change.request"

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        readonly=True,
    )
    line_ids = fields.One2many(
        'price.change.request.line',
        'change_id',
        string='Line'
    )

    def action_create_request(self):
        price_change = self.env['price.change.approval']
        for line in self.line_ids:
            if not self.env['price.change.approval'].search([('sequence_id', '=', line.sequence_id)]):
                print('Price :: ', line.user_ids)
                price_change.create({
                    'name': line.sale_order_id.partner_id.id,
                    'sale_id': line.sale_order_id.id,
                    'sale_line_id': line.order_line_id.id,
                    'product_id': line.product_id.id,
                    'price_unit': line.price_unit,
                    'change_unit': line.change_unit,
                    'user_ids': line.user_ids,
                    'state': 'send',
                    'company_id': self.env.company.id,
                    'requester_id': self.env.user.id,
                    'sequence_id': line.sequence_id
                })


class StockReservationLine(models.TransientModel):
    _name = "price.change.request.line"

    change_id = fields.Many2one(
        'price.change.request',
        string='Change',
    )
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        related="change_id.sale_order_id",
        store=True,
    )
    order_line_id = fields.Many2one(
        'sale.order.line',
        string='Sale Order Line',
        required=True,
        ondelete='cascade',
        # domain=lambda self: [
        #     ('order_id', '=', self._context.get('current_sale_order_id'))],
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )
    price_unit = fields.Float(
        string='Unit Price',
        related='order_line_id.price_unit',
        store=True
    )
    change_unit = fields.Float(
        string='Change Price',
    )
    user_ids = fields.Many2many(
        'res.users',
        string='Approval Users',
    )
    sequence_id = fields.Char(
        'Sequence',
        default=lambda self: str(uuid.uuid4())
    )

    @api.onchange("order_line_id")
    def _onchange_order_line_id(self):
        self.product_id = self.order_line_id.product_id.id
        self.price_unit = self.order_line_id.price_unit

    @api.onchange("change_unit")
    def _onchange_change_unit(self):
        approvals = self.env['sale.price.approval'].sudo().search(
            [('company_id', '=', self.env.company.id)], order='id ASC')[0]
        if not approvals:
            raise ValidationError('Please configure the approval settings.')

        if approvals:
            if self.change_unit > self.product_id.standard_price:
                self.user_ids = [(6, 0, approvals.line_id.filtered(lambda a: a.condition == 'senior').user_ids.ids)]

            elif self.change_unit >= self.product_id.standard_price:
                self.user_ids = [(6, 0, approvals.line_id.filtered(lambda a: a.condition == 'manager').user_ids.ids)]
            else:
                self.user_ids = [(6, 0, approvals.line_id.filtered(lambda a: a.condition == 'owner').user_ids.ids)]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
