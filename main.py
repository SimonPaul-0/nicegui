#!/usr/bin/env python3
import os
from pathlib import Path

from fastapi import Request
from starlette.middleware.sessions import SessionMiddleware

import prometheus
from nicegui import app, ui
from website import anti_scroll_hack, documentation, fly, main_page, svg

# Start Prometheus monitoring for the app
prometheus.start_monitor(app)

# Session middleware is required for demo in documentation and Prometheus
app.add_middleware(SessionMiddleware, secret_key=os.environ.get('NICEGUI_SECRET_KEY', ''))

# Setup for fly.io features
on_fly = fly.setup()

# Setup for preventing scrolling issues
anti_scroll_hack.setup()

# Static file configurations
app.add_static_files('/favicon', str(Path(__file__).parent / 'website' / 'favicon'))
app.add_static_files('/fonts', str(Path(__file__).parent / 'website' / 'fonts'))
app.add_static_files('/static', str(Path(__file__).parent / 'website' / 'static'))
app.add_static_file(local_file=svg.PATH / 'logo.png', url_path='/logo.png')
app.add_static_file(local_file=svg.PATH / 'logo_square.png', url_path='/logo_square.png')

# Build search index for documentation
documentation.build_search_index()


# API endpoint for handling dark mode settings
@app.post('/dark_mode')
async def _post_dark_mode(request: Request) -> None:
    app.storage.browser['dark_mode'] = (await request.json()).get('value')


# Define the main page
@ui.page('/')
def _main_page() -> None:
    main_page.create()


# Define the documentation main page
@ui.page('/documentation')
def _documentation_page() -> None:
    documentation.render_page(documentation.registry[''], with_menu=False)


# Define the documentation detail page
@ui.page('/documentation/{name}')
def _documentation_detail_page(name: str) -> None:
    documentation.render_page(documentation.registry[name])


# Health check endpoint
@app.get('/status')
def _status():
    return 'Ok'


# Run the UI application
# NOTE: do not reload on fly.io (see https://github.com/zauberzeug/nicegui/discussions/1720#discussioncomment-7288741)
ui.run(uvicorn_reload_includes='*.py, *.css, *.html', reload=not on_fly, reconnect_timeout=10.0)
