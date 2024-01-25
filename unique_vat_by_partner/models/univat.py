# -*- coding: utf-8 -*-
###############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2020-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
#16.0.1
class UniVat(models.Model):
    _inherit = 'res.partner'

    @api.constrains("vat")
    def _check_vat_unique(self):
        for record in self:
            if record.parent_id or not record.vat:
                continue
            if record.same_vat_partner_id:
                raise ValidationError(
                    _("El número de identificación (%s) ya existe actualmente en otro contacto.") % record.vat
                )