import azure.functions as func
import mimetypes
import re
from types import SimpleNamespace


_m = SimpleNamespace()
# from https://www.emailregex.com/
_m.pattern = re.compile('(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)')

def get_html_file(filename: str) -> str:
    with open(filename) as f:
        html = f.read()
    return html

def http_response(status_code: int, message: str = None):
    map = {200: html_200, 400: html_400, 404: html_404}
    body = map.get(status_code)
    if message:
        body = body.format(message)
    mimetype = mimetypes.types_map['.html']
    return func.HttpResponse(body, status_code=status_code, mimetype=mimetype)

def valid_email(email: str) -> bool:
    if re.fullmatch(_m.pattern, email):
        return True
    return False

html_200 = '''<!doctype html>
<html>
    <body>
        <form method="POST">
        <label for="location">NBN Location ID:</label><br>
        <input name="location" type="text" required="required" pattern="LOC\d{12}" placeholder="LOC000178376736">
        &nbsp;<a href="https://www.aussiebroadband.com.au/nbn-poi/" target="_blank">Click here</a> to get your Location ID<br>
        <label for="email">Email address:</label><br>
        <input name="email" type="email" required="required"><br><br>
        <input type="submit" value="Submit">
        </form>
    </body>
</html>'''

html_400 = '''<!doctype html>
<html>
    <body>
        <h1>400 Bad request</h1>
        {}
    </body>
</html>'''

html_404 = '''<!doctype html>
<html>
    <body>
        <h1>Not found</h1>
        {}
    </body>
</html>'''
