__author__ = 'Y8186314'
"""
Header model run before each controller access for the application.
Initialises common elements for use.
"""

# HTML elements dictionary. Used for holding all elements to display on a page
elements = dict()

# Define constants for bootable statuses
NOT_AVAILABLE = 'NOT_AVAILABLE'
OPEN_FOR_PLEDGES = 'OPEN_FOR_PLEDGES'
CLOSED_FUNDED = 'CLOSED_FUNDED'
CLOSED_NOT_FUNDED = 'CLOSED_NOT_FUNDED'

# Set user controls area depending on whether they're logged in
# If logged in show access to user specific functions
if ('curr_user_id' in request.cookies) ^ ('curr_user_id' in response.cookies):
    username = db.users(request.cookies['curr_user_id'].value).username
    user_controls = DIV('Welcome ' + username,
                        A('Logout', callback=URL('logout'), _class='button'))

# Initial login / register controls
else:
    login_user = INPUT(_id='login_username', _placeholder='Username')
    login_pwd = INPUT(_id='login_password', _type='password', _placeholder='password')
    user_controls = DIV(login_user, login_pwd,
                        A('Login', _id='login_button', _class='button'),
                        A('Register', callback=URL('signup')))

elements['user_controls'] = user_controls

# Initialise search box functionality
search = DIV(INPUT(_id='search', _placeholder='Search for bootables. Try adding @category to refine your search!'),
             A('Search', _id='search_button', _class='button'))
elements['search'] = search
