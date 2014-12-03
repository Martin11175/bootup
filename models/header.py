__author__ = 'Y8186314'
from gluon.storage import Storage
"""
Header model run before each controller access for the application.
Initialises common elements and functions for use.
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


def get_status_display_string(status):
    """
    Function for translating data model status strings to text for users

    :param status: The data model status string to translate
    :return: Returns a representative user facing formatted string
    """
    if status == NOT_AVAILABLE:
        return "Not Available to Public"
    elif status == OPEN_FOR_PLEDGES:
        return "Open for pledges!"
    elif status == CLOSED_FUNDED or status == CLOSED_NOT_FUNDED:
        return "Closed."

    return ''


def extract_bootable_short_form(bootable):
    """
    Common function for extracting the short form bootable information for display in subviews/boot.html.

    :param bootable: The bootable row from the data model
    :return: Returns a Storage element containing all necessary information for a short form bootable display
    """
    result = Storage()
    result['id'] = bootable.id
    result['status'] = get_status_display_string(bootable.status)
    result['title'] = A(bootable.title, callback=URL('boot', 'view', args=bootable.id)) \
        if bootable.status != NOT_AVAILABLE else bootable.title
    result['category'] = db.categories[bootable.category_ref].name
    result['owner'] = db.users[bootable.boot_manager].username
    result['intro'] = bootable.intro
    result['goal'] = bootable.goal
    value_sum = db.pledges.value.sum()
    result['total'] = db((db.pledges.boot_ref == bootable.id)
                         & (db.pledged.pledge_ref == db.pledges.id)).select(value_sum).first()[value_sum]
    return result
