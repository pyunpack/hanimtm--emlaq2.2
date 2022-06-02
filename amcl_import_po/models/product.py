# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    model_year = fields.Char('Model Year')
    grade = fields.Char('Grade (VC)')
    exterior_color = fields.Char('Exterior Color (VC)', translate=True)
    interior_color = fields.Char('Interior Color (VC)', translate=True)
    transmission_type = fields.Selection(
        [('automatic', 'AUTOMATIC'),
         ('cvt', 'CVT'),
         ('manual', 'MANUAL')],
        default='automatic', string="Transmission Type")
    #vms_customer = fields.Char('VMS Customer')
    alj_suffix = fields.Char('ALJ Suffix (VC)')
    vehicle_model = fields.Char('Vehicle Model', translate=True)
    brand = fields.Char('Brand', translate=True)
    #description = fields.Char('Description')
    complete_engine_number = fields.Char('Complete Engine Number')
    model_code = fields.Char('Model Code', translate=True)
    #action = fields.Char('Action')
    sales_document = fields.Char('Sales Document')
    #request_delivery_date = fields.Date('Request Delivery Date')
    billing_document = fields.Char('Billing Document')
    bill_date = fields.Date('Bill Date')
    #vehicle_wholesale_price = fields.Float('Vehicle Wholesale Price')
    #broker_declaration_date = fields.Date('Broker Declaration Date')
    #declaration_date = fields.Date('Declaration Date')
    #netval = fields.Float('Net Val')
    #vat_amount = fields.Float('VAT Amount')
    #purchase_order = fields.Many2one('purchase.order', 'Purchase')
    item = fields.Char('Item')
    car_id = fields.Many2one('car.company', string='Company')
    product_vc = fields.Char('Product (VC)')


class Product(models.Model):
    _inherit = 'product.product'

    _sql_constraints = [
        ('barcode_uniq', 'unique(barcode , company_id)', "A barcode can only be assigned to one product !"),
    ]