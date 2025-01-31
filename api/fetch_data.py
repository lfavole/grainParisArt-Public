import os
import sys
import traceback
from http.server import BaseHTTPRequestHandler
from pathlib import Path

import django

sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "grainparisart.settings")
django.setup()

from cinemas.management.commands.fetch_data import Command as FetchData


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if os.environ.get("CRON_SECRET") and self.headers.get("Authorization", "") != f"Bearer {os.environ.get('CRON_SECRET', '')}":
            self.send_response(401)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b'Unauthorized')
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()

        _stdout_write = sys.stdout.write
        _stderr_write = sys.stderr.write

        def write(text):
            self.wfile.write(text.encode("utf-8"))
        sys.stdout.write = sys.stderr.write = write

        try:
            FetchData().handle()
        except:
            traceback.print_exc(file=sys.stderr)
            return
        finally:
            sys.stdout.write = _stdout_write
            sys.stderr.write = _stderr_write

        self.wfile.write(b'OK')
