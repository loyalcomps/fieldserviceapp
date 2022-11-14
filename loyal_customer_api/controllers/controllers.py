# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import base64

from odoo import http
from odoo.addons.web.controllers.main import Session  # Import the class


class CustomSession(Session):  # Inherit in your custom class

# class Session(http.Controller):
    @http.route('/web/session/authenticate', type='json', auth="none")
    def authenticate(self, db, login, password, base_location=None):
        res = super(CustomSession, self).authenticate(db, login, password, base_location=None)
        uid = res.get('uid')
        # uid = request.session.uid
        users = request.env['res.users'].browse(uid)
        # res['user_image'] =  base64.encodestring(users.image_1920)
        res['user_image'] =  users.image_1920
        # res.write({'user_image': base64.encodestring(users.image_256)})
        return res

        # request.session.authenticate(db, login, password)
        # datas = kw.get('profile_image').stream.getvalue()
        # partner.sudo().write({'image': base64.encodestring(datas)})
        # return request.env['ir.http'].session_info()

class getCustomer(http.Controller):
    @http.route('/get_tags', auth='user',type="json",methods=['GET'])
    def getTags(self, **kw):
        try:
            category_ids = request.env['res.partner.category'].search_read([],['name'])
            return {"status":200,"message":"Success","data":category_ids}
        except Exception as e:
            return {"status":400,"message":"Failed","error":str(e)}
    @http.route('/get_customer', auth='user',type="json",methods=['GET','POST'])
    def getCustomer(self, **kw):
        try:
            customer_list = request.env['res.partner'].search_read([('customer_rank','>',0)],['name','email','phone','mobile','image_256','property_product_pricelist','vat','company_type','category_id','parent_id'])
            return {"status":200,"message":"Success","data":customer_list}
        except Exception as e:
            return {"status":400,"message":"Failed","error":str(e)}

    @http.route('/create_customer', auth='user',type="json",methods=['POST'])
    def createCustomer(self, **kw):
        try:
            kw['customer_rank']=1
            kw['category_id'] = [(4,tag) for tag in kw.get('tags')]
            kw.pop('tags')
            customer_id = request.env['res.partner'].create(kw)
            return {"status":201,"message":"Success","data":{'id':customer_id.id}}
        except Exception as e:
            return {"status":400,"message":"Failed","error":str(e)}
    @http.route('/update_customer', auth='user',type="json",methods=['PUT'])
    def updateCustomer(self, **kw):
        try:
            kw['category_id'] = [(6,0,kw.get('tags'))]
            kw.pop('tags')
            obj_partner = request.env['res.partner']
            obj_partner.browse([kw.get('id')]).write(kw)
            return {"status":202,"message":"Success","data":{'id':kw.get('id')}}
        except Exception as e:
            return {"status":400,"message":"Failed","error":str(e)}
    @http.route('/delete_customer', auth='user',type="json",methods=['DELETE'])
    def deleteCustomer(self, **kw):
        try:
            obj_partner = request.env['res.partner']
            obj_partner.browse([kw.get('id')]).unlink()
            return {"status":203,"message":"Success","data":{'id':kw.get('id')}}
        except Exception as e:
            return {"status":400,"message":"Failed","error":str(e)}
    @http.route('/archive_customer', auth='user',type="json",methods=['PUT'])
    def archiveCustomer(self, **kw):
        try:
            obj_partner = request.env['res.partner']
            kw['active']=0
            obj_partner.browse([kw.get('id')]).write(kw)
            return {"status":203,"message":"Success","data":{'id':kw.get('id')}}
        except Exception as e:
            return {"status":400,"message":"Failed","error":str(e)}

    @http.route('/create_sale_order', auth='user',type="json",methods=['POST'])
    def createSaleOrder(self, **kw):
        try:

            vals = []
            val = {
                'date_order': kw.get('date_order'),
                'partner_id': kw.get('partner_id'),
                "pricelist_id": kw.get('pricelist_id'),
                "payment_term_id":kw.get('payment_term_id'),
            }

            lines = []
            for line in kw.get('order_line'):
                l_val = {
                    'product_id': line.get('product_id'),
                    'product_template_id': line.get('product_template_id'),
                    'product_uom_qty': line.get('product_uom_qty'),
                    'product_uom': line.get('product_uom'),
                    'price_unit': line.get('price_unit'),
                    'tax_id': [(6, 0, line.get('tax_id'))],
                    'discount': line.get('discount'),
                }
                lines.append((0, 0, l_val))
            val['order_line'] = lines
            vals.append(val)
            sale_order_id = request.env['sale.order'].create(vals)
            return {"status":201,"message":"Success","data":{'id':sale_order_id.id}}
        except Exception as e:
            return {"status":400,"message":"Failed","error":str(e)}
    @http.route('/get_sale_product', auth='user',type="json",methods=['GET'])
    def getProducts(self, **kw):
        try:
            products = request.env['product.product'].search_read([('sale_ok','=',True)],
            ['name','lst_price','uom_id','taxes_id','categ_id','qty_available','image_variant_256'])
            print('products',products)
            return {"status":200,"message":"Success","data":products}
        except Exception as e:
            return {"status":400,"message":"Failed","error":str(e)}
    @http.route('/confirm_sale_order', auth="user", type="json",methods=["PUT"])
    def confirmSaleOrder(self,**kw):
        try:
            sale_order_id = kw.get('order_id')
            confirm = request.env['sale.order'].browse(sale_order_id).action_confirm()
            return {"status":201,"message":"Success","data":confirm}
        except Exception as e:
            return {"status":400,"message":"Failed","error":str(e)}
    @http.route('/get_delivery_orders', auth="user", type="json", methods=['GET'])
    def getDeliveryOrders(self,**kw):
        try:
            if not kw.get('user_id'):
                return {"status":400,"message":"Failed","error":"Value error: The sale person id is required."}

            delivery_ids = request.env['stock.picking'].search([('create_uid','=',kw.get('user_id')),('picking_type_code','=','outgoing')])
            vals = []
            for rec in delivery_ids:
                val = {'name':rec.name,
                        'origin':rec.origin,
                        'scheduled_date':rec.scheduled_date,
                        'date_deadline':rec.date_deadline,
                        'partner_id':rec.partner_id.name,
                        'state':dict(rec._fields['state'].selection).get(rec.state),
                        'state_value':rec.state,
                       'delivery_order_id':rec.id,
                        }
                lines = []
                for line in rec.move_ids_without_package:
                    l_val = {
                        'stock_move_id':line.id,
                        'product':line.product_id.display_name,
                        'product_uom_qty':line.product_uom_qty,
                        'forecast_availability':line.forecast_availability,
                        'quantity_done':line.quantity_done,
                        'product_uom':line.product_uom.name
                    }
                    lines.append(l_val)
                val['lines']=lines
                vals.append(val)
            return {"status":200,"message":"Success","data":vals}
        except Exception as e:
            return {"status":400,"message":"Failed","error":str(e)}
    @http.route('/set_delivery_order_quantity',auth="user",type="json",methods=['PUT'])
    def setDeliveryOrderQuantities(self,**kw):
        try:

            if not kw.get('delivery_id'):
                return {"status":400,"message":"Failed","error":"Value error: The delivery id is required."}
            delivery_id = request.env['stock.picking'].search([('id','=',kw.get('delivery_id'))])
            try:
                set_qty = delivery_id.action_set_quantities_to_reservation()
                return {"status":201,"message":"Success","data":"The quantities has been seuccessfully set."}

            except Exception as e:
                return {"status":400,"message":"Failed","error":str(e)}
        except Exception as e:
            return {"status":400,"message":"Failed","error":str(e)}
    @http.route('/unreserve_delivery_order_quantity',auth="user",type="json",methods=['PUT'])
    def unreserveDeliveryOrderQuantities(self,**kw):
        try:

            if not kw.get('delivery_id'):
                return {"status":400,"message":"Failed","error":"Value error: The delivery id is required."}
            delivery_id = request.env['stock.picking'].search([('id','=',kw.get('delivery_id'))])
            try:
                set_qty = delivery_id.do_unreserve()
                return {"status":201,"message":"Success","data":"The quantities has been seuccessfully unreserved."}

            except Exception as e:
                return {"status":400,"message":"Failed","error":str(e)}
        except Exception as e:
            return {"status":400,"message":"Failed","error":str(e)}
    @http.route('/validate_delivery_order',auth="user",type="json",methods=['PUT'])
    def validateDeliveryOrder(self,**kw):
        try:
            if not kw.get('delivery_id'):
                return {"status":400,"message":"Failed","error":"Value error: The delivery id is required."}
            delivery_id = request.env['stock.picking'].search([('id','=',kw.get('delivery_id'))])
            try:
                validate = delivery_id.button_validate()
                print('validate',validate)
                if validate:
                    return {"status":201,"message":"Success","data":"The delivery order has been validated successfully."}
                else:
                    return {"status":400,"message":"Success","data":"Something wrong happened while validating the Delivery Order."}

            except Exception as e:
                return {"status":400,"message":"Failed","error":str(e)}
        except Exception as e:
            return {"status":400,"message":"Failed","error":str(e)}
    @http.route('/cancel_delivery_order',auth="user",type="json",methods=['PUT'])
    def cancelDeliveryOrder(self,**kw):
        try:
            if not kw.get('delivery_id'):
                return {"status":400,"message":"Failed","error":"Value error: The delivery id is required."}
            delivery_id = request.env['stock.picking'].search([('id','=',kw.get('delivery_id'))])
            try:
                cancel = delivery_id.action_cancel()
                print('cancel',cancel)
                if cancel:
                    return {"status":201,"message":"Success","data":"The delivery order has been cancelled successfully."}
                else:
                    return {"status":400,"message":"Success","data":"Something wrong happened while validating the Delivery Order."}

            except Exception as e:
                return {"status":400,"message":"Failed","error":str(e)}
        except Exception as e:
            return {"status":400,"message":"Failed","error":str(e)}
        # print('set_qty',set_qty.dd)
    # @http.route('/get_customer_tax', auth='user',type="json",methods=['GET'])
    @http.route(['/get_tax/<int:tax_id>',
    '/get_customer_tax'], auth='user',type="json",methods=['GET'])
    def getCustomerTax(self, **kw):
        try:
            domain=[]
            if kw.get('tax_id'):
                domain = [('id','=',kw.get('tax_id'))]
            else:
                domain = [('type_tax_use','=','sale')]
            tax = request.env['account.tax'].search_read(domain,['name'])
            return {"status":200,"message":"Success","data":tax}
        except Exception as e:
            return {"status":400,"message":"Failed","error":str(e)}
    @http.route('/get_pricelist', auth="user", type="json", methods=['GET'])
    def getPricelist(self,**kw):
        try:
            pricelist_ids = request.env['product.pricelist'].search_read([],['name'])
            return {"status":200,"message":"Success","data":pricelist_ids}
        except Exception as e:
            return {"status":400,"message":"Failed","error":str(e)}

    @http.route('/get_payment_terms', auth="user", type="json", methods=['GET'])
    def getPaymentTerms(self,**kw):
        try:
            pricelist_ids = request.env['account.payment.term'].search_read([],['name'])
            return {"status":200,"message":"Success","data":pricelist_ids}
        except Exception as e:
            return {"status":400,"message":"Failed","error":str(e)}


    @http.route('/get_warehouse', auth="user", type="json", methods=['GET'])
    def getStockWarehouse(self,**kw):
        try:
            pricelist_ids = request.env['stock.warehouse'].search_read([],['name'])
            return {"status":200,"message":"Success","data":pricelist_ids}
        except Exception as e:
            return {"status":400,"message":"Failed","error":str(e)}
    @http.route('/get_product_category', auth="user", type="json", methods=['GET'])
    def getproductCategory(self,**kw):
        try:
            category_ids = request.env['product.category'].search_read([],['name'])
            return {"status":200,"message":"Success","data":category_ids}
        except Exception as e:
            return {"status":400,"message":"Failed","error":str(e)}


    @http.route('/get_customer_invoice', auth="user", type="json", methods=['GET'])
    def getCustoemrInvoice(self,**kw):
        try:
            if not kw.get('user_id'):
                return {"status":400,"message":"Failed","error":"Value error: The sale person id is required."}

            invoice_ids = request.env['account.move'].search([('invoice_user_id','=',kw.get('user_id')),('move_type', '=', 'out_invoice')])
            vals = []
            for rec in invoice_ids:
                val = {'name':rec.name,
                        'invoice_date':rec.invoice_date,
                        'currency':rec.currency_id.name,
                        'partner_id':rec.partner_id.name,
                        'partner_street':rec.partner_id.street,
                        'partner_street2':rec.partner_id.street2,
                        'partner_country':rec.partner_id.country_id.name,
                        'partner_state':rec.partner_id.state_id.name,
                        'partner_zip':rec.partner_id.zip,
                        'partner_phone':rec.partner_id.phone,
                        'partner_mobile':rec.partner_id.mobile,
                        'payment_reference':rec.payment_reference,
                        'state':dict(rec._fields['state'].selection).get(rec.state),
                        'state_value':rec.state,
                        'amount_total':rec.amount_total,
                        'amount_tax':rec.amount_tax,
                        'amount_untaxed':rec.amount_untaxed
                        }
                lines = []
                for line in rec.invoice_line_ids:
                    l_val = {
                        'invoice_line_id':line.id,
                        'product':line.product_id.display_name,
                        'quantity':line.quantity,
                        'uom_id':line.product_uom_id.id,
                        'uom_name':line.product_uom_id.name,
                        'price_unit':line.price_unit,
                        'price_subtotal':line.price_subtotal
                    }
                    tax_lines = []
                    for tax in line.tax_ids:
                        tax_lines.append({'id':tax.id,
                                            'amount':tax.amount,
                                            'name':tax.name})
                    l_val['taxes'] = tax_lines
                    lines.append(l_val)
                val['lines']=lines
                vals.append(val)
            return {"status":200,"message":"Success","data":vals}
        except Exception as e:
            return {"status":400,"message":"Failed","error":str(e)}
    @http.route('/create_customer_invoice', auth="user", type="json", methods=['POST'])
    def createCustoemrInvoice(self,**kw):
        try:
            vals = []
            val = {
                    'invoice_date':kw.get('invoice_date'),
                    'partner_id':kw.get('partner_id'),
                    'move_type':'out_invoice',
                    }
            lines = []
            for line in kw.get('invoice_lines'):
                l_val = {
                    'product_id':line.get('product_id'),
                    'quantity':line.get('quantity'),
                    'product_uom_id':line.get('product_uom_id'),
                    'price_unit':line.get('price_unit'),
                    'tax_ids':[(6,0,line.get('tax_ids'))]
                }
                lines.append((0,0,l_val))
            val['invoice_line_ids']=lines
            vals.append(val)
            invoice_id = request.env['account.move'].create(vals)
            print('invoice_id',invoice_id)
            return {"status":200,"message":"Success","data":invoice_id.id}
        except Exception as e:
            return {"status":400,"message":"Failed","error":str(e)}
    @http.route('/update_customer_invoice', auth="user", type="json", methods=['PUT'])
    def updateCustoemrInvoice(self,**kw):
        try:
            if not kw.get('invoice_id'):
                return {"status":400,"message":"Failed","error":"Invoice id is require to update the invoice."}
            val = {
                    'invoice_date':kw.get('invoice_date'),
                    'partner_id':kw.get('partner_id'),
                    'move_type':'out_invoice',
                    'invoice_payment_term_id':kw.get('invoice_payment_term_id')
                    }
            lines = []
            for line in kw.get('invoice_lines'):
                l_val = {
                    'product_id':line.get('product_id'),
                    'quantity':line.get('quantity'),
                    'product_uom_id':line.get('product_uom_id'),
                    'price_unit':line.get('price_unit'),
                    'tax_ids':[(6,0,line.get('tax_ids'))]
                }
                lines.append((0,0,l_val))
            val['invoice_line_ids']=lines
            invoice_id = request.env['account.move'].browse([kw.get('invoice_id')])
            invoice_id.line_ids.unlink()
            invoice_id.invoice_line_ids.unlink()
            invoice_id.write(val)
            return {"status":200,"message":"Success","data":invoice_id.id}
        except Exception as e:
            return {"status":400,"message":"Failed","error":str(e)}

    @http.route("/confirm_invoice", type="json", auth="user", methods=["PUT"])
    def confirmInvoice(self,**kw):
        try:
            if not kw.get('invoice_id'):
                return {"status":400,"message":"Failed","error":"Value error: The invoice id is required."}
            invoice_id = request.env['account.move'].search([('id','=',kw.get('invoice_id'))]).action_post()
            print('invoice_id',invoice_id)
            return {"status":200,"message":"Success","data":"Invoice successfully confirmed."}
        except Exception as e:
            return {"status":400,"message":"Failed","error":str(e)}
    # @http.route('/create_internal_transfer', auth="user", type="json", methods=["POST"])
    # def createInternalTransfer(self,**kw):
    #     try:


    @http.route("/get_sale_orders", type="json", auth="user", methods=["GET"])
    def get_sale_orders_values(self, **kw):
        try:
            if not kw.get('user_id'):
                return {"status": 400, "message": "Failed", "error": "Value error: The sale person id is required."}

            sale_orders = request.env['sale.order'].search([('user_id', '=', kw.get('user_id'))])
            vals = []
            for sales in sale_orders:
                val = {'partner_id': sales.partner_id.id,
                       'pricelist_id': sales.pricelist_id.id,
                       'date_order': sales.date_order,
                       'name':sales.name,
                       'company_id': sales.company_id.id,
                       'user_id': sales.user_id.id,
                       'state': sales.state,
                       'customer_name': sales.partner_id.name,
                       'pricelist_name': sales.pricelist_id.name,
                       'amount': sales.amount_total,
                       'sale_order_id': sales.id,

                       }
                sale_lines = []
                for line in sales.order_line:
                    line_vals = {

                        'name': line.name,
                        'price_unit': line.price_unit,
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.product_uom_qty,
                        'product_uom': line.product_id.uom_id.id,
                        'tax_id': [(6, 0, line.product_id.taxes_id.ids)],
                    }
                    sale_lines.append(line_vals)
                val['order_line'] = sale_lines
                vals.append(val)
            return {"status": 200, "message": "Success", "data": vals}
        except Exception as e:
            return {"status":400, "message" : "Failed", "error": str(e)}

    @http.route("/get_states", type="json", auth="user", methods=["GET"])
    def get_states_values(self, **kw):
        try:
            states = request.env['res.country.state'].search_read([], ['name'])
            return {"status": 200, "message": "Success", "data": states}
        except Exception as e:
            return {"status": 400, "message": "Failed", "error": str(e)}

    @http.route("/cancel_sale_order", type="json", auth="user", methods=["PUT"])
    def cancel_sale_order(self, **kw):
        try:
            if not kw.get('order_id'):
                return {"status": 400, "message": "Failed", "error": "Value error: The Order id is required."}
            order_id = request.env['sale.order'].search([('id', '=', kw.get('order_id'))]).action_cancel()
            return {"status": 200, "message": "Success", "data": "Cancelled"}
        except Exception as e:
            return {"status": 400, "message": "Failed", "error": str(e)}

    @http.route("/draft_sale_order", type="json", auth="user", methods=["PUT"])
    def draft_sale_order(self, **kw):
        try:
            if not kw.get('order_id'):
                return {"status": 400, "message": "Failed", "error": "Value error: The Order id is required."}
            order_id = request.env['sale.order'].search([('id', '=', kw.get('order_id'))]).action_draft()
            return {"status": 200, "message": "Success", "data": "Reset to Draft"}
        except Exception as e:
            return {"status": 400, "message": "Failed", "error": str(e)}

    @http.route("/get_country", type="json", auth="user", methods=["GET"])
    def get_country_values(self, **kw):
        try:
            states = request.env['res.country'].search_read([], ['name'])
            return {"status": 200, "message": "Success", "data": states}
        except Exception as e:
            return {"status": 400, "message": "Failed", "error": str(e)}

    @http.route("/get_company", type="json", auth="user", methods=["GET"])
    def get_company_values(self, **kw):
        try:
            states = request.env['res.company'].search_read([], ['name'])
            return {"status": 200, "message": "Success", "data": states}
        except Exception as e:
            return {"status": 400, "message": "Failed", "error": str(e)}


