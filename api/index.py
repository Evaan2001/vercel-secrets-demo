from http.server import BaseHTTPRequestHandler
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '':
            # Get all environment variables
            all_env_vars = dict(os.environ)
            
            # Filter to show only custom secrets
            secret_prefixes = ('TEST_', 'DEMO_', 'API_', 'SECRET_', 'ODOO_')
            custom_secrets = {
                key: value for key, value in all_env_vars.items()
                if key.startswith(secret_prefixes)
            }
            
            # Create HTML response
            secret_items_html = ''
            if custom_secrets:
                for key, value in custom_secrets.items():
                    secret_items_html += f'''
                    <div class="secret-item">
                        <div class="key">{key}</div>
                        <div class="value">{value if value else '<empty>'}</div>
                    </div>
                    '''
            else:
                secret_items_html = '<p class="empty">No custom secrets found. Add some in Vercel!</p>'
            
            html = f'''
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Vercel Secrets - Python</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            max-width: 800px;
                            margin: 50px auto;
                            padding: 20px;
                        }}
                        h1 {{ color: #0070f3; }}
                        .secret-item {{
                            background: #f5f5f5;
                            padding: 10px;
                            margin: 10px 0;
                            border-radius: 5px;
                            border-left: 4px solid #0070f3;
                        }}
                        .key {{ font-weight: bold; color: #333; }}
                        .value {{ color: #666; font-family: monospace; }}
                        .empty {{ color: #999; font-style: italic; }}
                    </style>
                </head>
                <body>
                    <h1>🔐 Vercel Secrets Demo</h1>
                    <p>Python serverless function displaying environment variables</p>
                    
                    <h2>Available Secrets:</h2>
                    {secret_items_html}
                    
                    <hr style="margin: 30px 0;">
                    <p><small>Total env vars: {len(all_env_vars)}</small></p>
                </body>
            </html>
            '''
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')
        
        return