import pymongo
from bson.objectid import ObjectId

client = pymongo.MongoClient('mongodb://cnode:cnode@ubuntu-linux:27017/?authSource=cnode')

db = client.cnode

# db.students.insert_one({'name': 'Asabeneh', 'country': 'Finland', 'city': 'Helsinki', 'age': 250})
# print(client.list_database_names())

# students = [
#         {'name':'David','country':'UK','city':'London','age':34},
#         {'name':'John','country':'Sweden','city':'Stockholm','age':28},
#         {'name':'Sami','country':'Finland','city':'Helsinki','age':25},
#     ]
# db.students.insert_many(students)

query = {'age':250}
new_value = {'$set':{'age':38}}
db.students.update_one(query, new_value)

print(db.students.find_one())
print(db.students.find_one({'_id':ObjectId('664725e70645634cec406f3d')}))

students = db.students.find({}, {"_id":0,  "name": 1, "country":1}) # 0 means not include and 1 means include
# -1为降序
students.sort('name',-1)
for student in students:
    print(student)


print("国家是Finland")
query = {
    "country":"Finland"
}
students = db.students.find(query)
for student in students:
    print(student)

print("大于30岁的")
query = {"age":{"$gt":30}}
students = db.students.find(query)
for student in students:
    print(student)

print("小于30岁的")
query = {"age":{"$lt":30}}
students = db.students.find(query).limit(1)
for student in students:
    print(student)