# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class SaleType(models.Model):
    _inherit = 'sale.type'

    allow_auto_reservation = fields.Boolean('Allow auto reservation')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
