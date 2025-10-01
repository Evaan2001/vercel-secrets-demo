from http.server import BaseHTTPRequestHandler
import os
import xmlrpc.client
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Check if KV variables exist
            kv_url = os.environ.get('KV_REST_API_URL')
            kv_token = os.environ.get('KV_REST_API_TOKEN')
            
            # For debugging - return this info
            if not kv_url or not kv_token:
                self.send_json_response({
                    'error': 'KV variables not found',
                    'kv_url_exists': bool(kv_url),
                    'kv_token_exists': bool(kv_token),
                    'env_vars': list(os.environ.keys())
                })
                return
            
            # Try upstash-redis
            try:
                from upstash_redis import Redis
                r = Redis(url=kv_url, token=kv_token)
                
                # Try to get from cache
                cached_data = r.get('dealers_cache')
                
                if cached_data:
                    data = json.loads(cached_data)
                    data['cached'] = True
                    self.send_json_response(data)
                else:
                    # Fetch from Odoo
                    dealers_data = self.fetch_from_odoo()
                    
                    # Store in cache
                    r.set('dealers_cache', json.dumps(dealers_data))
                    
                    dealers_data['cached'] = False
                    dealers_data['message'] = 'Stored in cache'
                    self.send_json_response(dealers_data)
                    
            except ImportError as e:
                self.send_json_response({
                    'error': 'upstash_redis not installed',
                    'details': str(e)
                }, status=500)
            
        except Exception as e:
            self.send_json_response({
                'error': str(e),
                'type': type(e).__name__
            }, status=500)
        
        return
    
    def fetch_from_odoo(self):
        url = 'https://mid-city-engineering.odoo.com/'
        db = 'mid-city-engineering'
        username = os.environ.get('ODOO_USERNAME')
        api_key = os.environ.get('ODOO_API_KEY')
        
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, api_key, {})
        
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
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
