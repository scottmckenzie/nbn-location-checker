import azure.functions as func
import mimetypes
import re


def get_html_file(filename: str) -> str:
    with open(filename) as f:
        html = f.read()
    return html

def http_response(status_code: int, message: str = None):
    filename = f'{status_code}.html'
    if status_code == 200:
        filename = f'index.html'
    body = get_html_file(filename)
    if message:
        body = body.format(message)
    mimetype = mimetypes.types_map['.html']
    return func.HttpResponse(body, status_code=status_code, mimetype=mimetype)

def valid_email(email: str) -> bool:
    pattern = '([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'
    if re.fullmatch(pattern, email):
        return True
    return False
