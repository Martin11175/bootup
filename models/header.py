__author__ = 'Y8186314'
"""
Header model run before each controller access for the application.
Initialises common elements for use.
"""

# HTML elements dictionary. Used for holding all elements to display on a page
elements = dict()

# Set user controls area depending on whether they're logged in
# If logged in show access to user specific functions
if ('curr_user_id' in request.cookies) ^ ('curr_user_id' in response.cookies):
    username = db.users(request.cookies['curr_user_id'].value).username
    logout = FORM(INPUT(_type='submit', _value='Log out'))
    user_controls = DIV('Welcome ' + username, logout)

# If the last attempt failed, keep the previous username attempt and highlight red
elif response.prev_login:
    user_controls = FORM(INPUT(_name='login_username', _placeholder='Username', _value=response.prev_login,
                               _style='color:red;'),
                         INPUT(_name='login_password', _type='password', _placeholder='password',
                               _style='color:red;'),
                         INPUT(_type='submit', _value='Login'))
    user_controls.add_button('Register', URL('signup'))
    logout = None

# Initial login / register controls
else:
    user_controls = FORM(INPUT(_name='login_username', _placeholder='Username'),
                         INPUT(_name='login_password', _type='password', _placeholder='password'),
                         INPUT(_type='submit', _value='Login'))
    user_controls.add_button('Register', URL('signup'))
    logout = None

elements['user_controls'] = user_controls

# Process login and logout from any page
if (type(user_controls) is FORM) and user_controls.accepts(request, session):
    login = db.users(username=request.vars.login_username)

    if (login is not None) and request.vars.login_password == login.pwd:
        response.cookies['curr_user_id'] = login.id
        response.cookies['curr_user_id']['expires'] = 24 * 3600
        response.cookies['curr_user_id']['path'] = '/'
        redirect(URL())
    else:
        response.prev_login = request.vars.login_username
        redirect(URL())
elif (type(logout) is FORM) and logout.accepts(request, session):
    response.cookies['curr_user_id'] = -1
    response.cookies['curr_user_id']['expires'] = -10
    response.cookies['curr_user_id']['path'] = '/'
    redirect(URL())

# Initialise search box functionality
search = FORM()
elements['search'] = search
