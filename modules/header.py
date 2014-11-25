__author__ = 'Y8186314'
from gluon import *


def init_header():
    """
    Page header initialiser for dynamic functionality
    :return: Returns a dictionary of common elements for use in the website's header
    """
    if 'curr_user_id' in current.request.cookies:
        user_controls = DIV()
    else:
        user_controls = DIV(FORM(INPUT(_name='username', _placeholder='Username'),
                                 INPUT(_name='password', _type='password', _placeholder='password'),
                                 INPUT(_type='submit', _value='Login'))
                            .add_button('Register', URL('signup')))


    search = FORM()

    return dict(user_controls=user_controls, search=search)
