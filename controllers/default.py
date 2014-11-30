# But sadly underneath's not all that great either.

__author__ = 'Y8186314'
from gluon.storage import Storage
from datetime import date


def index():
    """
    5 most recently created projects (by ID)
    5 projects closest to their goal (heavy calculation to sum all pledges, consider revising.)
    """
    # Get the 5 newest (by incremental ID) available projects
    visible = db(db.bootables.status != NOT_AVAILABLE)
    newest = visible.select(limitby=((visible.count() - 5), visible.count()))

    # Calculate distance to pledge goal for all open bootables and select top 5
    totals = db.pledges.value.sum()
    closest = db((db.bootables.status == OPEN_FOR_PLEDGES)
                 & (db.bootables.id == db.pledges.boot_ref)
                 & (db.pledges.id == db.pledged.pledge_ref))\
        .select(totals, groupby=db.bootables.id, orderby=~totals)

    return dict(pledged=closest, user_controls=user_controls)


def signup():
    """
    Form for creating a new user. Requires:
    UID, name, dob, complete address (street addr, city, country, post),
            credit card (ID, expiry, PIN, address)
    """
    # If signed in at any point, clear session and redirect to home
    if 'curr_user_id' in request.cookies:
        session.signup = dict()
        session.flash = \
            "Looks like you're already signed in! If you wish to create another account, please sign out first."
        redirect(URL('index'))

    # Break the form down into chunks to reduce visual load, don't start personal info until after username
    if (request.args(0) == '1') and 'username' in session.signup:
        session.current_signup_page = 1
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
                    DIV(INPUT(_type='submit', _value='Next')))
        form.add_button('Prev', URL('signup', args=(session.current_signup_page - 1)))

    # Finish up with credit information if personal details are complete
    elif (request.args(0) == '2') and 'address.postcode' in session.signup:
        session.current_signup_page = 2
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
                    DIV(INPUT(_type='submit', _value='Submit')))
        form.add_button('Prev', URL('signup', args=(session.current_signup_page - 1)))

    # If the page hasn't been accessed in this session, start afresh
    else:
        session.current_signup_page = 0
        form = FORM(H3('Welcome to the BootUp community!'),
                    H4('Help us get you started by choosing your community name.'),
                    DIV(LABEL('Username', _for='username'),
                        INPUT(_name='username', requires=IS_NOT_IN_DB(db, 'users.username'),
                              _value=session.signup['username'] if session.signup and 'username' in session.signup else '')),
                    DIV(LABEL('Password', _for='password'),
                        INPUT(_name='password', _type='password', requires=IS_NOT_EMPTY(),
                              _value=session.signup['password'] if session.signup and 'password' in session.signup else '')),
                    DIV(LABEL('Confirm Password', _for='confirm_pwd'),
                        INPUT(_name='confirm_pwd', _type='password', requires=IS_EQUAL_TO(request.vars.password),
                              _value=session.signup['password'] if session.signup and 'password' in session.signup else '')),
                    DIV(INPUT(_type='submit', _value='Next')))
        form.add_button('Cancel', URL('index'))

    # On receiving a valid form response
    if form.accepts(request, session):
        # Register details in session in case a user wishes to change them
        if session.current_signup_page == 0:
            if not session.signup:
                session.signup = dict()
            session.signup['username'] = request.vars.username
            session.signup['password'] = request.vars.password
            redirect(URL('signup', args=(session.current_signup_page + 1)))

        elif session.current_signup_page == 1:
            session.signup['firstname'] = request.vars.firstname
            session.signup['lastname'] = request.vars.lastname
            session.signup['dob'] = request.vars.dob
            session.signup['address.house'] = request.vars.house
            session.signup['address.street'] = request.vars.street
            session.signup['address.city'] = request.vars.city
            session.signup['address.country'] = request.vars.country
            session.signup['address.postcode'] = request.vars.postcode
            redirect(URL('signup', args=(session.current_signup_page + 1)))

        # If all forms complete, create the new user
        elif session.current_signup_page == 2:
            address_id = db.address.insert(number=session.signup['address.house'],
                                           street=session.signup['address.street'],
                                           city=session.signup['address.city'],
                                           country=session.signup['address.country'],
                                           postcode=session.signup['address.postcode'])

            # If marked, use the same data for user address and billing address
            credit_address_id = db.address.update_or_insert(number=request.vars.bill_house,
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
            del session.signup
            del session.current_signup_page

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
    if request.args(0):
        try:
            user_id = int(request.args[0])
        except ValueError:
            session.flash = "Please specify the user you're looking for by their ID"
            redirect(URL('index'))

        db_profile = db(db.users.id == user_id
                        & (db.users.address_ref == db.address.id)
                        & (db.users.credit_ref == db.credit.id)).select().first()
        if db_profile is not None:
            credit_address = db.address[db_profile.credit.address_ref]

            profile = dict()
            profile['firstname'] = db_profile.users.firstname
            profile['lastname'] = db_profile.users.lastname
            profile['username'] = db_profile.users.username
            profile['dob'] = db_profile.users.dob

            address = Storage()
            address['house'] = db_profile.address.number
            address['street'] = db_profile.address.street
            address['city'] = db_profile.address.city
            address['country'] = db_profile.address.country
            address['postcode'] = db_profile.address.postcode
            profile['address'] = address

            credit = Storage()
            credit['number'] = db_profile.credit.number
            credit['expiry'] = db_profile.credit.expiry
            credit['pin'] = db_profile.credit.PIN
            cred_address = Storage()
            cred_address['house'] = credit_address.number
            cred_address['street'] = credit_address.street
            cred_address['city'] = credit_address.city
            cred_address['country'] = credit_address.country
            cred_address['postcode'] = credit_address.postcode
            credit['address'] = cred_address
            profile['credit'] = credit

            # TODO: Bootables funding list
            profile['pledges'] = []
        else:
            session.flash = "Sorry, we couldn't find the user you're looking for."
            redirect(URL('view_profile'))

    else:
        session.flash = "Please specify the user you're looking for using their ID."
        redirect(URL('view_profile'))

    return profile


def boot_cupboard():
    """
    'Your dashboard'?
    Overview projects, change status, delete (if not open), go to edit
    Shown in sets of 10. First argument determines which set if > 10 boots.
    """
    return dict()


def new_boot():
    """
    Clear out currently held session data and start editing a new bootable.
    """
    if session.bootable:
        del session.bootable
    if session.boot_edit:
        del session.boot_edit
    if session.pledges:
        del session.pledges
    if session.pledge_edit:
        del session.pledge_edit

    redirect(URL('edit_boot'))


def edit_boot():
    """
    Edit or create boots
    """
    # Only allow if user logged in
    if not 'curr_user_id' in request.cookies:
        session.flash = "Sorry, you need to be signed in to create and modify bootables!"
        redirect(URL('index'))

    # First argument passed will be the bootable's ID if editing
    if request.args(0):
        try:  # Try to parse argument to int and get the record
            boot_id = int(request.args[0])
            bootable = db.bootables[boot_id]
            if bootable is None:
                session.flash = "Sorry, we couldn't find the bootable ID you were looking for"
                redirect(URL('index'))
            elif bootable.boot_manager != int(request.cookies['curr_user_id'].value):
                session.flash = "Sorry, you don't own that bootable!"
                redirect(URL('index'))
            elif bootable.status != NOT_AVAILABLE:
                session.flash = "Sorry, you've already made your idea available to the public! No going back now!"
                redirect(URL('index'))
            else:
                session.bootable = dict()
                session.bootable['title'] = bootable.title
                session.bootable['intro'] = bootable.intro
                # (filename, stream) = db.bootables.image.retreive(bootable.image)
                # session.bootable['image'] = shutil.copyfileobj(stream, open(filename, 'wb'))
                session.bootable['goal'] = bootable.goal
                session.bootable['category'] = bootable.category_ref
                session.bootable['desc'] = bootable.desc
                session.bootable['about_us'] = bootable.about_us
                session.boot_edit = True
        except ValueError:
            session.flash = "Sorry, bootables should be referenced by their ID"
            redirect(URL('index'))

    # Gather the category information first
    category_selector = SELECT(_name='category', requires=IS_NOT_EMPTY())
    for row in db(db.categories.id > 0).select():
        category_selector.append(OPTION(row.name, _value=row.id))
    if session.bootable:
        category_selector._value = session.bootable['category']

    print session.bootable

    # Create the bootable form. If a bootable has been found with the requested ID, pre-populate the fields.
    form = FORM(H3('Create a new Bootable Project' if not session.boot_edit else 'Editing Bootable'),
                (H4('Start with what you want to do. Let\'s get you off the ground!') if not session.boot_edit else None),
                DIV(LABEL('Bootable Name', _for='title'),
                    INPUT(_name='title', requires=IS_NOT_EMPTY(),
                          _value=session.bootable['title'] if session.bootable else '')),
                # DIV(LABEL('Title image', _for='image'),
                    # INPUT(_name='image', _type='file', requires=IS_IMAGE(maxsize=(1024, 768)),
                          # _value=session.bootable['image'] if session.bootable else '')),
                DIV(LABEL('Introduce your idea', _for='intro'),
                    TEXTAREA(_name='intro', requires=IS_NOT_EMPTY(),
                             value=session.bootable['intro'] if session.bootable else '')),
                DIV(LABEL('Category', _for='category'), category_selector),
                DIV(LABEL('Funding goal', _for='goal'),
                    INPUT(_name='goal', _type='number', _minimum='10', _maximum='1000000000',
                          requires=IS_INT_IN_RANGE(minimum=10, maximum=1000000000),
                          _value=session.bootable['goal'] if session.bootable else '')),
                DIV(LABEL('Project Description', _for='desc'),
                    TEXTAREA(_name='desc', requires=IS_NOT_EMPTY(),
                             value=session.bootable['desc'] if session.bootable else '')),
                DIV(LABEL('About you', _for='about_us'),
                    TEXTAREA(_name='about_us', requires=IS_NOT_EMPTY(),
                             value=session.bootable['about_us'] if session.bootable else '')),
                INPUT(_type='submit', _value='To the funding!' if not session.boot_edit else 'Submit Changes'))

    # If form contains all valid fields, modify the bootable or store in session for after the pledges are done
    if form.accepts(request, session):
        if not session.boot_edit:
            if not session.bootable:
                session.bootable = dict()
            session.bootable['title'] = request.vars.title
            session.bootable['intro'] = request.vars.intro
            # session.bootable['image'] = request.vars.image
            session.bootable['goal'] = request.vars.goal
            session.bootable['category'] = request.vars.category
            session.bootable['desc'] = request.vars.desc
            session.bootable['about_us'] = request.vars.about_us
            redirect(URL('edit_pledges', vars=dict(add_pledge=True)))
        else:
            db.bootables.insert(title=session.bootable['title'],
                                intro=session.bootable['intro'],
                                category_ref=session.bootable['category'],
                                goal=session.bootable['goal'],
                                # image=session.bootable['image'],
                                desc=session.bootable['desc'],
                                about_us=session.bootable['about_us'],
                                status=NOT_AVAILABLE,
                                boot_manager=request.cookies['curr_user_id'].value)
            db.commit()
            del session.bootable
            del session.boot_edit
            redirect(URL())

    return dict(form=form)


def edit_pledges():
    """
    Edit pledges screen for a bootable.
    """
    # Only allow if user logged in
    if not 'curr_user_id' in request.cookies:
        session.flash = "Sorry, you need to be signed in to change pledges!"
        redirect(URL('index'))

    # First argument passed will be the bootable's ID if editing
    if request.args(0):
        try:  # Try to parse argument to int and get the record
            boot_id = int(request.args[0])
            bootable = db.bootables[boot_id]
            if bootable is None:
                session.flash = "Sorry, we couldn't find the bootable ID you were looking for"
                redirect(URL('index'))
            elif bootable.boot_manager != int(request.cookies['curr_user_id'].value):
                session.flash = "Sorry, you don't own that bootable!"
                redirect(URL('index'))
            elif bootable.status != NOT_AVAILABLE:
                session.flash = "Sorry, you've already made your idea available to the public! No going back now!"
                redirect(URL('index'))
            else:
                session.pledges = dict()
                for pledge in db(db.pledges.boot_ref == boot_id).select(db.pledges.id,
                                                                        db.pledges.value,
                                                                        db.pledges.reward):
                    session.pledges[pledge.id] = (pledge.value, pledge.reward)
                session.pledge_edit = boot_id
        except ValueError:
            session.flash = "Sorry, bootables should be referenced by their ID"
            redirect(URL('index'))
    elif not session.pledges:
        session.pledges = dict()

    # Create list of current pledges, making the pledge editable or deleting if selected
    pledges = DIV()
    for pledge_id in session.pledges.keys():
        (value, reward) = session.pledges[pledge_id]

        # Skip deleted pledges
        if value is not None and reward is not None:
            if request.vars.pledge_edit_id and int(request.vars.pledge_edit_id) == pledge_id:
                form = FORM(DIV(LABEL('Value', _for='value'),
                                INPUT(_name='value', _minimum='1', _maximum='1000000000',
                                      requires=IS_INT_IN_RANGE(minimum=1, maximum=1000000000),
                                      _value=value)),
                            DIV(LABEL('Reward', _for='reward'),
                                TEXTAREA(_name='reward', requires=IS_NOT_EMPTY()), value=reward),
                            INPUT(_type='submit', _value='Submit'))
                pledges.append(form)

            elif request.vars.delete_pledge_id and int(request.vars.delete_pledge_id) == pledge_id:
                session.pledges[pledge_id] = (None, None)

            else:
                pledges.append(DIV(SPAN('Value: ' + value),
                                   SPAN('Reward: ' + reward),
                                   A('Edit', callback=URL(vars=dict(pledge_edit_id=pledge_id))),
                                   A('Delete', callback=URL(vars=dict(delete_pledge_id=pledge_id)))))

    # Add an empty pledge form at the end if requested
    if request.vars.add_pledge:
        form = FORM(DIV(LABEL('Value', _for='value'),
                        INPUT(_name='value', _minimum='1', _maximum='1000000000',
                              requires=IS_INT_IN_RANGE(minimum=1, maximum=1000000000))),
                    DIV(LABEL('Reward', _for='reward'),
                        TEXTAREA(_name='reward', requires=IS_NOT_EMPTY())),
                    INPUT(_type='submit', _value='Submit'))
        pledges.append(form)

    # Buttons for adding pledges to a bootable finalising changes
    pledges.append(A('Add pledge', callback=URL(vars=dict(add_pledge=True))))
    pledges.append(A('Save & Finish', callback=URL('finish_boot')))
    pledges.append(A('Return to Bootable', callback=URL('edit_boot')))

    # Submitting changes to a pledge
    if 'form' in locals() and form.accepts(request, session):
        # Add new pledge, marked by an id < 0
        if request.vars.add_pledge:
            session.pledges[-1 if -1 not in session.pledges else min(session.pledges.keys()) - 1] \
                = (request.vars.value, request.vars.reward)

        # Else find and update in the session data
        else:
            session.pledges[int(request.vars.pledge_edit_id)] = (request.vars.value, request.vars.reward)

        redirect(URL())

    # If the bootable has been completed, start creating pledges
    return dict(pledges=pledges)


def view_boot():
    """
    Shows: status, goal, pledges available,
            current contributions (username, amount, expected reward),
            current pledged amount, all normal bootable information.
    """
    if request.args(0):
        try:
            boot_id = int(request.args[0])
        except ValueError:
            session.flash = "Please specify the user you're looking for by their ID"
            redirect(URL('index'))

        db_bootable = db(db.bootables.id == boot_id).select().first()
        if db_bootable is not None:
            bootable = dict()
            bootable['title'] = db_bootable.title
            bootable['intro'] = db_bootable.intro
            bootable['category'] = db.categories[db_bootable.category_ref].name
            bootable['goal'] = db_bootable.goal
            bootable['description'] = db_bootable.desc
            bootable['about'] = db_bootable.about_us
            bootable['owner'] = db.users[db_bootable.boot_manager].username
            bootable['pledges'] = []

            total = 0

            # Collect the list of pledges available
            for db_pledge in db(db.pledges.boot_ref == boot_id).select():
                pledge = Storage()
                pledge['value'] = db_pledge.value
                pledge['reward'] = db_pledge.reward
                pledge['pledge_link'] = A('Pledge', _class='button',
                                          callback=URL('pledge', args=db_pledge.id))
                pledge['pledgers'] = []

                # Create a list of pledgers and sum their pledges
                for db_pledger in db((db.pledged.pledge_ref == db_pledge.id)
                                     & (db.pledged.user_ref == db.users.id)).select(db.users.username, db.users.id):
                    if 'curr_user_id' in request.cookies and db_pledger.id == int(request.cookies['curr_user_id'].value):
                        pledge['pledgers'].insert(0, 'YOU!')
                    else:
                        pledge['pledgers'].append(db_pledger.username)
                    total += db_pledge.value

                bootable['pledges'].append(pledge)

            bootable['total'] = total
        else:
            session.flash = "Sorry, we couldn't find the bootable you're looking for."
            redirect(URL('view_profile'))

    else:
        session.flash = "Please specify the bootable you're looking for using their ID."
        redirect(URL('view_profile'))

    return bootable


def finish_boot():
    """
    Page call to a bootable from the variables currently stored in the session.
    """
    # If called via a new bootable in session, create that object first
    if session.bootable:
        boot_id = db.bootables.insert(title=session.bootable['title'],
                                      intro=session.bootable['intro'],
                                      category_ref=session.bootable['category'],
                                      goal=session.bootable['goal'],
                                      # image=session.bootable['image'],
                                      desc=session.bootable['desc'],
                                      about_us=session.bootable['about_us'],
                                      status=NOT_AVAILABLE,
                                      boot_manager=request.cookies['curr_user_id'].value)
    # Otherwise use the bootable id they've been editing
    else:
        boot_id = session.pledge_edit

    print(session.pledges)

    # Mark if there is a pledge for the bootable
    has_pledges = False

    # Insert, update or delete pledges
    for pledge_id in session.pledges.keys():
        (value, reward) = session.pledges[pledge_id]

        # New pledges with id < 0 that contain values
        if pledge_id < 0 and value is not None and reward is not None:
            db.pledges.insert(boot_ref=boot_id,
                              value=value,
                              reward=reward)
            has_pledges = True

        # Deleted pledges with None for value and reward that already exist
        elif value is None and reward is None and pledge_id > 0:
            db.pledges[pledge_id].delete()

        # Update records as normal
        elif pledge_id > 0:
            db.pledges[pledge_id].update(value=value, reward=reward)
            has_pledges = True

    if not has_pledges:
        session.flash = "Your bootable needs at least one pledgable amount!"
        redirect(URL('edit_pledges'))

    if session.bootable:
        del session.bootable
    del session.pledges
    if session.pledge_edit:
        del session.pledge_edit
    db.commit()

    redirect(URL('view_boot', args=boot_id))


def search():
    """
    Page for showing search results in a list.
    First argument sets which 10 results to display if result set is larger.
    """
    if 'query' in request.vars:
        result = []

        for db_result in db(db.bootables.title.contains(request.vars.query)
                            | db.bootables.intro.contains(request.vars.query)) \
                .select(limitby=(request.args[0] * 10, (request.args[0] + 1) * 10) if request.args(0) else None):
            bootable = Storage()
            bootable['title'] = db_result.title
            bootable['category'] = db.categories[db_result.category_ref].name
            bootable['owner'] = db.users[db_result.boot_manager].username
            bootable['intro'] = db_result.intro
            bootable['goal'] = db_result.goal
            value_sum = db.pledges.value.sum()
            bootable['total'] = db((db.pledges.boot_ref == db_result.id)
                                   & (db.pledged.pledge_ref == db.pledges.id)).select(value_sum).first()[value_sum]

            if 'category' in request.vars and request.vars.category in bootable['category']:
                result.append(bootable)
            elif 'category' not in request.vars:
                result.append(bootable)

            search_string = request.vars.query
            if 'category' in request.vars:
                search_string += ' @' + request.vars.category
            if request.args(0):
                search_string += '(' + str(request.args[0] * 10) + '-' + str((request.args[0] + 1) * 10) + ')'

    else:
        session.flash = 'Please pass in a search query'
        redirect(URL('index'))

    return dict(result=result, search_string=search_string)


def pledge():
    """
    Takes and integer as an argument and pledges the currently signed in user to that pledge id.
    """
    # Check for valid arguments
    if request.args(0):
        try:
            pledge_id = int(request.args[0])
        except ValueError:
            session.flash = "Please refer to the pledge you want to donate to by its ID."
            redirect(URL('index'))
    else:
        session.flash = "Please refer to the pledge you want to donate to with its ID."
        redirect(URL('index'))

    # Only allow signed in users to pledge
    if not 'curr_user_id' in request.cookies:
        session.flash = "Sorry, you need to be signed in to pledge!"
        redirect(URL('index'))

    m_pledge = db.pledges[pledge_id]
    db.pledged.insert(pledge_ref=pledge_id,
                      user_ref=request.cookies['curr_user_id'].value)
    db.commit()

    boot_title = db.bootables[m_pledge.boot_ref].title

    session.flash = "You just pledged £" + m_pledge.reward + " to " + boot_title + ". Good on you. :)"
    redirect(URL('view_boot', args=m_pledge.boot_ref))

def login():
    """
    Takes login username and password, return login cookie if valid
    """
    login_record = db.users(username=request.vars.login_user)

    print request.vars

    if (login_record is not None) and request.vars.login_pwd == login_record.pwd:
        response.cookies['curr_user_id'] = login_record.id
        response.cookies['curr_user_id']['expires'] = 24 * 3600
        response.cookies['curr_user_id']['path'] = '/'
    else:
        session.flash = 'Sorry, that username and password combination doesn\'t exist'

    redirect(URL('index'))


def logout():
    """
    Page users are directed to in order to logout. Logs out and redirects to home.
    """
    response.cookies['curr_user_id'] = -1
    response.cookies['curr_user_id']['expires'] = -10
    response.cookies['curr_user_id']['path'] = '/'
    redirect(URL('index'))

