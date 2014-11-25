__author__ = 'Y8186314'
from datetime import date
from applications.BootUp.modules.header import *

def index():
    """
    5 most recently created projects (by ID)
    5 projects closest to their goal (heavy calculation to sum all pledges, consider revising.)
    """
    objects = init_header()

    # Get the 5 newest (by incremental ID) available projects
    visible = db(db.bootables.status != 'NOT_AVAILABLE')
    newest = visible.select(limitby=((visible.count() - 5), visible.count()))

    # Calculate distance to pledge goal for all open bootables and select top 5
    totals = db.pledges.value.sum()
    closest = db((db.bootables.status == 'OPEN_FOR_PLEDGES')
                 & (db.bootables.id == db.pledges.boot_ref)
                 & (db.pledges.id == db.pledged.pledge_ref))\
        .select(totals, groupby=db.bootables.id, orderby=~totals)

    objects['pledged'] = closest

    return objects


def signup():
    """
    Form for creating a new user. Requires:
    UID, name, dob, complete address (street addr, city, country, post),
            credit card (ID, expiry, PIN, address)
    """
    init_header()

    # Break the form down into chunks to reduce visual load, don't start personal info until after username
    if (request.args(0) == '1') and 'username' in session.signup:
        session.current_page = 1
        form = FORM(H3('Just a little more!'),
                    H4('Awesome! We\'re gonna need some personal details to get you booting.'),
                    DIV(LABEL('First Name', _for='firstname'),
                        INPUT(_name='firstname', requires=IS_NOT_EMPTY(),
                              _value=session.signup['firstname'] if 'firstname' in session.signup else '')),
                    DIV(LABEL('Last Name', _for='lastname'),
                        INPUT(_name='lastname', requires=IS_NOT_EMPTY(),
                              _value=session.signup['lastname'] if 'lastname' in session.signup else '')),
                    DIV(LABEL('Date of Birth', _for='dob'),
                        INPUT(_name='dob', _type='date',
                              requires=IS_DATE_IN_RANGE(maximum=date.today()),
                              _value=session.signup['dob'] if 'dob' in session.signup else '')),
                    DIV(H4('Address'),
                        DIV(LABEL('House Name / Number', _for='house'),
                            INPUT(_name='house', requires=IS_NOT_EMPTY(),
                                  _value=session.signup['address.house'] if 'address.house' in session.signup else '')),
                        DIV(LABEL('Road name', _for='street'),
                            INPUT(_name='street', requires=IS_NOT_EMPTY(),
                                  _value=session.signup['address.street'] if 'address.street' in session.signup else '')),
                        DIV(LABEL('City', _for='city'),
                            INPUT(_name='city', requires=IS_NOT_EMPTY(),
                                  _value=session.signup['address.city'] if 'address.city' in session.signup else '')),
                        DIV(LABEL('Country', _for='country'),
                            INPUT(_name='country', requires=IS_NOT_EMPTY(),
                        _value=session.signup['address.country'] if 'address.country' in session.signup else '')),
                        DIV(LABEL('Post Code', _for='postcode'),
                            INPUT(_name='postcode', requires=IS_MATCH('^\w{4} \w{3}$'),
                                  _value=session.signup['address.postcode'] if 'address.postcode' in session.signup else ''))),
                    DIV(INPUT(_type='submit', _value='Next')))\
                    .add_button('Prev', URL('signup', args=(session.current_page - 1)))

    # Finish up with credit information if personal details are complete
    elif (request.args(0) == '2') and 'address.postcode' in session.signup:
        session.current_page = 2
        form = FORM(H3('One. Last. Step.'),
                    H4('Finally some credit information for the bootables you love.'),
                    DIV(LABEL('Card Number', _for='card_num'),
                        INPUT(_name='card_num', _type='number', requires=IS_MATCH('^\d{12}$'))),
                    DIV(LABEL('Card Expiry Date', _for='expiry'),
                        INPUT(_name='expiry', _type='month', requires=IS_DATE_IN_RANGE(format='%Y-%m',
                                                                                       minimum=date.today()))),
                    DIV(LABEL('Security PIN', _for='pin'),
                        INPUT(_name='pin', _type='number', _min='000', _max='999', requires=IS_MATCH('^\d{3}$'))),
                    DIV(H4('Billing Address'),
                        DIV(LABEL('Use same as previous address?', _for='use_prev'),
                            INPUT(_name='use_prev', _type='checkbox', _checked='true')),
                        DIV(LABEL('House Name / Number', _for='bill_house'),
                            INPUT(_name='bill_house', requires=IS_NOT_EMPTY(),
                                  _value=session.signup['address.house'], _readonly='true')),
                        DIV(LABEL('Road name', _for='bill_street'),
                            INPUT(_name='bill_street', requires=IS_NOT_EMPTY(),
                                  _value=session.signup['address.street'], _readonly='true')),
                        DIV(LABEL('City', _for='bill_city'),
                            INPUT(_name='bill_city', requires=IS_NOT_EMPTY(),
                                  _value=session.signup['address.city'], _readonly='true')),
                        DIV(LABEL('Country', _for='bill_country'),
                            INPUT(_name='bill_country', requires=IS_NOT_EMPTY(),
                                  _value=session.signup['address.country'], _readonly='true')),
                        DIV(LABEL('Post Code', _for='bill_postcode'),
                            INPUT(_name='bill_postcode', requires=IS_MATCH('^\w{4} \w{3}$'),
                                  _value=session.signup['address.postcode'], _readonly='true'))),
                    DIV(INPUT(_type='submit', _value='Submit')))\
                    .add_button('Prev', URL('signup', args=(session.current_page - 1)))

    # If the page hasn't been accessed in this session, start afresh
    else:
        session.current_page = 0
        form = FORM(H3('Welcome to the BootUp community!'),
                    H4('Help us get you started by choosing your community name.'),
                    DIV(LABEL('Username', _for='username'),
                        INPUT(_name='username', requires=IS_NOT_IN_DB(db, 'users.username'),
                              _value=session.signup['username'] if 'username' in session.signup else '')),
                    DIV(LABEL('Password', _for='password'),
                        INPUT(_name='password', _type='password', requires=IS_NOT_EMPTY(),
                              _value=session.signup['password'] if 'password' in session.signup else '')),
                    DIV(LABEL('Confirm Password', _for='confirm_pwd'),
                        INPUT(_name='confirm_pwd', _type='password', requires=IS_EQUAL_TO(request.vars.password),
                              _value=session.signup['password'] if 'password' in session.signup else '')),
                    DIV(INPUT(_type='submit', _value='Next')))\
                    .add_button('Cancel', URL('index'))

    # On receiving a valid form response
    if form.accepts(request, session):
        # Register details in session in case a user wishes to change them
        if session.current_page == 0:
            if not session.signup:
                session.signup = dict()
            session.signup['username'] = request.vars.username
            session.signup['password'] = request.vars.password
            redirect(URL('signup', args=(session.current_page + 1)))

        elif session.current_page == 1:
            session.signup['firstname'] = request.vars.firstname
            session.signup['lastname'] = request.vars.lastname
            session.signup['dob'] = request.vars.dob
            session.signup['address.house'] = request.vars.house
            session.signup['address.street'] = request.vars.street
            session.signup['address.city'] = request.vars.city
            session.signup['address.country'] = request.vars.country
            session.signup['address.postcode'] = request.vars.postcode
            session.current_page += 1
            redirect(URL('signup', args=(session.current_page + 1)))

        # If all forms complete, create the new user
        elif session.current_page == 2:
            address_id = db.address.insert(number=session.signup['address.house'],
                                           street=session.signup['address.street'],
                                           city=session.signup['address.city'],
                                           country=session.signup['address.country'],
                                           postcode=session.signup['address.postcode'])

            # If marked, use the same data for user address and billing address
            if request.vars.use_prev == 'true':
                credit_address_id = address_id
            else:
                credit_address_id = db.address.insert(number=request.vars.bill_house,
                                                      street=request.vars.bill_street,
                                                      city=request.vars.bill_city,
                                                      country=request.vars.bill_country,
                                                      postcode=request.vars.bill_postcode)

            credit_id = db.credit.insert(number=request.vars.card_num,
                                         expiry=request.vars.expiry,
                                         PIN=request.vars.pin,
                                         address_ref=credit_address_id)

            new_user = db.users.insert(username=session.signup['username'],
                                       pwd=session.signup['password'],
                                       firstname=session.signup['firstname'],
                                       lastname=session.signup['lastname'],
                                       dob=session.signup['dob'],
                                       address_ref=address_id,
                                       credit_ref=credit_id)
            db.commit()

            # Clear current session in case another user wants to sign up
            session.signup = dict()
            session.current_page = 0

            # Log in and return to home page
            response.cookies['curr_user_id'] = new_user
            response.cookies['curr_user_id']['expires'] = 24 * 3600
            response.cookies['curr_user_id']['path'] = '/'
            redirect(URL('index'))

    return dict(form=form)


def view_profile():
    """
    Edit any aspect of the user, addresses or credit sections
    """
    init_header()

    profile = db((db.users.address_ref == db.address.id)
                 & (db.users.credit_ref == db.credit.id)
                 & (db.credit.address_ref == db.address.id))
    return dict(profile=profile)


def new_boot():
    """
    Form for creating bootable. Must be logged in first.
    """
    init_header()

    return dict()


def boot_cupboard():
    """
    'Your dashboard'?
    Overview projects, change status, delete (if not open), go to edit
    """
    init_header()

    return dict()


def edit_boot():
    """
    Edit boots
    """
    init_header()

    return dict()


def view_boot():
    """
    Shows: status, goal, pledges available,
            current contributions (username, amount, expected reward) [group by pledge in hovering window?],
            current pledged amount, all normal bootable information.
    """
    init_header()

    return dict()
