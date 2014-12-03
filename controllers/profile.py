__author__ = 'Y8186314'
from gluon.storage import Storage
from datetime import date


def index():
    """ Set the default action for the controller to be viewing the currently logged in profile. """
    redirect(URL('profile', 'view'))


def signup():
    """
    Form for creating a new user. Requires:
    Username, password, name, dob, complete address (street addr, city, country, post),
            credit card (number, expiry, PIN, address)

    :arg 0 - The signup page to jump to if supplied. Only allowed if this stage has already been reached.
    :return - Returns 3 Different forms depending on the user's progress through the signup process,
              pre-populated if already completed and returned to later.
    """
    # If signed in at any point, clear session and redirect to home
    if 'curr_user_id' in request.cookies:
        session.signup = dict()
        session.flash = \
            "Looks like you're already signed in! If you wish to create another account, please sign out first."
        redirect(URL('default', 'index'))

    # Break the form down into chunks to reduce visual load, don't start personal info until after username
    if (request.args(0) == '1') and 'username' in session.signup:
        session.current_signup_page = 1
        form = FORM(H2('Just a little more!'),
                    H3('Awesome! We\'re gonna need some personal details to get you booting.'),
                    DIV(H4('About you'),
                        DIV(LABEL('First Name', _for='firstname'),
                            INPUT(_name='firstname', requires=IS_NOT_EMPTY(error_message='Please enter your first name.'),
                                  _value=session.signup['firstname'] if 'firstname' in session.signup else '')),
                        DIV(LABEL('Last Name', _for='lastname'),
                            INPUT(_name='lastname', requires=IS_NOT_EMPTY(error_message='Please enter your last name.'),
                                  _value=session.signup['lastname'] if 'lastname' in session.signup else '')),
                        DIV(LABEL('Date of Birth', _for='dob'),
                            INPUT(_name='dob', _type='date',
                                  requires=IS_DATE_IN_RANGE(maximum=date.today(),
                                                            error_message='Please enter your date of birth (cannot be after today).'),
                                  _value=session.signup['dob'] if 'dob' in session.signup else '')),
                        _class='info_div'),
                    DIV(H4('Address'),
                        DIV(LABEL('House Name / Number', _for='house'),
                            INPUT(_name='house',
                                  requires=IS_NOT_EMPTY(error_message='Please enter your house name / number.'),
                                  _value=session.signup['address.house'] if 'address.house' in session.signup else '')),
                        DIV(LABEL('Road name', _for='street'),
                            INPUT(_name='street', requires=IS_NOT_EMPTY('Please enter your road name.'),
                                  _value=session.signup['address.street'] if 'address.street' in session.signup else '')),
                        DIV(LABEL('City', _for='city'),
                            INPUT(_name='city', requires=IS_NOT_EMPTY('Please give the city location of your address.'),
                                  _value=session.signup['address.city'] if 'address.city' in session.signup else '')),
                        DIV(LABEL('Country', _for='country'),
                            INPUT(_name='country', requires=IS_NOT_EMPTY('Please enter a country.'),
                                  _value=session.signup['address.country'] if 'address.country' in session.signup else '')),
                        DIV(LABEL('Post Code', _for='postcode'),
                            INPUT(_name='postcode', requires=IS_MATCH('^\w{4} \w{3}$',
                                                                      error_message='Please enter your postcode (like "YO12 5ZB").'),
                                  _value=session.signup['address.postcode'] if 'address.postcode' in session.signup else '')),
                        _class='address_div'),
                    DIV(_class='clear'),
                    INPUT(_type='submit', _value='Next', _class='button_forward'),
                    _id='split_form')
        form.add_button('Prev', URL('profile', 'signup', args=(session.current_signup_page - 1)), _class="button_back")

    # Finish up with credit information if personal details are complete
    elif (request.args(0) == '2') and 'address.postcode' in session.signup:
        session.current_signup_page = 2
        form = FORM(H2('One. Last. Step.'),
                    H3('Finally some credit information for the bootables you love.'),
                    DIV(H4('Card details'),
                        DIV(LABEL('Card Number', _for='card_num'),
                            INPUT(_name='card_num', _type='number',
                                  requires=IS_MATCH('^\d{12}$', error_message='Please enter a 12 digit card number.'))),
                        DIV(LABEL('Card Expiry Date', _for='expiry'),
                            INPUT(_name='expiry', _type='month',
                                  requires=IS_DATE_IN_RANGE(format='%Y-%m', minimum=date.today(),
                                                            error_message='Please enter your card\'s expiry date (e.g. 2015-02).'))),
                        DIV(LABEL('Security PIN', _for='pin'),
                            INPUT(_name='pin', _type='number', _min='000', _max='999',
                                  requires=IS_MATCH('^\d{3}$',
                                                    error_message='Please enter your card\'s 3-digit security pin).'))),
                        _class='info_div'),
                    DIV(H4('Billing Address'),
                        DIV(LABEL('House Name / Number', _for='bill_house'),
                            INPUT(_name='bill_house',
                                  requires=IS_NOT_EMPTY(error_message='Please enter your billing house name / number.'),
                                  _value=session.signup['address.house'])),
                        DIV(LABEL('Road name', _for='bill_street'),
                            INPUT(_name='bill_street',
                                  requires=IS_NOT_EMPTY(error_message='Please enter your billing address road name.'),
                                  _value=session.signup['address.street'])),
                        DIV(LABEL('City', _for='bill_city'),
                            INPUT(_name='bill_city',
                                  requires=IS_NOT_EMPTY(error_message='Please enter the city of your billing address.'),
                                  _value=session.signup['address.city'])),
                        DIV(LABEL('Country', _for='bill_country'),
                            INPUT(_name='bill_country',
                                  requires=IS_NOT_EMPTY(error_message='Please enter the country of your billing address.'),
                                  _value=session.signup['address.country'])),
                        DIV(LABEL('Post Code', _for='bill_postcode'),
                            INPUT(_name='bill_postcode',
                                  requires=IS_MATCH('^\w{4} \w{3}$',
                                                    error_message='Please enter your billing post code (e.g. YO12 5QQ).'),
                                  _value=session.signup['address.postcode'])),
                        _class='address_div'),
                    DIV(_class='clear'),
                    INPUT(_type='submit', _value='Submit', _class="button_forward"),
                    _id='split_form')
        form.add_button('Prev', URL('profile', 'signup', args=(session.current_signup_page - 1)), _class="button_back")

    # If the page hasn't been accessed in this session, start afresh
    else:
        session.current_signup_page = 0
        form = FORM(H2('Welcome to the BootUp community!'),
                    H3('Help us get you started by choosing your BootUp identity:'),
                    DIV(LABEL('Username', _for='username'),
                        INPUT(_name='username',
                              requires=IS_NOT_IN_DB(db, 'users.username',
                                                    error_message='Sorry, that username\'s already taken, please choose another.'),
                              _value=session.signup['username'] if session.signup and 'username' in session.signup else '')),
                    DIV(LABEL('Password', _for='password'),
                        INPUT(_name='password', _type='password',
                              requires=IS_NOT_EMPTY(error_message='Please set yourself a password (cannot be blank).'),
                              _value=session.signup['password'] if session.signup and 'password' in session.signup else '')),
                    DIV(LABEL('Confirm Password', _for='confirm_pwd'),
                        INPUT(_name='confirm_pwd', _type='password',
                              requires=IS_EQUAL_TO(request.vars.password,
                                                   error_message='Set passwords do not match.'),
                              _value=session.signup['password'] if session.signup and 'password' in session.signup else '')),
                    INPUT(_type='submit', _value='Next', _class='button_forward'),
                    _id='user_form')
        form.add_button('Cancel', URL('default', 'index'), _class='button_back')

    # On receiving a valid form response
    if form.accepts(request, session):
        # Register details in session in case a user wishes to change them
        if session.current_signup_page == 0:
            if not session.signup:
                session.signup = dict()
            session.signup['username'] = request.vars.username
            session.signup['password'] = request.vars.password
            redirect(URL('profile', 'signup', args=(session.current_signup_page + 1)))

        elif session.current_signup_page == 1:
            session.signup['firstname'] = request.vars.firstname
            session.signup['lastname'] = request.vars.lastname
            session.signup['dob'] = request.vars.dob
            session.signup['address.house'] = request.vars.house
            session.signup['address.street'] = request.vars.street
            session.signup['address.city'] = request.vars.city
            session.signup['address.country'] = request.vars.country
            session.signup['address.postcode'] = request.vars.postcode
            redirect(URL('profile', 'signup', args=(session.current_signup_page + 1)))

        # If all forms complete, create the new user
        elif session.current_signup_page == 2:
            address_id = db.address.insert(number=session.signup['address.house'],
                                           street=session.signup['address.street'],
                                           city=session.signup['address.city'],
                                           country=session.signup['address.country'],
                                           postcode=session.signup['address.postcode'])

            # If marked, use the same data for user address and billing address
            credit_address_id = db.address.insert(number=request.vars.bill_house,
                                                  street=request.vars.bill_street,
                                                  city=request.vars.bill_city,
                                                  country=request.vars.bill_country,
                                                  postcode=request.vars.bill_postcode)
            if credit_address_id is None:
                credit_address_id = address_id

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
            session.flash = "Congratulations " + session.signup['username'] + "! Welcome to the community."
            session.signup = dict()
            del session.signup
            del session.current_signup_page

            # Log in and return to home page
            response.cookies['curr_user_id'] = new_user
            response.cookies['curr_user_id']['expires'] = 24 * 3600
            response.cookies['curr_user_id']['path'] = '/'
            redirect(URL('default', 'index'))

    response.files.insert(2, URL('static', 'css/signup.css'))
    return dict(form=form)


