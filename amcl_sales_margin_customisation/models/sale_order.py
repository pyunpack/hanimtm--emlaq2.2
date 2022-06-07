# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('sales_type_id')
    def _onchange_sales_type_id(self):
        for line in self.order_line:
            if line.product_id:
                line.product_id_change()

    def action_create_request(self):
        self.ensure_one()
        return {
            'name': _('Price Change Request'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'price.change.request',
            'view_id': self.env.ref('amcl_sales_margin_customisation.wiz_price_change_request_view').id,
            'type': 'ir.actions.act_window',
            'context': {
                'default_sale_order_id': self.id,
                'current_order_line_id': self.id,
            },
            'target': 'new'
        }

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sales_type_id = fields.Many2one(related='order_id.sales_type_id', string='Sales Type')

    @api.onchange('price_unit')
    def onchange_unit_price_change(self):
        price = self._get_display_price(self.product_id)
        if self.product_id and self.price_unit != price:
            margin = self.product_id.margin_price
            approvals = self.env['sale.price.approval'].sudo().search(
                [('company_id', '=', self.env.company.id)], order='id ASC')[0]
            rule = False
            if approvals:
                for line in approvals.line_id:
                    users = line.mapped('user_ids')
                    if self.env.user in users:
                        rule = line.condition
                        break

                if rule == 'normal' and self.price_unit != margin:
                    self.write({'price_unit': margin})
                    raise UserError(
                        _('You dont have authority to change the price.\n'
                          'To change the price, please submit the request')
                    )
                elif rule == 'senior':
                    if self.price_unit > self.product_id.standard_price:
                        self.write({'price_unit': self.price_unit})
                    else:
                        raise UserError(
                            _('You can not enter a Unit Price, equal to the cost price.\n'
                              'To change the price, please submit the request')
                        )
                elif rule == 'manager':
                    if self.price_unit >= self.product_id.standard_price:
                        self.write({'price_unit': self.price_unit})
                    else:
                        raise UserError(
                            _('You can not enter a Unit Price, less than the cost price.\n'
                              'To change the price, please submit the request')
                        )
                elif rule == 'owner':
                    self.write({'price_unit': self.price_unit})

            else:
                self.write({'price_unit': margin})

        # if margin > 0 and self.env.user.has_group(
        #         'sales_team.group_sale_salesman') and (
        #         not self.env.user.has_group('sales_team.group_sale_manager') or not self.env.user.has_group(
        #     'base.group_erp_manager')):
        #     if (self.price_unit != 0 and self.price_unit < margin) or (
        #             self.price_unit != 0 and self.price_unit < self.product_id.standard_price):
        #         self.write({'price_unit': margin})
        #         raise UserError(
        #             _('You can not enter a Unit Price, which is less than marginal amount or less than the cost.'))

    def _get_display_price(self, product):
        res = super(SaleOrderLine, self)._get_display_price(product)
        if self.product_id.property_global_margin:
            property_global_margin = self.product_id.property_global_margin

        elif not self.product_id.property_global_margin:
            property_global_margin = \
                self.env['global.margin'].sudo().search([('company_id', '=', self.env.company.id)], order='id ASC')[
                    0]
        else:
            raise ValidationError(_('Please configure the Global Margin and assign to Product.'))

        sales_type = property_global_margin.sales_type.filtered(
            lambda l: l.name.id == self.sales_type_id.id)
        if sales_type:
            if sales_type.type == 'percentage':
                res = res + ((res * sales_type.amount) / 100)
            else:
                res = res + sales_type.amount
        return res
