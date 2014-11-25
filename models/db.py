# -*- coding: utf-8 -*-
__author__ = 'Y8186314'
from gluon import DAL, Field

db = DAL('sqlite://bootup.db')
db.define_table('address',
                Field('number', 'string', required=True, notnull=True),
                Field('street', 'string', required=True, notnull=True),
                Field('city', 'string', required=True, notnull=True),
                Field('country', 'string', required=True, notnull=True),
                Field('postcode', 'string', required=True, notnull=True))
db.define_table('credit',
                Field('number', 'integer', required=True, notnull=True),
                Field('expiry', 'date', required=True, notnull=True),
                Field('PIN', 'integer', required=True, notnull=True),
                Field('address_ref', 'reference address', required=True, notnull=True))
db.define_table('users',
                Field('username', 'string', required=True, notnull=True, unique=True),
                Field('pwd', 'password', required=True, notnull=True),
                Field('firstname', 'string', required=True, notnull=True),
                Field('lastname', 'string', required=True, notnull=True),
                Field('dob', 'date', required=True, notnull=True),
                Field('address_ref', 'reference address', required=True, notnull=True),
                Field('credit_ref', 'reference credit', required=True, notnull=True))
db.define_table('categories',
                Field('name', 'string', required=True, notnull=True))
db.define_table('bootables',
                Field('title', 'string', required=True, notnull=True),
                Field('intro', 'text', required=True, notnull=True),
                Field('category_ref', 'reference categories', required=True, notnull=True),
                Field('goal', 'integer', required=True, notnull=True),
                Field('image', 'upload', uploadfield='image_file', required=True, notnull=True),
                Field('image_file', 'blob', required=True, notnull=True),
                Field('desc', 'text', required=True, notnull=True),
                Field('about_us', 'text', required=True, notnull=True),
                Field('status', 'string', required=True, notnull=True, default='NOT_AVAILABLE'),
                Field('boot_manager', 'reference users', required=True, notnull=True))
db.define_table('pledges',
                Field('boot_ref', 'reference bootables', required=True, notnull=True),
                Field('value', 'integer', required=True, notnull=True),
                Field('reward', 'text', required=True, notnull=True))
db.define_table('pledged',
                Field('pledge_ref', 'reference pledges', required=True, notnull=True),
                Field('user_ref', 'reference users', required=True, notnull=True))

