from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import urllib.parse
import logging
import html

# --- CYBERPUNK THEMED HTML CONTENT ---
# We store the entire interface in a string for simplicity.
CYBERPUNK_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CYBERNETIC DATA RETRIEVER - SYNAPSE SYSTEMS</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <style>
        :root {
            --neon-green: #00ff00;
            --neon-blue: #00ffff;
            --dark-bg: #1a1a2e;
            --medium-bg: #2b2b45;
            --light-text: #e0e0e0;
            --faded-text: #999999;
            --border-color: #006666;
            --error-red: #ff3333;
        }

        body {
            font-family: 'Share Tech Mono', monospace;
            background-color: var(--dark-bg);
            color: var(--light-text);
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
            overflow-x: hidden;
            background-image: 
                radial-gradient(circle at top left, rgba(0,255,255,0.15) 0%, transparent 40%),
                radial-gradient(circle at bottom right, rgba(0,255,0,0.15) 0%, transparent 40%);
        }

        .container {
            width: 90%;
            max-width: 900px;
            background-color: var(--medium-bg);
            border: 2px solid var(--border-color);
            box-shadow: 0 0 15px var(--neon-blue), 0 0 25px var(--neon-green) inset;
            padding: 30px;
            border-radius: 8px;
            animation: flicker-border 3s infinite alternate;
        }

        @keyframes flicker-border {
            0%, 100% { border-color: var(--border-color); box-shadow: 0 0 15px var(--neon-blue), 0 0 25px var(--neon-green) inset; }
            50% { border-color: var(--neon-green); box-shadow: 0 0 20px var(--neon-green), 0 0 30px var(--neon-blue) inset; }
        }

        h1, h2 {
            font-family: 'Orbitron', sans-serif;
            color: var(--neon-green);
            text-align: center;
            text-shadow: 0 0 8px var(--neon-blue);
            margin-bottom: 20px;
            letter-spacing: 2px;
        }

        h1 {
            font-size: 2.5em;
            color: var(--neon-blue);
        }

        .section-title {
            color: var(--neon-green);
            text-shadow: 0 0 5px rgba(0,255,0,0.5);
            margin-top: 30px;
            margin-bottom: 15px;
            border-bottom: 1px dashed var(--faded-text);
            padding-bottom: 5px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: var(--neon-green);
            font-size: 0.9em;
        }

        input[type="text"] {
            width: calc(100% - 20px);
            padding: 12px;
            margin-bottom: 20px;
            background-color: #3a3a5a;
            border: 1px solid var(--neon-blue);
            color: var(--neon-green);
            font-family: 'Share Tech Mono', monospace;
            font-size: 1em;
            border-radius: 4px;
            box-shadow: 0 0 5px rgba(0,255,255,0.3);
            outline: none;
            transition: border-color 0.3s, box-shadow 0.3s;
        }

        input[type="text"]:focus {
            border-color: var(--neon-green);
            box-shadow: 0 0 8px rgba(0,255,0,0.5);
        }

        button {
            display: block;
            width: 100%;
            padding: 15px;
            background-color: var(--neon-green);
            color: var(--dark-bg);
            border: none;
            border-radius: 4px;
            font-family: 'Orbitron', sans-serif;
            font-size: 1.1em;
            cursor: pointer;
            transition: background-color 0.3s, transform 0.2s, box-shadow 0.3s;
            text-shadow: 0 0 3px var(--dark-bg);
            box-shadow: 0 0 10px var(--neon-green);
        }

        button:hover {
            background-color: var(--neon-blue);
            transform: translateY(-2px);
            box-shadow: 0 0 15px var(--neon-blue);
        }

        #result-area {
            background-color: #11111b;
            border: 1px dashed var(--neon-blue);
            padding: 15px;
            margin-top: 30px;
            max-height: 400px;
            overflow-y: auto;
            border-radius: 4px;
            font-size: 0.9em;
            color: var(--light-text);
            box-shadow: 0 0 7px rgba(0,255,255,0.4);
            white-space: pre-wrap; /* Preserve formatting of fetched content */
        }

        .output-line {
            color: var(--neon-green);
        }
        
        .alert-error {
            color: var(--error-red);
            font-weight: bold;
            margin-top: 10px;
            text-shadow: 0 0 5px var(--error-red);
        }
        
        .disclaimer {
            font-size: 0.8em;
            color: var(--faded-text);
            margin-top: 40px;
            text-align: center;
            border-top: 1px dotted var(--faded-text);
            padding-top: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Beast - The Secret</h1>
        <p class="section-title">// RESOURCE FETCH INTERFACE</p>

        <form id="fetchForm">
            <label for="urlInput">TARGET URL:</label>
            <input type="text" id="urlInput" name="url" placeholder="Enter URL (e.g., http://example.com or http://127.0.0.1:8000)" required>
            <button type="submit">INITIATE DATA RETRIEVAL // SEND REQUEST</button>
        </form>

        <p class="section-title">// RETRIEVED DATA LOG</p>
        <div id="result-area">
            %RESULT_CONTENT%
        </div>

        <div class="disclaimer">
            <p>WARNING: Unauthorized access to internal network resources is prohibited.</p>
            <p>SSRF Lab: This vulnerable server will fetch any URL provided via the 'url' parameter.</p>
        </div>
    </div>

    <script>
        // The form action will now simply reload the page with the URL parameter
        document.getElementById('fetchForm').addEventListener('submit', function(event) {
            event.preventDefault(); 
            const url = document.getElementById('urlInput').value;
            // Redirect the browser to the vulnerable server with the 'url' parameter
            window.location.href = window.location.origin + window.location.pathname + '?url=' + encodeURIComponent(url);
        });
        
        // Populate the input field with the current URL parameter on page load
        const urlParams = new URLSearchParams(window.location.search);
        const currentUrl = urlParams.get('url');
        if (currentUrl) {
            document.getElementById('urlInput').value = currentUrl;
        }
    </script>
</body>
</html>
"""

class VulnerableApp(BaseHTTPRequestHandler):
    """A simple HTTP server with an intentional SSRF vulnerability."""
    
    def _set_response(self, code=200, content_type='text/html'):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        query_string = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query_string)
        
        target_url = params.get('url', [''])[0]
        
        # --- Handle SSRF Request ---
        if target_url:
            logging.info(f"Attempting to fetch URL: {target_url}")
            
            result_content = self._fetch_url(target_url)
        else:
            # Initial load without any URL parameter
            result_content = '<p class="output-line">// Awaiting command. Enter a URL above and submit.</p>'
            
        # Insert the dynamic result content into the static HTML template
        final_html = CYBERPUNK_HTML.replace("%RESULT_CONTENT%", result_content)
        
        self._set_response(200, 'text/html')
        self.wfile.write(final_html.encode('utf-8'))
        
    def _fetch_url(self, target_url):
        """Core vulnerable function that makes the server-side request."""
        
        output_lines = [
            f'<p class="output-line">> // Server attempting connection to: {html.escape(target_url)}</p>',
            '<p class="output-line">-----------------------------------------------</p>'
        ]
        
        try:
            # VULNERABILITY: No input validation or restriction on the target URL.
            response = requests.get(target_url, timeout=10)
            
            # --- Success Output ---
            output_lines.append(f'<p class="output-line">// Connection successful. Status: {response.status_code}</p>')
            output_lines.append(f'<p class="output-line">// Content Type: {response.headers.get("Content-Type", "text/plain")}</p>')
            output_lines.append('<p class="output-line">// Data stream incoming:</p>')
            
            # Use html.escape() to safely display the fetched content inside the HTML
            content_display = html.escape(response.text[:2000]) # Truncate for display
            output_lines.append(f'<pre>{content_display}</pre>')
            
            output_lines.append('<p class="output-line">-----------------------------------------------</p>')
            output_lines.append('<p class="output-line">// Data retrieval complete.</p>')

        except requests.exceptions.ConnectionError as e:
            # --- Connection Refused/Error Output ---
            output_lines.append(f'<p class="output-line alert-error">!!! ERROR: Connection Refused or Host Unreachable !!!</p>')
            output_lines.append(f'<p class="output-line">// Target system unresponsive or access denied. Details: {html.escape(str(e))}</p>')

        except requests.exceptions.RequestException as e:
            # --- General Request Error Output ---
            output_lines.append(f'<p class="output-line alert-error">!!! WARNING: Request Error Occurred !!!</p>')
            output_lines.append(f'<p class="output-line">// Failed to fetch URL. Details: {html.escape(str(e))}</p>')
            
        return "\n".join(output_lines)


def run(server_class=HTTPServer, handler_class=VulnerableApp, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('127.0.0.1', port)
    httpd = server_class(server_address, handler_class)
    logging.info(f'Starting VULNERABLE SSRF app on http://127.0.0.1:{port}...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping vulnerable app.\n')

if __name__ == '__main__':
    run(port=8080)
