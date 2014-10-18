import os
import urllib.request
import urllib.error

from bottle import route, run, request, response, HTTPError, default_app


proxyconf = dict(
    api_protocal='https',
    api_host='www.google.com',
    api_port='80',
    localhost=os.environ.get('OPENSHIFT_APP_DNS', 'localhost:8088'),
    localport=os.environ.get('OPENSHIFT_PYTHON_PORT', '8088'),
)

_api_burl = proxyconf['api_host'].encode()
_loc_burl = proxyconf['localhost'].encode()

_hoppish = {
    'connection':1, 'keep-alive':1, 'proxy-authenticate':1,
    'proxy-authorization':1, 'te':1, 'trailers':1, 'transfer-encoding':1,
    'upgrade':1
}.__contains__


@route('/<uri:re:.*>')
@route('/<uri:re:.*>', method='POST')
def proxy(uri=''):
    # port suffix
    if len(uri) > 0:
        i = request.url.index('://')
        j = request.url[i+3:].index('/')
        uri = request.url[i+3+j:]
    port = "" if proxyconf['api_port'] == "80" else ":%s" % proxyconf['api_port']
    url = "%s://%s%s%s" % (proxyconf['api_protocal'], proxyconf['api_host'], port, uri)

    # update host to destination host
    method = request.method
    headers = dict(request.headers)
    headers["Host"] = proxyconf['api_host']
    if 'Content-Length' in headers:
        del headers['Content-Length']
    
    data = request.body.getvalue() if method == 'POST' else None
    req = urllib.request.Request(
        url=url,
        method=method,
        headers=headers,
        data=data,
        )
    
    body = b'error'
    try:
        r = urllib.request.urlopen(req)
        for k, v in r.headers.items():
            if not _hoppish(k.lower()):
                response.set_header(k, v)
                #print(k, v)
        response.status = r.getcode()
        body = r.readall()
        if len(body):
            body = body.replace(_api_burl, _loc_burl)
    except urllib.error.HTTPError as x:
        print(x)
        HTTPError(500)

    return body

application = default_app()

if __name__ == '__main__':
    run(host='localhost', port=proxyconf['localport'], debug=True)
