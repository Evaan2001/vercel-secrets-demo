# Save this file as: api/update-dealers.py

from http.server import BaseHTTPRequestHandler
import os
import xmlrpc.client
import json
import redis

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Optional: Verify webhook secret for security
            webhook_secret = os.environ.get('WEBHOOK_SECRET')
            auth_header = self.headers.get('Authorization')
            
            if webhook_secret and auth_header != f'Bearer {webhook_secret}':
                self.send_json_response({
                    'error': 'Unauthorized'
                }, status=401)
                return
            
            # Connect to Vercel KV
            kv_url = os.environ.get('KV_REST_API_URL')
            kv_token = os.environ.get('KV_REST_API_TOKEN')
            
            if not kv_url or not kv_token:
                self.send_json_response({
                    'error': 'KV not configured'
                }, status=500)
                return
            
            # Fetch fresh data from Odoo
            dealers_data = self.fetch_from_odoo()
            
            # Update cache
            r = redis.from_url(kv_url, decode_responses=True, 
                             password=kv_token.split(':')[-1])
            r.set('dealers_cache', json.dumps(dealers_data))
            
            self.send_json_response({
                'success': True,
                'message': 'Cache refreshed successfully',
                'dealers_count': dealers_data.get('count', 0)
            })
            
        except Exception as e:
            self.send_json_response({
                'error': str(e)
            }, status=500)
        
        return
    
    def fetch_from_odoo(self):
        """Fetch fresh dealer data from Odoo"""
        url = 'https://mid-city-engineering.odoo.com/'
        db = 'mid-city-engineering'
        username = os.environ.get('ODOO_USERNAME')
        api_key = os.environ.get('ODOO_API_KEY')
        
        if not username or not api_key:
            raise Exception('ODOO_USERNAME and ODOO_API_KEY not set')
        
        # Connect to Odoo
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, api_key, {})
        
        if not uid:
            raise Exception('Odoo authentication failed')
        
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
        
        return {
            'success': True,
            'count': len(dealers),
            'dealers': dealers
        }
    
    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
