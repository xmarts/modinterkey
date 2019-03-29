## -*- coding: utf-8 -*-

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


#from requests_toolbelt import MultipartEncoder

"""
class LogPlugin(MessagePlugin):
    def sending(self, context):
        print(str(context.envelope))
    def received(self, context):
        print(str(context.reply))
"""
auth_production_url  = 'https://services.sw.com.mx/security/authenticate'
auth_testing_url     = 'http://services.test.sw.com.mx/security/authenticate'

production_url      = 'https://services.sw.com.mx/cfdi33/stamp/v4'
testing_url         = 'http://services.test.sw.com.mx/cfdi33/stamp/v4'
_logger = logging.getLogger(__name__)

class AccountInvoiceLIne(models.Model):
    _inherit ='account.invoice.line'
    costo= fields.Float(string='Costo')
    utilidad = fields.Float(string='Utilidad')

    @api.onchange('product_id')
    def costoproduct_onchange(self):
        self.costo=self.product_id.standard_price
    @api.model
    def create(self,vals):
        #producto = self.env['product.product'].search([('id','=',vals['product_id'])])
        if 'costo' in vals:
            costo= vals['costo']
            total=  vals['price_unit'] - costo
            vals['utilidad']=total * vals['quantity']
        else:
            producto = self.env['product.product'].search([('id', '=', vals['product_id'])])
            costo = producto.standard_price
            total = vals['price_unit'] - costo
            vals['costo'] = costo
            vals['utilidad'] = total * vals['quantity']
        return super(AccountInvoiceLIne,self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get("costo") is not None:
            costo = vals.get("costo")
            precio =self.price_unit
            qty=self.quantity
            total = precio- costo
            vals['utilidad'] = total * qty
        return super(AccountInvoiceLIne, self).write(vals)
class AccountInvoice(models.Model):
    _inherit='account.invoice'
    
    ganancy= fields.Float(string="ganancia", store=True, compute="_compute_ganancy")

    amount_to_text = fields.Char(compute='_get_amount_to_text', string='Monto en Texto', readonly=True,
                                 help='Amount of the invoice in letter')
    
    @api.one
    @api.depends('amount_total')
    def _get_amount_to_text(self):
        self.amount_to_text = amount_to_text.get_amount_to_text(self, self.amount_total, self.currency_id.name)

    # @api.one
    #def generate(self):
        #if self.state !='draft':
            #valor =self.create_qr_image(self.amount_total)
           # self.write({'cfdi_cbb': valor})
    # def create_qr_image(self, amount_total):
    #     url = "https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx"
    #     UUID = self.cfdi_folio_fiscal

    #     qr_emisor = self.partner_id.vat_split
    #     qr_receptor = self.company_id.vat_split
    #     total = "%.6f" % (amount_total or 0.0)
    #     total_qr = ""
    #     qr_total_split = total.split('.')
    #     decimales = qr_total_split[1]
    #     index_zero = self.return_index_floats(decimales)
    #     decimales_res = decimales[0:index_zero + 1]
    #     if decimales_res == '0':
    #         total_qr = qr_total_split[0]
    #     else:
    #         total_qr = qr_total_split[0] + "." + decimales_res

    #     last_8_digits_sello = ""


    #     cfdi_sello = self.cfdi_sello

    #     last_8_digits_sello = cfdi_sello[len(cfdi_sello) - 8:]

    #     qr_string = '%s&id=%s&re=%s&rr=%s&tt=%s&fe=%s' % (
    #     url, UUID, qr_emisor, qr_receptor, total_qr, last_8_digits_sello)

    #     qr_code = QR(data=qr_string.encode('utf-8'))
    #     try:
    #         qr_code.encode()
    #     except Exception as e:
    #         raise UserError(_('Advertencia !!!\nNo se pudo crear el Código Bidimensional. Error %s') % e)
    #     if qr_code.filename is None:
    #         pass
    #     else:
    #         qr_file = open(qr_code.filename, "rb")
    #         temp_bytes = qr_file.read()
    #         qr_bytes = base64.encodestring(temp_bytes)
    #         qr_file.close()

    #     return qr_bytes or False

    # @api.one
    # def _compute_bank(self):
    #     bank_obj = self.env['res.partner.bank']
    #     partner=self.company_emitter_id.partner_id
    #     bank_ids = bank_obj.search([('partner_id', '=', partner.id)])
    #     bank =''
    #     apa = True
    #     for bk in bank_ids:
    #         bank = bank+ ' '+str(bk.acc_number)
    #     self.bank = bank

    # @api.one
    # def _compute_banks(self):
    #     bank_obj = self.env['res.partner.bank']
    #     partner = self.company_emitter_id.partner_id
    #     bank_ids = bank_obj.search([('partner_id', '=', partner.id)])
    #     bank = ''
    #     apa = True
    #     for bk in bank_ids:
    #         bank = bank + ' ' + str(bk.bank_id.name)
    #     self.banco = bank

    # @api.one
    # def _compute_clabe(self):
    #     bank_obj = self.env['res.partner.bank']
    #     partner = self.company_emitter_id.partner_id
    #     bank_ids = bank_obj.search([('partner_id', '=', partner.id)])
    #     bank = ''
    #     apa = True
    #     for bk in bank_ids:
    #         bank = bank + ' ' + str(bk.clabe)
    #     self.clabe= bank

    # bank = fields.Char(string="Banco clave interbancaria")
    # banco =fields.Char(string="Banco")
    # clabe = fields.Char(string="Clabe")
    # bank = fields.Char(string="Banco clave interbancaria",compute="_compute_bank")
    # banco =fields.Char(string="Banco",compute="_compute_banks")
    # clabe = fields.Char(string="Clabe", compute="_compute_clabe")

    @api.depends('invoice_line_ids')
    @api.one
    def _compute_ganancy(self):
        total=0
        for i in self.invoice_line_ids:
            total += i.utilidad
        self.ganancy = total

    invoice_line_ids = fields.One2many('account.invoice.line', 'invoice_id', string='Invoice Lines',
                                       oldname='invoice_line',
                                       readonly=True, states={'draft': [('readonly', False)],'open': [('readonly', False)]}, copy=True)

class AccountPayment(models.Model):
    _inherit ='account.payment'
    
    # @api.multi
    # def get_teamwise_commission(self):
    #     sum_line_manager = []
    #     sum_line_person = []
    #     amount_person, amount_manager = 0.0, 0.0
    #     for payment in self:
    #         if not payment.sales_team_id:
    #             raise Warning(_('Plaese select Sales Team.'))
    #         if not payment.sales_user_id:
    #             raise Warning(_('Plaese select Sales User.'))
    #         if payment.invoice_ids:
    #             for invoice in payment.invoice_ids:
    #                 ##modificacion naye
    #                 sum_line_manager.append((invoice.ganancy * invoice.team_id.sales_manager_commission)/100)
    #                 sum_line_person.append((invoice.ganancy * invoice.team_id.sales_person_commission)/100)
    #             amount_manager = sum(sum_line_manager)
    #             amount_person = sum(sum_line_person)
    #         else:
    #             amount_manager = (invoice.ganancy * payment.sales_team_id.sales_manager_commission)/100
    #             amount_person =  (invoice.ganancy * payment.sales_team_id.sales_person_commission)/100
    #     return amount_person, amount_manager

    # @api.multi
    # def create_commission(self, amount, commission, type):
    #     commission_obj = self.env['sales.commission.line']
    #     product = self.env['product.product'].search([('is_commission_product', '=', 1)], limit=1)
    #     for payment in self:
    #         if payment.invoice_ids:
    #             for invoice in payment.invoice_ids:
    #                 # Salesperson
    #                 if amount != 0.0:
    #                     commission_value = {
    #                         # 'sales_team_id': invoice.team_id.id,
    #                         # 'commission_user_id': invoice.user_id.id,
    #                         'amount': amount,
    #                         'origin': payment.name,
    #                         'type': type,
    #                         'product_id': product.id,
    #                         'date': payment.payment_date,
    #                         'src_payment_id': payment.id,
    #                         'src_invoice_id': invoice.id,
    #                         'invoice_id': invoice.id,
    #                         'sales_commission_id': commission.id,
    #                     }
    #                     commission_id = commission_obj.create(commission_value)
    #                     if type == 'sales_person':
    #                         payment.commission_person_id = commission_id.id
    #                     if type == 'sales_manager':
    #                         payment.commission_manager_id = commission_id.id
    #         else:
    #             if amount != 0.0:
    #                 commission_value = {
    #                     # 'sales_team_id': payment.team_id.id,
    #                     # 'commission_user_id': payment.user_id.id,
    #                     'amount': amount,
    #                     'origin': payment.name,
    #                     'src_invoice_id': invoice.id,
    #                     'type': type,
    #                     'product_id': product.id,
    #                     'date': payment.payment_date,
    #                     'src_payment_id': payment.id,
    #                     'sales_commission_id': commission.id,
    #                 }
    #                 commission_id = commission_obj.create(commission_value)
    #                 if type == 'sales_person':
    #                     payment.commission_person_id = commission_id.id
    #                 if type == 'sales_manager':
    #                     payment.commission_manager_id = commission_id.id

    #     return True

    """@api.multi
    def post(self):
        res = super(AccountPayment, self).post()
        when_to_pay = self.env['ir.values'].get_default('sale.config.settings', 'when_to_pay')
        
        if  when_to_pay == 'invoice_payment':
            for payment in self:
                if payment.sales_commission_apply:
                    commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
                    amount_person, amount_manager = 0.0,0.0
                    # if commission_based_on == 'sales_team':
                    #     amount_person, amount_manager = payment.get_teamwise_commission()
                    if commission_based_on == 'sales_team':
                        #amount_person, amount_manager = payment.get_teamwise_commission()
                        #if payment.invoice_ids:
                        #    for invoice in payment.invoice_ids:
                        #        amount_manager = amount_manager + ((payment.amount * invoice.team_id.sales_manager_commission)/100)
                        #        amount_person = amount_person + ((payment.amount * invoice.team_id.sales_person_commission)/100)
                        #else:
                        commission_obj = self.env['sales.commission.line']
                        product = self.env['product.product'].search([('is_commission_product','=',1)],limit=1)
                        if payment.invoice_ids:
                            for invoice in payment.invoice_ids:
                                commission_line = self.env['sales.commission.line'].search([
                                ('src_invoice_id', '=', invoice.id),
                                ],
                                limit=1)

                                if not commission_line:
                                    amount_manager = (invoice.ganancy * payment.sales_team_id.sales_manager_commission)/100
                                    amount_person =  (invoice.ganancy * payment.sales_team_id.sales_person_commission)/100

                                    commission = self.env['sales.commission'].search([
                                    ('commission_user_id', '=', payment.sales_user_id.id),
                                    ('start_date', '<=', payment.payment_date),
                                    ('end_date', '>=', payment.payment_date),
                                    ('state','=','draft')],limit=1)

                                    if not commission:
                                        commission = payment.create_base_commission(type='sales_person')

                                    if amount_person > 0.0:
                                        commission_value = {
                                            # 'sales_team_id': invoice.team_id.id,
                                            #'commission_user_id': invoice.user_id.id,
                                            'src_invoice_id': invoice.id,
                                            'invoice_id': invoice.id,
                                            'amount': amount_person,
                                            'origin': payment.name,
                                            'type':'sales_person',
                                            'product_id': product.id,
                                            'date' : payment.payment_date,
                                            'src_payment_id': payment.id,
                                            'sales_commission_id':commission.id,
                                        }
                                        commission_id = commission_obj.create(commission_value)
                                        if type == 'sales_person':
                                            payment.commission_person_id = commission_id.id
                                        if type == 'sales_manager':
                                            payment.commission_manager_id = commission_id.id

                                    #payment.create_commission(amount_person, commission, type='sales_person')

                                    if not payment.sales_user_id.id == payment.sales_team_id.user_id.id and payment.sales_team_id.user_id:
                                        commission = self.env['sales.commission'].search([
                                            ('commission_user_id', '=', payment.sales_team_id.user_id.id),
                                            ('start_date', '<=', payment.payment_date),
                                            ('end_date', '>=', payment.payment_date),
                                            ('state','=','draft')],limit=1)
                                        if not commission:
                                            commission = payment.create_base_commission(type='sales_manager')


                                        if amount_manager > 0.0:
                                            commission_value = {
                                                # 'sales_team_id': invoice.team_id.id,
                                                #'commission_user_id': invoice.user_id.id,
                                                'src_invoice_id': invoice.id,
                                                'amount': amount_manager,
                                                'origin': payment.name,
                                                'type':'sales_manager',
                                                'product_id': product.id,
                                                'date' : payment.payment_date,
                                                'src_payment_id': payment.id,
                                                'sales_commission_id':commission.id,
                                            }
                                            commission_id = commission_obj.create(commission_value)
                                            if type == 'sales_person':
                                                payment.commission_person_id = commission_id.id
                                            if type == 'sales_manager':
                                                payment.commission_manager_id = commission_id.id

                                        #payment.create_commission(amount_manager,commission, type='sales_manager')


                        else:
                            amount_manager = (payment.amount * payment.sales_team_id.sales_manager_commission)/100
                            amount_person =  (payment.amount * payment.sales_team_id.sales_person_commission)/100

                            commission = self.env['sales.commission'].search([
                                ('commission_user_id', '=', payment.sales_user_id.id),
                                ('start_date', '<=', payment.payment_date),
                                ('end_date', '>=', payment.payment_date),
                                ('state','=','draft')],limit=1)
                            if not commission:
                                commission = payment.create_base_commission(type='sales_person')
                            payment.create_commission(amount_person, commission, type='sales_person')
                            
                            if not payment.sales_user_id.id == payment.sales_team_id.user_id.id and payment.sales_team_id.user_id:
                                commission = self.env['sales.commission'].search([
                                    ('commission_user_id', '=', payment.sales_team_id.user_id.id),
                                    ('start_date', '<=', payment.payment_date),
                                    ('end_date', '>=', payment.payment_date),
                                    ('state','=','draft')],limit=1)
                                if not commission:
                                    commission = payment.create_base_commission(type='sales_manager')
                                payment.create_commission(amount_manager,commission, type='sales_manager')
                    
        return res
        """