def view():
    """
    View and edit any aspect of the user, addresses or credit sections. Also displays pledge history.

    :return - Returns a form complete with all of the users information for editing and a list of bootables
              for display in short form with the user's pledged amount.
    """
    # Only allow if user logged in
    if not 'curr_user_id' in request.cookies:
        session.flash = "Sorry, you need to be signed in to see your bootables!"
        redirect(URL('default', 'index'))

    # Fetch the currently logged in user's details
    db_profile = db.users[request.cookies['curr_user_id'].value]
    db_address = db.address[db_profile.address_ref]
    db_credit = db.credit[db_profile.credit_ref]
    db_credit_address = db.address[db_credit.address_ref]

    # Create a form of all of the user's info for updating as needed
    form = FORM(H3('Login info'),
                DIV(LABEL('Username', _for='username'),
                    INPUT(_name='username', requires=IS_NOT_IN_DB(db, 'users.username',
                                                                  allowed_override=db_profile.username),
                          _value=db_profile.username)),
                DIV(LABEL('Password', _for='password'),
                    INPUT(_name='password', _type='password', requires=IS_NOT_EMPTY(),
                          _value=db_profile.pwd)),
                DIV(LABEL('Confirm Password', _for='confirm_pwd'),
                    INPUT(_name='confirm_pwd', _type='password', requires=IS_EQUAL_TO(request.vars.password),
                          _value=db_profile.pwd)),
                H3('Personal Info'),
                DIV(LABEL('First Name', _for='firstname'),
                    INPUT(_name='firstname', requires=IS_NOT_EMPTY(),
                          _value=db_profile.firstname)),
                DIV(LABEL('Last Name', _for='lastname'),
                    INPUT(_name='lastname', requires=IS_NOT_EMPTY(),
                          _value=db_profile.lastname)),
                DIV(LABEL('Date of Birth', _for='dob'),
                    INPUT(_name='dob', _type='date',
                          requires=IS_DATE_IN_RANGE(maximum=date.today()),
                          _value=db_profile.dob)),
                DIV(H4('Address'),
                    DIV(LABEL('House Name / Number', _for='house'),
                        INPUT(_name='house', requires=IS_NOT_EMPTY(),
                              _value=db_address.number)),
                    DIV(LABEL('Road name', _for='street'),
                        INPUT(_name='street', requires=IS_NOT_EMPTY(),
                              _value=db_address.street)),
                    DIV(LABEL('City', _for='city'),
                        INPUT(_name='city', requires=IS_NOT_EMPTY(),
                              _value=db_address.city)),
                    DIV(LABEL('Country', _for='country'),
                        INPUT(_name='country', requires=IS_NOT_EMPTY(),
                              _value=db_address.country)),
                    DIV(LABEL('Post Code', _for='postcode'),
                        INPUT(_name='postcode', requires=IS_MATCH('^\w{4} \w{3}$'),
                              _value=db_address.postcode))),
                H3('Credit Details'),
                DIV(LABEL('Card Number', _for='card_num'),
                    INPUT(_name='card_num', _type='number', requires=IS_MATCH('^\d{12}$'),
                          _value=db_credit.number)),
                DIV(LABEL('Card Expiry Date', _for='expiry'),
                    INPUT(_name='expiry', _type='month', requires=IS_DATE_IN_RANGE(format='%Y-%m',
                                                                                   minimum=date.today()),
                          _value=db_credit.expiry)),
                DIV(LABEL('Security PIN', _for='pin'),
                    INPUT(_name='pin', _type='number', _min='000', _max='999', requires=IS_MATCH('^\d{3}$'),
                          _value=db_credit.PIN)),
                DIV(H4('Billing Address'),
                    DIV(LABEL('House Name / Number', _for='bill_house'),
                        INPUT(_name='bill_house', requires=IS_NOT_EMPTY(),
                              _value=db_credit_address.number, _readonly='true')),
                    DIV(LABEL('Road name', _for='bill_street'),
                        INPUT(_name='bill_street', requires=IS_NOT_EMPTY(),
                              _value=db_credit_address.street, _readonly='true')),
                    DIV(LABEL('City', _for='bill_city'),
                        INPUT(_name='bill_city', requires=IS_NOT_EMPTY(),
                              _value=db_credit_address.city, _readonly='true')),
                    DIV(LABEL('Country', _for='bill_country'),
                        INPUT(_name='bill_country', requires=IS_NOT_EMPTY(),
                              _value=db_credit_address.country, _readonly='true')),
                    DIV(LABEL('Post Code', _for='bill_postcode'),
                        INPUT(_name='bill_postcode', requires=IS_MATCH('^\w{4} \w{3}$'),
                              _value=db_credit_address.postcode, _readonly='true'))),
                DIV(INPUT(_type='submit', _value='Submit')))

    pledges = []
    for bootable in db((db.pledged.user_ref == request.cookies['curr_user_id'].value)
                       & (db.pledged.pledge_ref == db.pledges.id)
                       & (db.pledges.boot_ref == db.bootables.id))\
            .select(db.bootables.ALL, db.pledges.ALL, distinct=True):
        pledge = Storage()
        pledge['title'] = bootable.bootables.title
        pledge['category'] = db.categories[bootable.bootables.category_ref].name
        pledge['owner'] = db.users[bootable.bootables.boot_manager].username
        pledge['intro'] = bootable.bootables.intro
        pledge['goal'] = bootable.bootables.goal
        value_sum = db.pledges.value.sum()
        pledge['total'] = db((db.pledges.boot_ref == bootable.bootables.id)
                             & (db.pledged.pledge_ref == db.pledges.id)).select(value_sum).first()[value_sum]
        pledge['value'] = bootable.pledges.value
        pledge['reward'] = bootable.pledges.reward
        pledges.append(pledge)

    if form.accepts(request, session):
        db_profile.update_record(username=request.vars.username,
                                 pwd=request.vars.password,
                                 firstname=request.vars.firstname,
                                 lastname=request.vars.lastname,
                                 dob=request.vars.dob)

        db_address.update_record(number=request.vars.house,
                                 street=request.vars.street,
                                 city=request.vars.city,
                                 country=request.vars.country,
                                 postcode=request.vars.postcode)

        db_credit.update_record(number=request.vars.card_num,
                                expiry=request.vars.expiry,
                                PIN=request.vars.pin)

        db_credit_address.update_record(number=request.vars.bill_house,
                                        street=request.vars.bill_street,
                                        city=request.vars.bill_city,
                                        country=request.vars.bill_country,
                                        postcode=request.vars.bill_postcode)
        session.flash = 'Details updated.'
        redirect(URL())

    return dict(form=form, pledges=pledges)


