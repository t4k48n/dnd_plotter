import urllib
import io
import http.server
import csv
import numpy as np
import cgi
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

def compile_template(fpath: str, **kwargs) -> str:
    pre_text = ''
    with open(fpath, 'r') as template_file:
        pre_text = template_file.read()
    for key in kwargs:
        pre_text = pre_text.replace('{{{{ {} }}}}'.format(key), kwargs[key])
    return pre_text

class Handler(http.server.BaseHTTPRequestHandler):
    def __response_template(self, svg_string: str):
        with # デフォルトsvgの挿入
        response = compile_template('template.html', encoded_svg=urllib.parse.quote(svg_string), svg=svg_string, form_action='/').encode()
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Content-length', len(response))
        self.end_headers()
        self.wfile.write(response)
    def do_GET(self):
        self.__response_template('')
    def do_POST(self):
        try:
            length = int(self.headers.get('Content-length'))
            data = self.rfile.read(length)
            _, pdict = cgi.parse_header(self.headers['content-type'])
            pdict['boundary'] = pdict['boundary'].encode()
            csv_bytes = cgi.parse_multipart(io.BytesIO(data), pdict)['csv-file'][0]
            svg_str = svgstr_of_csvbytes(csv_bytes)
        except:
            svg_str = ""
        self.__response_template(svg_str)

def svgstr_of_csvbytes(csv_bytes: bytes):
    csv_filelike = io.StringIO(csv_bytes.decode())
    matrix = np.loadtxt(csv_filelike, delimiter=',')
    f, a = plt.subplots()
    try:
        a.plot(matrix)
        svg_str = io.StringIO()
        f.savefig(svg_str, format='svg', facecolor='lightgrey')
    except:
        print("?")
    finally:
        plt.close(f)
    return svg_str.getvalue()

with http.server.HTTPServer(('', 12345), Handler) as httpd:
    httpd.serve_forever()
