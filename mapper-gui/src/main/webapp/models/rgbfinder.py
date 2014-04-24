# -*- coding: utf-8 -*-

#########################################################################
## Set up RGB tile cache lookups
#########################################################################

#this is for if the databases need to be stored somewhere else
#db_path = request.folder + "static/databases/"
#mapcachedb  = DAL("sqlite://rgbcaches.sqlite", folder=db_path, migrate_enabled=False)
#aquifersdb = DAL("sqlite://aquifers.sqlite", folder=db_path, migrate_enabled=False)


mapcachedb  = DAL("sqlite://rgbcaches.sqlite", migrate_enabled=False)

mapcachedb.define_table('caches',  
    Field('name', 'string', length=25)
) 

aquifersdb = DAL("sqlite://aquifers.sqlite", migrate_enabled=False)

aquifersdb.define_table('rgb',  
    Field('red', 'integer'),
    Field('green', 'integer'),
    Field('blue', 'integer')
) 

aquifersdb.define_table('fat',  
    Field('name', 'string', length=50)
) 