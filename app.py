import os
import mimetypes

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def app(environ, start_response):
    """
    WSGI Application entrypoint para o Vercel.
    Permite que o portal funcione perfeitamente tanto no runtime Python do Vercel
    quanto como site estático.
    """
    raw_path = environ.get('PATH_INFO', '/').lstrip('/')
    if not raw_path:
        raw_path = 'index.html'

    # Normalização de segurança contra directory traversal
    safe_rel = os.path.normpath(raw_path)
    if safe_rel.startswith('..') or os.path.isabs(safe_rel):
        start_response('403 Forbidden', [('Content-Type', 'text/plain')])
        return [b'Forbidden']

    target_path = os.path.join(BASE_DIR, safe_rel)

    # Se a URL não tiver extensão e for um artigo (ex: /artigos/nome-da-materia)
    if not os.path.exists(target_path) or os.path.isdir(target_path):
        if os.path.exists(target_path + '.html'):
            target_path = target_path + '.html'
        elif os.path.exists(os.path.join(target_path, 'index.html')):
            target_path = os.path.join(target_path, 'index.html')
        else:
            target_path = os.path.join(BASE_DIR, 'index.html')

    if not os.path.exists(target_path):
        start_response('404 Not Found', [('Content-Type', 'text/plain; charset=utf-8')])
        return [b'Arquivo nao encontrado']

    content_type, _ = mimetypes.guess_type(target_path)
    if not content_type:
        ext = os.path.splitext(target_path)[1].lower()
        if ext == '.mp3':
            content_type = 'audio/mpeg'
        elif ext == '.jpg' or ext == '.jpeg':
            content_type = 'image/jpeg'
        elif ext == '.png':
            content_type = 'image/png'
        elif ext == '.json':
            content_type = 'application/json'
        elif ext == '.xml':
            content_type = 'application/xml'
        else:
            content_type = 'text/html; charset=utf-8'

    headers = [
        ('Content-Type', content_type),
        ('Cache-Control', 'public, max-age=3600'),
        ('X-Content-Type-Options', 'nosniff'),
        ('X-Frame-Options', 'DENY')
    ]

    try:
        with open(target_path, 'rb') as f:
            content = f.read()
        headers.append(('Content-Length', str(len(content))))
        start_response('200 OK', headers)
        return [content]
    except Exception as e:
        start_response('500 Internal Server Error', [('Content-Type', 'text/plain; charset=utf-8')])
        return [str(e).encode('utf-8')]

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    port = int(os.environ.get('PORT', 8000))
    print(f"Servidor Ímprobo ativo em http://localhost:{port}")
    httpd = make_server('', port, app)
    httpd.serve_forever()

