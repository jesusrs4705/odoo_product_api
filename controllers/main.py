from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class ProductController(http.Controller):
    
    @http.route('/api_module/create_update_product', type='http', auth='public', methods=['POST'], csrf=False)
    def create_update_product(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            _logger.info("Datos recibidos: %s", data)
            
            # Verificar token de autorización
            if data.get('token') != "asdfghjklqwertyuiop":
                return request.make_response(
                    json.dumps({"error": "No autorizado"}),
                    headers={'Content-Type': 'application/json'},
                    status=401
                )
            
            # Verificar campos requeridos
            required_fields = ['name', 'type', 'description_sale', 'list_price', 'standard_price', 'default_code']
            for field in required_fields:
                if field not in data:
                    return request.make_response(
                        json.dumps({"error": f"Falta el campo requerido: {field}"}),
                        headers={'Content-Type': 'application/json'},
                        status=400
                    )
            
            # Usar un usuario específico con permisos (reemplaza 'admin' por tu usuario administrador)
            admin_user = request.env.ref('base.user_admin')
            env = request.env(user=admin_user.id)
            
            # Buscar producto existente
            product = env['product.template'].search([('default_code', '=', data['default_code'])], limit=1)
            
            product_template_data = {
                'name': data['name'],
                'type': data['type'],
                'description_sale': data['description_sale'],
                'standard_price': data['standard_price'],
                'default_code': data['default_code'],
            }
            
            if product:
                # Actualizar producto existente
                product.write(product_template_data)
                if product.product_variant_id:
                    product.product_variant_id.write({'list_price': data['list_price']})
                message = "Producto actualizado correctamente"
            else:
                # Crear nuevo producto
                new_product = env['product.template'].create(product_template_data)
                if new_product.product_variant_id:
                    new_product.product_variant_id.write({'list_price': data['list_price']})
                message = "Producto creado correctamente"
            
            return request.make_response(
                json.dumps({"message": message}),
                headers={'Content-Type': 'application/json'},
                status=200
            )
            
        except Exception as e:
            _logger.exception("Error procesando la solicitud")
            return request.make_response(
                json.dumps({"error": "Error interno del servidor", "details": str(e)}),
                headers={'Content-Type': 'application/json'},
                status=500
            )