# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self,vals):
        print('vals',vals)
        # print('vals',vals.dd)
        return super(SaleOrder,self).create(vals)

class CustomerInvoice(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self,vals):
        print('vals---------',vals)
        # print('vals',vals.dd)
        # print('vals',vals.dd)
        return super(CustomerInvoice,self).create(vals)
    def write(self,vals):
        print('vals+++++++++++',vals)
        # print('vals',vals.dd)
        # print('vals',vals.dd)
        return super(CustomerInvoice,self).write(vals)

    def _move_autocomplete_invoice_lines_write(self, vals):
        ''' During the write of an account.move with only 'invoice_line_ids' set and not 'line_ids', this method is called
        to auto compute accounting lines of the invoice. In that case, accounts will be retrieved and taxes, cash rounding
        and payment terms will be computed. At the end, the values will contains all accounting lines in 'line_ids'
        and the moves should be balanced.

        :param vals_list:   A python dict representing the values to write.
        :return:            True if the auto-completion did something, False otherwise.
        '''
        enable_autocomplete = 'invoice_line_ids' in vals and 'line_ids' not in vals and True or False
        print('enable_autocomplete--------',enable_autocomplete)
        print('vals000000000000--------',vals)
        if not enable_autocomplete:
            return False

        vals['line_ids'] = vals.pop('invoice_line_ids')
        for invoice in self:
            invoice_new = invoice.with_context(
                default_move_type=invoice.move_type,
                default_journal_id=invoice.journal_id.id,
                default_partner_id=invoice.partner_id.id,
                default_currency_id=invoice.currency_id.id,
            ).new(origin=invoice)
            invoice_new.update(vals)
            values = invoice_new._move_autocomplete_invoice_lines_values()
            values.pop('invoice_line_ids', None)
            invoice.write(values)
        return True
