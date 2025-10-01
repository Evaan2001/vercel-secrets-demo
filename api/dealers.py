from http.server import BaseHTTPRequestHandler
import os
import xmlrpc.client
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Get Odoo credentials from environment variables
            url = 'https://mid-city-engineering.odoo.com/'
            db = 'mid-city-engineering'
            username = os.environ.get('ODOO_USERNAME')
            api_key = os.environ.get('ODOO_API_KEY')
            
            # Check if credentials are available
            if not username or not api_key:
                self.send_json_response({
                    'error': 'ODOO_USERNAME and ODOO_API_KEY environment variables not set'
                }, status=500)
                return
            
            # Connect to Odoo
            common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
            uid = common.authenticate(db, username, api_key, {})
            
            if not uid:
                self.send_json_response({
                    'error': 'Authentication failed. Check your credentials.'
                }, status=401)
                return
            
            # Query dealers
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
            required_fields = ['name', 'partner_latitude', 'partner_longitude', 'x_latitude', 
                             'x_longitude', 'street', 'street2', 'city', 'state_id', 
                             'zip', 'country_id', 'phone', 'email']
            
            dealers = models.execute_kw(db, uid, api_key,
                                      'res.partner',
                                      'search_read',
                                      [[['category_id', '=', 'Dealer']]],
                                      {'fields': required_fields})
            
            # Send successful response
            self.send_json_response({
                'success': True,
                'count': len(dealers),
                'dealers': dealers
            })
            
        except Exception as e:
            self.send_json_response({
                'error': str(e)
            }, status=500)
        
        return
    
    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # Enable CORS
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
