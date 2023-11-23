# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request


class PortalInscription(CustomerPortal):
        def _prepare_home_portal_values(self):
                values = super(PortalInscription, self)._prepare_home_portal_values()
                doc_count = values.get("doc_count") or 0
                training_doc_count = request.env['training.edu'].sudo().get_doc_training_count()

                values["doc_count"] = doc_count + training_doc_count
                return values