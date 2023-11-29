from sanic import Sanic
from sanic.response import json
from sanic_mako import SanicMako,render_template,render_template_def

app = Sanic('nnq')

mako = SanicMako(app)


# or setup later
# mako = SanicMako()
# mako.init_app(app)

@app.route('/index')
@mako.template('index.html')  # decorator method is staticmethod
async def index(request):
    return {'name': 'Hello, sanic!'}


@app.route('/login', methods=['GET', 'POST'])
async def login(request):
    error = None
    return await render_template('admin/login_user.html', request,
                                 {'error': error})


@app.route('/post/<post_id>/react', methods=['POST', 'DELETE'])
async def react(request, post_id):
    # ...
    return json({'r': 0, 'html': await render_template_def(
        'utils.html', 'render_react_container', request,
        {'reaction_type': 1})})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)