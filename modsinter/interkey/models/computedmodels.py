from openerp import models, fields, api, _, tools
from openerp.exceptions import UserError, RedirectWarning, ValidationError
import shutil
import logging
from xml.dom.minidom import parseString
import time
import codecs
from xml.dom import minidom
from datetime import datetime, timedelta
#from qrtools import QR

import qrcode
import os
import sys
import time
import tempfile
import base64
import binascii

import json
import requests
from . import amount_to_text		

class prueba(models.Model):
	_inherit = 'res.partner.bank'
	
	clabe = fields.Char(string="Clave")

class AddCampClave(models.Model):
	_inherit = 'res.partner'

	clabe = fields.Char(string="Clave")

class AddComputes(models.Model):
	_inherit ='account.invoice'

	bank = fields.Char(string="Banco clave interbancaria",compute="_compute_bank")
	banco =fields.Char(string="Banco",compute="_compute_banks")
	clabe = fields.Char(string="Clabe", compute="_compute_clabe")
	cuent_client = fields.Char(string="Cuenta cliente", compute="_compute_cuenta_cliente")
	ultim_digitos = fields.Char(string="Ultimos 4 dijitos", compute="_compute_digitos")

	@api.one
	def _compute_digitos(self):
		if self.move_name:
			self.ultim_digitos = self.move_name[-4:]

	@api.one
	def _compute_cuenta_cliente(self):
		bank_obj = self.env['res.partner.bank']
		partner=self.partner_id
		bank_ids = bank_obj.search([('partner_id', '=', partner.id)])
		bank =''
		apa = True
		for bk in bank_ids:
			bank = bank+ ' '+str(bk.acc_number)
		self.cuent_client = bank[-4:]

	@api.one
	def _compute_bank(self):
		bank_obj = self.env['res.partner.bank']
		partner=self.company_id.partner_id
		bank_ids = bank_obj.search([('partner_id', '=', partner.id)])
		bank =''
		apa = True
		for bk in bank_ids:
			bank = bank+ ' '+str(bk.acc_number)
		self.bank = bank

	@api.one
	def _compute_banks(self):
		bank_obj = self.env['res.partner.bank']
		partner = self.company_id.partner_id
		bank_ids = bank_obj.search([('partner_id', '=', partner.id)])
		bank = ''
		apa = True
		for bk in bank_ids:
			bank = bank + ' ' + str(bk.bank_id.name)
		self.banco = bank

	@api.one
	def _compute_clabe(self):
		bank_obj = self.env['res.partner.bank']
		partner = self.company_id.partner_id
		bank_ids = bank_obj.search([('partner_id', '=', partner.id)])
		bank = ''
		apa = True
		for bk in bank_ids:
			bank = bank + ' ' + str(bk.clabe)
		self.clabe= bank


	@api.multi
	def action_invoice_paid(self):
		if self.type == 'out_invoice':
			to_pay_invoices = self.filtered(lambda inv: inv.state != 'paid')
			if to_pay_invoices.filtered(lambda inv: inv.state not in ('open', 'in_payment')):
				raise UserError(_('Invoice must be validated in order to set it to register payment.'))
			if to_pay_invoices.filtered(lambda inv: not inv.reconciled):
				raise UserError(_('You cannot pay an invoice which is partially paid. You need to reconcile payment entries first.'))
			for invoice in to_pay_invoices:
				if any([move.journal_id.post_at_bank_rec and move.state == 'draft' for move in invoice.payment_move_line_ids.mapped('move_id')]):
					invoice.write({'state': 'in_payment'})
				else:
					when_to_pay = self.env['ir.config_parameter'].sudo().get_param('sales_commission_calculation.when_to_pay')
					if  when_to_pay == 'invoice_payment':
						for payment in self:
							commission_based_on = self.env['ir.config_parameter'].sudo().get_param('sales_commission_calculation.commission_based_on')
							if commission_based_on == 'sales_team':
								commission_obj = self.env['sales.commission.line']
								product = self.env['product.product'].search([('is_commission_product','=',1)],limit=1)
								commission_line = self.env['sales.commission.line'].search([('src_invoice_id', '=', payment.id),],limit=1)
								if not commission_line:
									commission = self.env['sales.commission'].search([
										('commission_user_id', '=', payment.user_id.id),
										('start_date', '<=', self.date.today()),
										('end_date', '>=', self.date.today()),
										('state','=','draft')],limit=1)
									if not commission:
										commission = payment.create_base_commission(type='sales_person')
									calculate = (payment.ganancy * payment.team_id.sales_person_commission)/100
									if calculate >= 0.0:
										commission_obj = self.env['sales.commission.line']
										commission_value = {
										'src_invoice_id': payment.id,
										'invoice_id': payment.id,
										'amount': calculate,
										'origin': payment.number,
										'type':'sales_person',
										'product_id': product.id,
										'date' : self.date.today(),
										'sales_commission_id':commission.id,
										}
										commission_id = commission_obj.create(commission_value)
					invoice.write({'state': 'paid'})
		elif self.type == 'out_refund':
			to_pay_invoices = self.filtered(lambda inv: inv.state != 'paid')
			if to_pay_invoices.filtered(lambda inv: inv.state not in ('open', 'in_payment')):
				raise UserError(_('Invoice must be validated in order to set it to register payment.'))
			if to_pay_invoices.filtered(lambda inv: not inv.reconciled):
				raise UserError(_('You cannot pay an invoice which is partially paid. You need to reconcile payment entries first.'))
			for invoice in to_pay_invoices:
				if any([move.journal_id.post_at_bank_rec and move.state == 'draft' for move in invoice.payment_move_line_ids.mapped('move_id')]):
					invoice.write({'state': 'in_payment'})
				else:
					when_to_pay = self.env['ir.config_parameter'].sudo().get_param('sales_commission_calculation.when_to_pay')
					if  when_to_pay == 'invoice_payment':
						for payment in self:
							commission_based_on = self.env['ir.config_parameter'].sudo().get_param('sales_commission_calculation.commission_based_on')
							if commission_based_on == 'sales_team':
								commission_obj = self.env['sales.commission.line']
								product = self.env['product.product'].search([('is_commission_product','=',1)],limit=1)
								commission_line = self.env['sales.commission.line'].search([('src_invoice_id', '=', payment.id),],limit=1)
								if not commission_line:
									commission = self.env['sales.commission'].search([
										('commission_user_id', '=', payment.user_id.id),
										('start_date', '<=', self.date.today()),
										('end_date', '>=', self.date.today()),
										('state','=','draft')],limit=1)
									if not commission:
										commission = payment.create_base_commission(type='sales_person')
									calculate = (payment.ganancy * payment.team_id.sales_person_commission)/100
									calculatep = calculate * -1
									if calculatep != 0.0:
										commission_obj = self.env['sales.commission.line']
										commission_value = {
										'src_invoice_id': payment.id,
										'invoice_id': payment.id,
										'amount': calculatep,
										'origin': payment.number,
										'type':'sales_person',
										'product_id': product.id,
										'date' : self.date.today(),
										'sales_commission_id':commission.id
										}
										commission_id = commission_obj.create(commission_value)
					invoice.write({'state': 'paid'})		
		