def dashboard():
    """
    Shows users an overview of their bootables. Allows changing status, editing and deleting.
    Shown in sets of 10. First argument determines which set if > 10 boots.

    :arg 0 - Pagination in sets of 10
    :return - Returns a list of bootable's information for display in their short form with IDs and statuses for links
    """
    # Only allow if user logged in
    if not 'curr_user_id' in request.cookies:
        session.flash = "Sorry, you need to be signed in to see your bootables!"
        redirect(URL('default', 'index'))

    bootables = []
    for db_bootable in db(db.bootables.boot_manager == request.cookies['curr_user_id'].value) \
            .select(orderby=~db.bootables.id,
                    limitby=((0, 10) if not request.args(0)
                             else ((request.args[0] * 10), ((request.args[0] + 1) * 10)))):
        bootable = Storage()
        bootable['id'] = db_bootable.id
        if db_bootable.status == NOT_AVAILABLE:
            bootable['status'] = "Not Available to Public"
        elif db_bootable.status == OPEN_FOR_PLEDGES:
            bootable['status'] = "Open for pledges!"
        else:
            bootable['status'] = "Closed."
        bootable['title'] = A(db_bootable.title, callback=URL('boot', 'view', args=db_bootable.id)) \
            if db_bootable.status != NOT_AVAILABLE else db_bootable.title
        bootable['category'] = db.categories[db_bootable.category_ref].name
        bootable['owner'] = db.users[db_bootable.boot_manager].username
        bootable['intro'] = db_bootable.intro
        bootable['goal'] = db_bootable.goal
        value_sum = db.pledges.value.sum()
        bootable['total'] = db((db.pledges.boot_ref == db_bootable.id)
                               & (db.pledged.pledge_ref == db.pledges.id)).select(value_sum).first()[value_sum]
        bootables.append(bootable)

    return dict(bootables=bootables)


