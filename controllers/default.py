# But sadly underneath's not all that great either.
__author__ = 'Y8186314'
from gluon.storage import Storage


def index():
    """
    Home page, displays the 5 most recently created projects (by ID) and the 5 projects closest to their goal.

    :return  - Returns 2 lists of bootable's information for display in their short forms
    """
    # Get the 5 newest (by incremental ID) available projects
    newest = []
    for db_bootable in db(db.bootables.status != NOT_AVAILABLE).select(orderby=~db.bootables.id, limitby=(0, 5)):
        bootable = Storage()
        bootable['title'] = A(db_bootable.title, callback=URL('boot', 'view', args=db_bootable.id))
        bootable['category'] = db.categories[db_bootable.category_ref].name
        bootable['owner'] = db.users[db_bootable.boot_manager].username
        bootable['intro'] = db_bootable.intro
        bootable['goal'] = db_bootable.goal
        value_sum = db.pledges.value.sum()
        bootable['total'] = db((db.pledges.boot_ref == db_bootable.id)
                               & (db.pledged.pledge_ref == db.pledges.id)).select(value_sum).first()[value_sum]
        newest.append(bootable)

    # Calculate distance to pledge goal for all open bootables and select top 5
    totals = db.pledges.value.sum()
    closest = []
    for db_bootable in db((db.bootables.status == OPEN_FOR_PLEDGES)
                          & (db.bootables.id == db.pledges.boot_ref)
                          & (db.pledges.id == db.pledged.pledge_ref))\
            .select(db.bootables.ALL, totals, groupby=db.bootables.id, orderby=(db.bootables.goal - totals),
                    having=(db.bootables.goal > totals), limitby=(0, 5)):
        bootable = Storage()
        bootable['title'] = A(db_bootable.bootables.title, callback=URL('boot', 'view', args=db_bootable.bootables.id))
        bootable['category'] = db.categories[db_bootable.bootables.category_ref].name
        bootable['owner'] = db.users[db_bootable.bootables.boot_manager].username
        bootable['intro'] = db_bootable.bootables.intro
        bootable['goal'] = db_bootable.bootables.goal
        bootable['total'] = db_bootable[totals]
        closest.append(bootable)

    return dict(newest=newest, closest=closest)


def search():
    """
    Page for showing search results in a list.

    :arg 0 - Paginate results by 10s
    :var query - Query string to search for in bootable titles and intros
    :var category - Query string to search for category names containing it
    :return - Returns a list of bootables matching the query and category parameters (if supplied)
    """
    if 'query' in request.vars:
        result = []

        for db_result in db((db.bootables.title.lower().contains(request.vars.query.lower())
                            | db.bootables.intro.lower().contains(request.vars.query.lower()))
                            & (db.bootables.status != NOT_AVAILABLE))\
                .select(limitby=(request.args[0] * 10, (request.args[0] + 1) * 10) if request.args(0) else None):
            bootable = Storage()
            bootable['title'] = A(db_result.title, callback=URL('boot', 'view', args=db_result.id))
            bootable['category'] = db.categories[db_result.category_ref].name
            bootable['owner'] = db.users[db_result.boot_manager].username
            bootable['intro'] = db_result.intro
            bootable['goal'] = db_result.goal
            value_sum = db.pledges.value.sum()
            bootable['total'] = db((db.pledges.boot_ref == db_result.id)
                                   & (db.pledged.pledge_ref == db.pledges.id)).select(value_sum).first()[value_sum]

            # Post process the category search
            if 'category' in request.vars and request.vars.category.lower() in bootable['category'].lower():
                result.append(bootable)
            elif 'category' not in request.vars:
                result.append(bootable)

        # Report the user's search query
        search_string = request.vars.query
        if 'category' in request.vars:
            search_string += ' @' + request.vars.category
        if request.args(0):
            search_string += '(' + str(request.args[0] * 10) + '-' + str((request.args[0] + 1) * 10) + ')'

    else:
        session.flash = 'Please pass in a search query'
        redirect(URL('default', 'index'))

    return dict(result=result, search_string=search_string)


def login():
    """
    Login function controller.

    :var login_user - Username to attempt sign in as
    :var login_pwd - Password to check against the database
    :return - If successful, creates a cookie in the browser containing the now logged in ID for 24 hours
    """
    login_record = db.users(username=request.vars.login_user)

    print request.vars

    if (login_record is not None) and request.vars.login_pwd == login_record.pwd:
        response.cookies['curr_user_id'] = login_record.id
        response.cookies['curr_user_id']['expires'] = 24 * 3600
        response.cookies['curr_user_id']['path'] = '/'
    else:
        session.flash = 'Sorry, that username and password combination doesn\'t exist'

    redirect(URL('default', 'index'))


def logout():
    """ Page users are directed to in order to logout. Deletes the login cookie and redirects to home. """
    response.cookies['curr_user_id'] = -1
    response.cookies['curr_user_id']['expires'] = -10
    response.cookies['curr_user_id']['path'] = '/'
    redirect(URL('default', 'index'))

