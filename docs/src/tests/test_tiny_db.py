from tinydb import TinyDB, Query
db = TinyDB("./db.json") # in memory?
# db = TinyDB('/path/to/db.json')
# we use upsert instead?
db.insert({'name':'sampleName', 'start':0, 'end':20})
# no deduplication?
db.insert({'name':'sampleName2', 'start':21, 'end':40})
db.insert({'name':'withOriginalLine', 'value':True})
db.insert({"path":'abcdefg'})

User = Query()

# this thing is a limited implementation of no-sql database. SQL is advanced.

# point = 15
# result = db.search((User.start <= point) & (User.end >= point))
# print("RESULT:", result)

result = db.search((User.name == 'withOriginalLine'))
print('RESULT:', result)
result = db.search((User.path == 'abcdefg'))
print('RESULT:', result)