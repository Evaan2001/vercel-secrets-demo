# Save this file as: api/index.py
# Directory structure:
# vercel-secrets-demo/
# └── api/
#     └── index.py  <-- This file goes here

from http.server import BaseHTTPRequestHandler
import os
import xmlrpc.client
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '':
            try:
                # Get Odoo credentials from environment variables
                url = 'https://mid-city-engineering.odoo.com/'
                db = 'mid-city-engineering'
                username = os.environ.get('ODOO_USERNAME')
                api_key = os.environ.get('ODOO_API_KEY')
                
                # Check if credentials are available
                if not username or not api_key:
                    self.send_error_response('ODOO_USERNAME and ODOO_API_KEY environment variables not set')
                    return
                
                # Connect to Odoo
                common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
                uid = common.authenticate(db, username, api_key, {})
                
                if not uid:
                    self.send_error_response('Authentication failed. Check your credentials.')
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
                
                # Create HTML response
                html = self.create_html_response(uid, dealers)
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(html.encode())
                
            except Exception as e:
                self.send_error_response(f'Error: {str(e)}')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')
        
        return
    
    def send_error_response(self, error_message):
        html = f'''
        <!DOCTYPE html>
        <html>
            <head>
                <title>Odoo API Error</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        max-width: 800px;
                        margin: 50px auto;
                        padding: 20px;
                    }}
                    .error {{
                        background: #fee;
                        border-left: 4px solid #f00;
                        padding: 15px;
                        border-radius: 5px;
                    }}
                </style>
            </head>
            <body>
                <h1>🔐 Odoo API Demo</h1>
                <div class="error">
                    <strong>Error:</strong> {error_message}
                </div>
            </body>
        </html>
        '''
        self.send_response(500)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def create_html_response(self, uid, dealers):
        # Create dealer cards HTML
        dealer_cards = ''
        for dealer in dealers:
            state = dealer.get('state_id')[1] if dealer.get('state_id') else 'N/A'
            country = dealer.get('country_id')[1] if dealer.get('country_id') else 'N/A'
            
            dealer_cards += f'''
            <div class="dealer-card">
                <h3>{dealer.get('name', 'N/A')}</h3>
                <div class="dealer-info">
                    <p><strong>Address:</strong> {dealer.get('street', '')} {dealer.get('street2', '')}</p>
                    <p><strong>City:</strong> {dealer.get('city', 'N/A')}, {state} {dealer.get('zip', '')}</p>
                    <p><strong>Country:</strong> {country}</p>
                    <p><strong>Phone:</strong> {dealer.get('phone', 'N/A')}</p>
                    <p><strong>Email:</strong> {dealer.get('email', 'N/A')}</p>
                    <p><strong>Coordinates:</strong> 
                        Lat: {dealer.get('partner_latitude') or dealer.get('x_latitude', 'N/A')}, 
                        Lng: {dealer.get('partner_longitude') or dealer.get('x_longitude', 'N/A')}
                    </p>
                </div>
            </div>
            '''
        
        html = f'''
        <!DOCTYPE html>
        <html>
            <head>
                <title>Odoo Dealers - Vercel Demo</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        max-width: 1000px;
                        margin: 50px auto;
                        padding: 20px;
                        background: #f9f9f9;
                    }}
                    h1 {{ color: #0070f3; }}
                    .success {{
                        background: #d4edda;
                        border-left: 4px solid #28a745;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    .dealer-card {{
                        background: white;
                        padding: 20px;
                        margin: 15px 0;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        border-left: 4px solid #0070f3;
                    }}
                    .dealer-card h3 {{
                        margin-top: 0;
                        color: #333;
                    }}
                    .dealer-info p {{
                        margin: 8px 0;
                        color: #666;
                    }}
                    .stats {{
                        background: #e3f2fd;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <h1>Odoo API Demo - Dealers List</h1>
                
                <div class="success">
                    Connected successfully to Odoo!
                </div>

                <div class="stats">
                    User ID: {uid}
                </div>
                
                <div class="stats">
                    <strong>Number of dealers found:</strong> {len(dealers)}
                </div>
            </body>
        </html>
        '''
        return html
