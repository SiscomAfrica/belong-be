from __future__ import annotations

from django.http import HttpResponse

REDOC_HTML = """<!DOCTYPE html>
<html><head>
<title>Belong API — ReDoc</title>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Inter&display=swap"
      rel="stylesheet">
<style>body{margin:0;padding:0;}</style>
</head><body>
<redoc spec-url="/api/openapi.json"></redoc>
<script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js">
</script>
</body></html>"""


def redoc_view(request):  # noqa: ANN001, ANN201
    return HttpResponse(REDOC_HTML, content_type="text/html")
