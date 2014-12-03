__author__ = 'Y8186314'
from gluon.storage import Storage


def index():
    """ Set default action for bootable controller to create a new bootable. """
    redirect(URL('boot', 'new'))


def new():
    """ Clear out currently held session data and start editing a new bootable. """
    if session.bootable:
        del session.bootable
    if session.boot_edit:
        del session.boot_edit
    if session.pledges:
        del session.pledges
    if session.pledge_edit:
        del session.pledge_edit

    redirect(URL('boot', 'edit'))


def edit():
    """
    Edit or create boots, progress is held in session storage.

    :arg 0: If passed, this will be the bootable ID to edit
    :return: Returns the form to display for setting a bootable's information
    """
    # Only allow if user logged in
    if not 'curr_user_id' in request.cookies:
        session.flash = "Sorry, you need to be signed in to create and modify bootables!"
        redirect(URL('default', 'index'))

    # First argument passed will be the bootable's ID if editing
    if request.args(0):
        try:  # Try to parse argument to int and get the record
            boot_id = int(request.args[0])
            bootable = db.bootables[boot_id]
            if bootable is None:
                session.flash = "Sorry, we couldn't find the bootable ID you were looking for"
                redirect(URL('default', 'index'))
            elif bootable.boot_manager != int(request.cookies['curr_user_id'].value):
                session.flash = "Sorry, you don't own that bootable!"
                redirect(URL('default', 'index'))
            elif bootable.status != NOT_AVAILABLE:
                session.flash = "Sorry, you've already made your idea available to the public! No going back now!"
                redirect(URL('profile', 'dashboard'))
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
            redirect(URL('default', 'index'))

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
                    TEXTAREA(_name='intro', requires=[IS_NOT_EMPTY(), IS_LENGTH(120)],
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
            redirect(URL('boot', 'edit_pledges', vars=dict(add_pledge=True)))
        else:
            db.bootables[request.args[0]].update_record(title=request.vars.title,
                                                        intro=request.vars.intro,
                                                        category_ref=request.vars.category,
                                                        goal=request.vars.goal,
                                                        # image=request.vars.image,
                                                        desc=request.vars.desc,
                                                        about_us=request.vars.about_us)
            del session.bootable
            del session.boot_edit
            redirect(URL('profile', 'dashboard'))

    return dict(form=form)


def delete():
    """
    Controller function for deleting a bootable.
    Only allows deletion if not open and belongs to the logged in user.

    :arg 0: The ID of the bootable to delete
    """
    # Only allow if user logged in
    if not 'curr_user_id' in request.cookies:
        session.flash = "Sorry, you need to be signed in to create and modify bootables!"
        redirect(URL('default', 'index'))

    if request.args(0):
        db_bootable = db.bootables[int(request.args[0])]
        if db_bootable.boot_manager != int(request.cookies['curr_user_id'].value):
            session.flash = "Sorry, that bootable doesn't belong to you."
        elif db_bootable.status == OPEN_FOR_PLEDGES:
            session.flash = "Sorry, that bootable's currently open to pledges." \
                            " You need to close it before you can delete it."
        else:
            db_bootable.delete_record()
    else:
        session.flash = "Please specify the ID of the bootable you wish to delete."
    redirect(URL('profile', 'dashboard'))


def progress():
    """
    Progress a bootable through its lifecycle.
    NOT_AVAILABLE -> OPEN_FOR_PLEDGES -> CLOSED.
    Closing can result in CLOSED_FUNDED or CLOSED_NOT_FUNDED depending on how much has been pledged.
    Only allows progression if not at the end of its lifecycle and belongs to the currently signed in user.

    :arg 0: The ID of the bootable to progress
    """
    # Only allow if user logged in
    if not 'curr_user_id' in request.cookies:
        session.flash = "Sorry, you need to be signed in to create and modify bootables!"
        redirect(URL('default', 'index'))

    if request.args(0):
        db_bootable = db.bootables[int(request.args[0])]
        if db_bootable.boot_manager != int(request.cookies['curr_user_id'].value):
            session.flash = "Sorry, that bootable doesn't belong to you."
        elif db_bootable.status == NOT_AVAILABLE:
            db_bootable.update_record(status=OPEN_FOR_PLEDGES)
        elif db_bootable.status == OPEN_FOR_PLEDGES:
            value_sum = db.pledges.value.sum()
            raised = db((db.pledges.boot_ref == db_bootable.id)
                        & (db.pledged.pledge_ref == db.pledges.id)).select(value_sum).first()[value_sum]
            if raised > db_bootable.goal:
                db_bootable.update_record(status=CLOSED_FUNDED)
            else:
                db_bootable.update_record(status=CLOSED_NOT_FUNDED)
        else:
            session.flash = "Your bootable has already been closed, there's nothing more to do!"
    else:
        session.flash = "Please specify the ID of the bootable you wish to delete."
    redirect(URL('profile', 'dashboard'))


def edit_pledges():
    """
    Edit pledges of a bootable.
    Users can only edit pledges for bootables that are NOT_AVAILABLE and belong to them.

    :arg 0: The ID of the bootable for which to edit pledges verily
    :return: Returns a complete div with all pledges, the pledge currently being edited and completion controls.
    """
    # Only allow if user logged in
    if not 'curr_user_id' in request.cookies:
        session.flash = "Sorry, you need to be signed in to change pledges!"
        redirect(URL('default', 'index'))

    # First argument passed will be the bootable's ID if editing
    if request.args(0):
        try:  # Try to parse argument to int and get the record
            boot_id = int(request.args[0])
            bootable = db.bootables[boot_id]
            if bootable is None:
                session.flash = "Sorry, we couldn't find the bootable ID you were looking for"
                redirect(URL('default', 'index'))
            elif bootable.boot_manager != int(request.cookies['curr_user_id'].value):
                session.flash = "Sorry, you don't own that bootable!"
                redirect(URL('default', 'index'))
            elif bootable.status != NOT_AVAILABLE:
                session.flash = "Sorry, you've already made your idea available to the public! No going back now!"
                redirect(URL('profile', 'dashboard'))
            else:
                session.pledges = dict()
                for pledge in db(db.pledges.boot_ref == boot_id).select(db.pledges.id,
                                                                        db.pledges.value,
                                                                        db.pledges.reward,
                                                                        orderby=db.pledges.value):
                    session.pledges[pledge.id] = (pledge.value, pledge.reward)
                session.pledge_edit = boot_id
        except ValueError:
            session.flash = "Sorry, bootables should be referenced by their ID"
            redirect(URL('default', 'index'))
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
                pledges.append(DIV(SPAN('Value: {}' + str(value)),
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
    pledges.append(A('Save & Finish', callback=URL('boot', 'finish')))
    pledges.append(A('Return to Bootable', callback=URL('boot', 'edit')))

    # Submitting changes to a pledge
    if 'form' in locals() and form.accepts(request, session):
        # Add new pledge, marked by an id < 0
        if request.vars.add_pledge:
            session.pledges[-1 if -1 not in session.pledges else min(session.pledges.keys()) - 1] \
                = (request.vars.value, request.vars.reward)

        # Else find and update in the session data
        else:
            session.pledges[int(request.vars.pledge_edit_id)] = (request.vars.value, request.vars.reward)

        redirect(URL(vars=dict(add_pledge=True)))

    # If the bootable has been completed, start creating pledges
    return dict(pledges=pledges)


def view():
    """
    Bootable view. Only those that are not NOT_AVAILABLE can be viewed.

    :return: Returns a bootable object for display in its long form including all pledges and pledgers.
    """
    if request.args(0):
        try:
            boot_id = int(request.args[0])
        except ValueError:
            session.flash = "Please specify the user you're looking for by their ID"
            redirect(URL('default', 'index'))

        db_bootable = db(db.bootables.id == boot_id).select().first()
        if db_bootable is not None and db_bootable.status != NOT_AVAILABLE:
            bootable = dict()
            bootable['title'] = db_bootable.title
            bootable['status'] = "Open for pledges!" if db_bootable.status == OPEN_FOR_PLEDGES else "Closed."
            bootable['intro'] = db_bootable.intro
            bootable['category'] = db.categories[db_bootable.category_ref].name
            bootable['goal'] = db_bootable.goal
            bootable['description'] = db_bootable.desc
            bootable['about'] = db_bootable.about_us
            bootable['owner'] = db.users[db_bootable.boot_manager].username
            bootable['pledges'] = []

            total = 0

            # Collect the list of pledges available
            for db_pledge in db(db.pledges.boot_ref == boot_id).select(orderby=db.pledges.value):
                pledge = Storage()
                pledge['value'] = db_pledge.value
                pledge['reward'] = db_pledge.reward
                if db_bootable.status == OPEN_FOR_PLEDGES:
                    pledge['pledge_link'] = A('Pledge', _class='button pledge_link',
                                              callback=URL('boot', 'pledge', args=db_pledge.id))
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
            redirect(URL('default', 'index'))

    else:
        session.flash = "Please specify the bootable you're looking for using their ID."
        redirect(URL('default', 'index'))

    response.files.insert(2, URL('static', 'css/view_boot.css'))
    return bootable


def finish():
    """ Controller function to finalise changes in edit_pledges and create a bootable if held in session. """
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

    # A bootable must have at least one pledgeable amount
    if not has_pledges:
        session.flash = "Your bootable needs at least one pledgable amount!"
        redirect(URL('boot', 'edit_pledges'))

    if session.bootable:
        del session.bootable
    del session.pledges
    if session.pledge_edit:
        del session.pledge_edit
    db.commit()

    redirect(URL('profile', 'dashboard'))


def pledge():
    """
    Controller function for pledging an amount as the currently logged in user.

    :arg 0: The pledge ID to pledge to
    """
    # Check for valid arguments
    if request.args(0):
        try:
            pledge_id = int(request.args[0])
        except ValueError:
            session.flash = "Please refer to the pledge you want to donate to by its ID."
            redirect(URL('default', 'index'))
    else:
        session.flash = "Please refer to the pledge you want to donate to with its ID."
        redirect(URL('default', 'index'))

    m_pledge = db.pledges[pledge_id]
    bootable = db.bootables[m_pledge.boot_ref]

    # Only allow signed in users to pledge
    if not 'curr_user_id' in request.cookies:
        session.flash = "Sorry, you need to be signed in to pledge!"
        redirect(URL('boot', 'view', args=bootable.id))

    # Only allow pledging to bootables that are OPEN_FOR_PLEDGES
    if bootable.status == OPEN_FOR_PLEDGES:
        # Only update the user's pledge if they've already pledged
        already_pledged = False
        for bootable_pledge in db(bootable.id == db.pledges.boot_ref).select(db.pledges.id):
            if not db((db.pledged.user_ref == request.cookies['curr_user_id'].value)
                      & (db.pledged.pledge_ref == bootable_pledge.id)).isempty():
                already_pledged = True
                db(db.pledged.pledge_ref == bootable_pledge).select().first().update_record(pledge_ref=pledge_id)
                session.flash = "Changed your pledge to £" + str(m_pledge.value)

        # Else, pledge anew
        if not already_pledged:
            db.pledged.insert(pledge_ref=pledge_id,
                              user_ref=request.cookies['curr_user_id'].value)
            db.commit()
            session.flash = "You just pledged £" + str(m_pledge.value) + " to " + bootable.title + ". Good on you. :)"
    else:
        session.flash = "Sorry, that bootable's not open for pledges right now!"
    redirect(URL('boot', 'view', args=bootable.id))
