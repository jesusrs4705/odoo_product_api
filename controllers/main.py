import json
import logging
from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)

class ProductAPI(http.Controller):
    
    @http.route('/custom_product_api/create_update_product', type='http', auth='none', methods=['POST'], csrf=False)
    def create_update_product(self, **kwargs):
        """
        Endpoint para crear/actualizar productos basado en referencia interna (default_code)
        Recibe JSON con datos del producto y token de validación
        """
        try:
            # Obtener datos JSON del cuerpo de la solicitud
            data = json.loads(request.httprequest.data.decode('utf-8'))
            
            # Validar token
            token = data.get('token')
            if token != 'asdfghjklqwertyuiop':
                return self._json_response(
                    {'error': 'No autorizado'}, 
                    status=401
                )
            
            # Campos requeridos
            required_fields = ['name', 'type', 'default_code']
            for field in required_fields:
                if field not in data:
                    return self._json_response(
                        {'error': f'Campo requerido faltante: {field}'}, 
                        status=400
                    )
            
            # Validar tipo de producto
            valid_types = ['consu', 'service', 'combo']
            if data.get('type') not in valid_types:
                return self._json_response(
                    {'error': f'Tipo de producto inválido. Debe ser uno de: {valid_types}'}, 
                    status=400
                )

            # Buscar la moneda "EUR" directamente
            currency = request.env['res.currency'].sudo().search([('name', '=', 'EUR')], limit=1)

            if not currency:
                _logger.error("No se encontró la moneda EUR.")
                return self._json_response({'error': 'No se encontró la moneda EUR.'}, status=500)

            # Preparar datos para creación/actualización
            product_data = {
                'name': data.get('name'),
                'type': data.get('type'),
                'default_code': data.get('default_code'),
                'currency_id': currency.id,
            }
            
            # Agregar campos opcionales
            if 'description_sale' in data:
                product_data['description_sale'] = data.get('description_sale')
            
            # Manejar correctamente los campos de precio
            if 'lst_price' in data:
                product_data['list_price'] = float(data.get('lst_price'))
            
            if 'standard_price' in data:
                product_data['standard_price'] = float(data.get('standard_price'))
            
            # Buscar producto existente por default_code
            Product = request.env['product.template'].sudo()
            existing_product = Product.search([('default_code', '=', data.get('default_code'))], limit=1)
            
            result = {}
            if existing_product:
                # Actualizar producto existente
                existing_product.write(product_data)
                product = existing_product
                result = {
                    'status': 'updated',
                    'product_id': product.id,
                    'name': product.name,
                    'default_code': product.default_code,
                    'list_price': product.list_price,
                    'standard_price': product.standard_price
                }
                _logger.info(f"Producto actualizado: {product.name} (ID: {product.id})")
            else:
                # Crear nuevo producto
                product = Product.create(product_data)
                result = {
                    'status': 'created',
                    'product_id': product.id,
                    'name': product.name,
                    'default_code': product.default_code,
                    'list_price': product.list_price,
                    'standard_price': product.standard_price
                }
                _logger.info(f"Producto creado: {product.name} (ID: {product.id})")
                
            return self._json_response(result, status=200)
            
        except Exception as e:
            _logger.error(f"Error al procesar la petición: {str(e)}")
            return self._json_response(
                {'error': f'Error interno del servidor: {str(e)}'}, 
                status=500
            )
    
    def _json_response(self, data, status=200):
        """Método auxiliar para retornar respuestas JSON con códigos de estado HTTP"""
        return Response(
            json.dumps(data),
            status=status,
            mimetype='application/json'
        )
