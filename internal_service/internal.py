from settings import *
from aiohttp import web


API_KEYS = [hashlib.md5(random.randbytes(i*10)).hexdigest() for i in range(20)]
API_KEYS[11] = hashlib.md5(app.flag_ssrf.encode('utf-8')).hexdigest()
API_KEYS_VALUES = {}
for key in API_KEYS:
    if key == hashlib.md5(app.flag_ssrf.encode('utf-8')).hexdigest():
        API_KEYS_VALUES[key] = app.flag_ssrf
    else:
        API_KEYS_VALUES[key] = hashlib.sha256(key.encode('utf-8')).hexdigest()


async def index(req: web.BaseRequest):
    parameters = req.query
    msg = {}
    if 'help' in list(parameters.keys()):
        msg['msg'] = ('You can get the list of API keys (list), add new keys (add) and remove old keys (remove).'
                      'Also you can get content by API key (keycontent).')
        return web.json_response(msg)
    if 'list' in list(parameters.keys()):
        msg['Keys'] = [{i: value} for i, value in enumerate(API_KEYS)]
        return web.json_response(msg)
    if 'add' in list(parameters.keys()) or 'remove' in list(parameters.keys()):
        msg['msg'] = 'Need the master token for this operation!'
        return web.json_response(msg)
    if 'keycontent' in list(parameters.keys()):
        if parameters.get('keycontent') not in API_KEYS:
            msg['msg'] = "Bad key!"
            return web.json_response(msg)
        else:
            msg['content'] = API_KEYS_VALUES[parameters.get('keycontent')]
            return web.json_response(msg)
    msg['msg'] = "Missing parameters!"
    return web.json_response(msg)


app = web.Application()
app.add_routes([web.get('/', index)])

web.run_app(app, host="localhost", port=9090)
