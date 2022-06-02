# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountMoveLineInherit(models.Model):
    _inherit = "account.move.line"

    product_move_id = fields.Many2one('account.move.line', 'Product Line')


class AccountMoveInherit(models.Model):
    _inherit = "account.move"

    sale_order = fields.Many2one('sale.order', 'SO')
    anglo_saxon = fields.Boolean('Anglo Saxon')

    def button_draft(self):
        res = super(AccountMoveInherit, self).button_draft()
        self.write({'anglo_saxon': False})

    def _post(self, soft=True):
        if self._context.get('move_reverse_cancel'):
            return super()._post(soft)

        # Create additional COGS lines for customer invoices.
        for move in self:
            if not move.anglo_saxon:
                move.env['account.move.line'].create(self._stock_account_prepare_anglo_saxon_out_lines_vals_new())
                move.write({'anglo_saxon': True})

        posted = super()._post(soft)

        posted._stock_account_anglo_saxon_reconcile_valuation()
        return posted

    def _stock_account_prepare_anglo_saxon_out_lines_vals_new(self):
        lines_vals_list = []
        for move in self:
            if move.anglo_saxon is False:
                if not move.is_sale_document(include_receipts=True) or not move.company_id.anglo_saxon_accounting:
                    continue

                for line in move.invoice_line_ids:
                    # Filter out lines being not eligible for COGS.
                    if not line._eligible_for_cogs():
                        continue

                    # Retrieve accounts needed to generate the COGS.

                    accounts = (
                        line.product_id.product_tmpl_id
                            .with_company(line.company_id)
                            .get_product_accounts(fiscal_pos=move.fiscal_position_id)
                    )
                    debit_interim_account = accounts['stock_output']
                    if move.sale_order.sales_type_id:
                        credit_expense_account = move.sale_order.sales_type_id.expense_account
                    else:
                        credit_expense_account = accounts['expense'] or self.journal_id.default_account_id
                    if not debit_interim_account or not credit_expense_account:
                        continue

                    # Compute accounting fields.
                    sign = -1 if move.move_type == 'out_refund' else 1
                    price_unit = line._stock_account_get_anglo_saxon_price_unit()
                    balance = sign * line.quantity * price_unit

                    # Add interim account line.
                    lines_vals_list.append({
                        'name': line.name[:64],
                        'move_id': move.id,
                        'product_id': line.product_id.id,
                        'product_uom_id': line.product_uom_id.id,
                        'quantity': line.quantity,
                        'price_unit': price_unit,
                        'debit': balance < 0.0 and -balance or 0.0,
                        'credit': balance > 0.0 and balance or 0.0,
                        'account_id': debit_interim_account.id,
                        'exclude_from_invoice_tab': True,
                        'is_anglo_saxon_line': True,
                        'product_move_id': line.id,
                    })

                    # Add expense account line.
                    lines_vals_list.append({
                        'name': line.name[:64],
                        'move_id': move.id,
                        'product_id': line.product_id.id,
                        'product_uom_id': line.product_uom_id.id,
                        'quantity': line.quantity,
                        'price_unit': -price_unit,
                        'debit': balance > 0.0 and balance or 0.0,
                        'credit': balance < 0.0 and -balance or 0.0,
                        'account_id': credit_expense_account.id,
                        'analytic_account_id': line.analytic_account_id.id,
                        'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
                        'exclude_from_invoice_tab': True,
                        'is_anglo_saxon_line': True,
                        'product_move_id': line.id,
                    })
        return lines_vals_list
