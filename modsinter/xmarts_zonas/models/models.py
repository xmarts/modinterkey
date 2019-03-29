## -*- coding: utf-8 -*-

from openerp import models, fields, api, _, tools
from openerp.exceptions import UserError, RedirectWarning, ValidationError
import xlrd
import shutil



class respartnerzonas(models.Model):
	_name = 'zonas.partner'

	name = fields.Char(string='Zona de Residencia', help='Coloca la zona de residencia para especificar la zona de localizacion', requiered=True)



class InheritZona(models.Model):

	_inherit = 'res.partner'

	# @api.model
	# def create(self, values):
	# 	# Override the original create function for the res.partner model
	# 	partner_name = self.env['res.partner'].search([('name','=',values['name'])],limit=1)
	# 	if partner_name:
	# 		raise UserError(_('Advertencia !!!\nYa existe alguien registrado con el nombre  %s') % values['name'])
	# 	partner_rfc = self.env['res.partner'].search([('vat','=',values['vat'])],limit=1)
	# 	if partner_rfc:
	# 		raise UserError(_('Advertencia !!!\nYa existe un registro con el rfc  %s') % values['vat'])
	# 	record = super(InheritZona, self).create(values)
	# 	return record

	# @api.multi
	# def write(self, values):
	# 	# Override the original create function for the res.partner model
	# 	if self.name != values['name']:
	# 		partner_name = self.env['res.partner'].search([('name','=',values['name']),('id','!=',self.id)],limit=1)
	# 		if partner_name:
	# 			raise UserError(_('Advertencia !!!\nYa existe alguien registrado con el nombre  %s') % values['name'])
	# 	if values['vat']:
	# 		partner_rfc = self.env['res.partner'].search([('vat','=',values['vat']),('id','!=',self.id)],limit=1)
	# 		if partner_rfc:
	# 			raise UserError(_('Advertencia !!!\nYa existe un registro con el rfc  %s') % values['vat'])
	# 	record = super(InheritZona, self).write(values)
	# 	return record

	zone = fields.Many2one('zonas.partner',string='Zona de Entrega', help='Coloca la zona de residencia para especificar la zona de localizacion')

	_sql_constraints = [('rfc_uniq','unique(vat)','EL RFC debe de ser unico, ya existe uno registrado.')]

	_sql_constraints = [('name_field_unique', 'unique(name)', 'El nombre de cliente ya existe')]




# class ReportClassName(models.AbstractModel):
# 	_name = 'report.account.invoice.report_invoice_document_interkey'

# 	@api.model
# 	def render_html(self, docids, data=None):
# 		print "data....", data
# 		docargs = {
# 			'doc_ids': self.ids,
# 			'doc_model': self.model,
# 			'data': data,
# 		}
# 		return self.env['report'].render('account.invoice.report_invoice_document_interkey', docargs)
