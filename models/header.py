__author__ = 'Y8186314'
"""
Header model run before each controller access for the application.
Initialises common elements for use.
"""

# Define constants for bootable statuses
NOT_AVAILABLE = 'NOT_AVAILABLE'
OPEN_FOR_PLEDGES = 'OPEN_FOR_PLEDGES'
CLOSED_FUNDED = 'CLOSED_FUNDED'
CLOSED_NOT_FUNDED = 'CLOSED_NOT_FUNDED'

# Set user controls area depending on whether they're logged in
# If logged in show access to user specific functions
if ('curr_user_id' in request.cookies) ^ ('curr_user_id' in response.cookies):
    username = db.users(request.cookies['curr_user_id'].value).username
    user_controls = DIV(SPAN('Welcome ', A(username, callback=URL('profile', 'view')), _class='user_control'),
                        A('Logout', callback=URL('default', 'logout'), _class='button'),
                        A('Your Dashboard', callback=URL('profile', 'dashboard'), _class='user_control'),
                        A('Bootable++', callback=URL('boot', 'new'), _class='user_control'),
                        _id='user_controls')

# Initial login / register controls
else:
    login_user = INPUT(_id='login_username', _placeholder='Username', _class='user_control')
    login_pwd = INPUT(_id='login_password', _type='password', _placeholder='password', _class='user_control')
    user_controls = DIV(login_user, login_pwd,
                        A('Login', _id='login_button', _class='button'),
                        A('Register', callback=URL('profile', 'signup'), _class='user_control'),
                        _id='user_controls')

# Initialise search box functionality
search = DIV(INPUT(_id='search_box', _placeholder='Try adding an @category to refine your search!'),
             A('Search', _id='search_button', _class='button'), _id='search')
