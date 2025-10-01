# Save this file as: api/update-dealers.py

from http.server import BaseHTTPRequestHandler
import os
import xmlrpc.client
import json
import traceback

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Log environment check
            kv_url = os.environ.get('KV_REST_API_URL')
            kv_token = os.environ.get('KV_REST_API_TOKEN')
            
            if not kv_url or not kv_token:
                error_msg = f'KV not configured. URL exists: {bool(kv_url)}, Token exists: {bool(kv_token)}'
                print(f'ERROR: {error_msg}')
                self.send_json_response({'error': error_msg}, status=500)
                return
            
            print('Starting cache refresh...')
            
            # Fetch fresh data from Odoo
            dealers_data = self.fetch_from_odoo()
            print(f'Fetched {dealers_data.get("count", 0)} dealers from Odoo')
            
            # Update cache
            try:
                from upstash_redis import Redis
                r = Redis(url=kv_url, token=kv_token)
                r.set('dealers_cache', json.dumps(dealers_data))
                print('Successfully updated cache')
            except ImportError as e:
                error_msg = f'upstash_redis not installed: {str(e)}'
                print(f'ERROR: {error_msg}')
                self.send_json_response({'error': error_msg}, status=500)
                return
            
            self.send_json_response({
                'success': True,
                'message': 'Cache refreshed successfully',
                'dealers_count': dealers_data.get('count', 0)
            })
            
        except Exception as e:
            error_msg = f'{type(e).__name__}: {str(e)}'
            error_trace = traceback.format_exc()
            print(f'ERROR: {error_msg}')
            print(f'TRACEBACK: {error_trace}')
            self.send_json_response({
                'error': error_msg,
                'traceback': error_trace
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
        
        print('Connecting to Odoo...')
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, api_key, {})
        
        if not uid:
            raise Exception('Odoo authentication failed')
        
        print(f'Authenticated as user ID: {uid}')
        
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
