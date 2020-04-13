from flask import Flask, jsonify, request, render_template, abort, Response
import json
#import flask_restful
import re
import pymongo
import requests
from datetime import datetime
import time

#WORKING  WITH THE DATABASE

myclient = pymongo.MongoClient("mongodb://ride_mongodb:27017/")
mydb = myclient["RideShare_rides"]
rides = mydb['rides']
count = mydb['count']

app = Flask(__name__)

def validateTimestamp(tz):
        try:
            datetime.strptime(tz, "%d-%m-%Y:%S-%M-%H")
            return 1
        except:
            return 0

def compare_time(to_check):
    pattern = "%Y%m%d%S%M%H"
    dt = datetime.now()
    current= dt.strftime(pattern)
    # print(current)
    # to_check = "10-11-2022:12-12-08"
    # to_check = to_check.strftime("%Y-%m-%d:%S-%M-%H")
    li = to_check.split(":")
    date = li[0]
    time = li[1]
    temp = date.split("-")
    time = time.split("-")
    temp_var = temp[2]
    temp[2] = temp[0]
    temp[0] = temp_var
    to_check = ""
    for i in temp:
        to_check += i
    for i in time:
        to_check += i
    if (to_check > current):
        return 1
    return 0


def increment_count():
    found = 0
    dbquery = count.find({})
    for i in dbquery:
        found = 1
        break
    if found == 0:
        query = {"id" : "counting_accesses", "access" : 0}
        count.insert(query)
    else:
        value = 0
        select = {"id" : "counting_accesses"}
        dbquery = count.find(select)
        for i in dbquery:
            value = i["access"]
            break
        value += 1
        new_value = {"$set" : {"access" : value}}
        count.update(select, new_value)
    return 0

@app.errorhandler(404)
def not_found_error(error):
    return "Not found", 404

@app.errorhandler(400)
def bad_request_error(error):
    return "Bad Request", 400

@app.errorhandler(405)
def method_not_allowed_error(error):
    return "Methods Not Allowed", 405

@app.errorhandler(500)
def internal_server_error(error):
    return "Internal Server Error", 500

#API'S

@app.route('/')
def test():
    return "HELLO WORLD"



@app.route('/api/v1/test', methods = ["GET"])
def check_user():
    # if(request.method == "GET"):
    d = {}
    d['table'] = "users"
    d["work"] = "GET_ALL"
    d["check"] = None
    d["data"] = {}
    db_query = requests.get("http://CC-Project-93974937.us-east-1.elb.amazonaws.com/api/v1/users", data = json.dumps(d))  #user_service:8000
    dbquery = json.loads(db_query.text)
            # for i in dbquery:
    return jsonify(dbquery), 200
    # else:
    #     return {}, 405


@app.route('/api/v1/rides', methods = ['POST'])
def new_ride():
    if (request.method == 'POST'):
        increment_count()
        dataDict = request.get_json()
        source = dataDict["source"]
        source = int(source)
        destination = dataDict["destination"]
        destination = int(destination)
        username = dataDict["created_by"]
        timestamp = dataDict['timestamp']   #VALIDATE TIMESTAMP
        # print("check")
        if not(validateTimestamp(timestamp)):
            return {}, 400
        # print("check1")
        if (source >= 1 and source <= 198) and (destination >= 1 and destination <= 198):
            d = {}
            d["table"] = "rides"
            d["work"] = "INSERT"
            d["data"] = dataDict
            # d["rideid"] = 0
            d["check"] = "user"
            d["data"]["username"] = username
            list_of_users = requests.get("http://localhost:8000/api/v1/test", data = json.dumps(d))
            list_of_users = json.loads(list_of_users.text)
            found = 0
            for i in list(list_of_users):
                if i == username:
                    found = 1
                    break
            # return jsonify({"found" : found}), 200
            # found = int(found)
            if found == 0:
                return {}, 400  
                
            else:        
                # d["rideid"] = 1
                d["check"] = None
                rideid = requests.post("http://localhost:8000/api/v1/db/read", data = json.dumps(d))
                rideid = rideid.text
                rideid = int(rideid)
                d["data"]["ride_id"] = rideid
                retjson = requests.post("http://localhost:8000/api/v1/db/write", data = json.dumps(d))
                return {}, 201
        else:
            return {}, 400
    else:
        return {}, 405  #POST METHOD NOT USED


@app.route('/api/v1/rides', methods = ['GET']) #CHECK FOR THE SOURCE AND DESTINATION
def upcoming_rides():
    if (request.method == 'GET'):
        increment_count()
        source = request.args.get("source")
        if source == None or source == '':
            return {}, 400
        source = int(source)
        destination = request.args.get("destination")
        if destination == None or destination == '':
            return {}, 400
        destination = int(destination)
        if (source >= 1 and source <= 198) and (destination >= 1 and destination <= 198):
            d = {}
            d["table"] = "rides"
            d["work"] = "GET_RIDES"
            dataDict = {"source" : source, "destination" : destination}
            d["data"] = dataDict
            d["check"] = None
            dbquery = requests.post("http://localhost:8000/api/v1/db/read", data = json.dumps(d))
            dbquery = json.loads(dbquery.text)
            for i in dbquery:
                return jsonify(dbquery), 200
            else:
                return {}, 204
        else:
            return {}, 400
    else:
        return {}, 405


@app.route('/api/v1/rides/<rideId>', methods = ['GET'])
def list_all_details(rideId):
    if (request.method == 'GET'):
        increment_count()
        rideid = int(rideId)
        d = {}
        d["table"] = "rides"
        d["work"] = "ALL_DETAILS"
        dataDict = {"ride_id" : rideid}
        d["data"] = dataDict
        d["check"] = None
        dbquery = requests.post("http://localhost:8000/api/v1/db/read", data = json.dumps(d))
        if (dbquery.status_code == 400):
            return {}, 400
        dbquery = json.loads(dbquery.text)

        return jsonify(dbquery), 200
    else:
        return {}, 405

        
@app.route('/api/v1/rides/<rideId>', methods = ['POST'])
def join_ride(rideId):
    if (request.method == 'POST'):
        increment_count()
        rideid = int(rideId)
        dataDict = request.get_json()
        username = dataDict["username"]
        d = {}
        list_of_users = requests.get("http://localhost:8000/api/v1/test", data = json.dumps(d))
        list_of_users = json.loads(list_of_users.text)
        found = 0
        for i in list(list_of_users):
            if i == username:
                found = 1
                break
            # return jsonify({"found" : found}), 200
            # found = int(found)
        if found == 0:
            return {}, 400  
        dataDict["ride_id"] = rideid
        d = {}
        d["table"] = "rides"
        d["work"] = "JOIN_EXISTING"
        d["data"] = dataDict
        d["check"] = None
        dbquery = requests.post("http://localhost:8000/api/v1/db/read", data = json.dumps(d))
        dbquery = dbquery.text
        if dbquery == "10":
            return {}, 400
        else:
            retjson = requests.post("http://localhost:8000/api/v1/db/write", data = json.dumps(d))
            return {}, 200


@app.route('/api/v1/rides/<rideId>', methods = ['DELETE'])
def delete_ride(rideId):
    if (request.method == 'DELETE'):
        increment_count()
        rideid = int(rideId)
        d = {}
        d["table"] = "rides"
        d["work"] = "DELETE"
        d["check"] = None
        dataDict = {"ride_id" : rideid}
        d["data"] = dataDict
        found = requests.post("http://localhost:8000/api/v1/db/read", data = json.dumps(d))
        found = int(found.text)
        if (found == 0):
            return {}, 400
        retjson = requests.post("http://localhost:8000/api/v1/db/write", data = json.dumps(d))
        return {}, 200
    else:
        return {}, 405


@app.route('/api/v1/db/read', methods = ['POST'])
def db_read():

    dataDict = json.loads(request.data)
    table = dataDict["table"]
    work = dataDict["work"]
    data = dataDict["data"]
    check = dataDict["check"]
    if table != '' and table != None and work != None and work != '':
        
        if table == "rides" and work == "INSERT":
            rideid = 1000
            dbquery = rides.find({})
            count = 0
            for i in dbquery:
                count += 1
            if count == 0:
                rideid = 1000
            else:
                rideid = rides.find_one(sort = [("ride_id", -1)])["ride_id"]
                rideid += 10
            rideid = str(rideid)
            return rideid
        
        elif table == "rides" and work == "GET_RIDES":
            source = int(data["source"])
            destination = int(data["destination"])
            search = {"source" : source, "destination" : destination}
            dbquery = rides.find(search)
            li = []
            found = 0
            # now = datetime.now().strftime("%d-%m-%Y:%S-%M-%H")
            for i in dbquery:
                d = dict()
                d["rideId"] = i["ride_id"]   ##GLOBALLY UNIQUE CHECK
                d["username"] = i["created_by"]
                d["timestamp"] = i["timestamp"]
                if compare_time(i["timestamp"]):
                    li.append(d)
                else:
                    pass
                found = 1
            # print(li)x

            return jsonify(li)

        elif table == "rides" and work == "ALL_DETAILS":
            rideid = data["ride_id"]
            search = {"ride_id" : rideid}
            dbquery = rides.find(search)
            found = 0
            for i in dbquery:
                found += 1
                created_by = i["created_by"]
                users = i["users_rides"]
                timestamp = i["timestamp"]
                source = i["source"]
                destination = i["destination"]
            if (found == 0):
                return Response(None, status = 400, mimetype = 'application/json')
            else:
                retjson = {
                "rideId" : rideid,
                "created_by" : created_by,
                "users" : users,
                "timestamp" : timestamp,
                "source" : source,
                "destination" : destination
            }
            return jsonify(retjson), 200

        elif table == "rides" and work == "JOIN_EXISTING":
            rideid = data["ride_id"]
            search = {"ride_id" : rideid}
            dbquery = rides.find(search)
            ride_exists = 0
            for i in dbquery:
                ride_exists = 1
            if ride_exists == 0:
                return  "10" #rideis doesnot exist
            return  "11" #both exists

        elif table == "rides" and work == "DELETE":
            rideid = data["ride_id"]
            search = {"ride_id" : rideid}
            dbquery = rides.find(search)
            for i in dbquery:
                return "1"
            return "0"
        
    else:
        return {}, 400


@app.route('/api/v1/db/write', methods = ['POST'])
def db_write():
    dataDict = json.loads(request.data)
    table = dataDict["table"]
    work = dataDict["work"]
    data = dataDict["data"]
    if table != '' and table != None and work != None and work != '':

        if table == "rides" and work == "INSERT":
            rideid = data["ride_id"]
            username = data["created_by"]
            timestamp = data["timestamp"]
            source = int(data["source"])
            destination = int(data["destination"])
            rides.insert({"ride_id" : rideid, "created_by" : username, "timestamp" : timestamp, "source" : source, "destination" : destination, "users_rides" : [username]})
            return "Successfully Inserted"

        elif table == "rides" and work == "JOIN_EXISTING":
            rideid = data["ride_id"]
            select = {"ride_id" : rideid}
            dbquery = rides.find(select)
            username = data["username"]
            # found = 0
            for i in dbquery:
                li = i["users_rides"]
                li.append(username)            
            new_value = {"$set" : {"users_rides" : li}}
            rides.update(select, new_value)
            return Response(None, status = 200, mimetype = 'application/json')

        elif table == "rides" and work == "DELETE":
            rideid = data["ride_id"]
            search = {"ride_id" : rideid}
            x = rides.delete_many(search)
            return "Successfully deleted"

    else:
        return "Bad request", 400

@app.route('/api/v1/db/clear', methods = ["POST"])
def db_clear():
    dblist = myclient.list_database_names()
    if "RideShare_rides" in dblist:
        myclient.drop_database('RideShare_rides')
        return {}, 200
    else:
        return {}, 200

### ASSIGNMENT 3 ###


@app.route('/api/v1/_count', methods = ["GET", "DELETE"])
def count_requests():
    if (request.method == "GET"):
        query = {"id" : "counting_accesses"}
        dbquery = count.find(query)
        found = 0
        for i in dbquery:
            value = i["access"]
            found = 1
            break
        if found == 0:
            li = [0]
            return jsonify(li), 200
        else:
            li = [value]
            return jsonify(li), 200

    elif (request.method == "DELETE"):
        query = {"id" : "counting_accesses"}
        dbquery = count.find(query)
        found = 0
        for i in dbquery:
            value = i["access"]
            found = 1
            break
        if found == 0:
            return {}, 200
        else:
            select = {"id" : "counting_accesses"}   
            new_value = {"$set" : {"access" : 0}}
            count.update(select, new_value)
            return {}, 200
        
@app.route('/api/v1/rides/count', methods = ["GET"])
def get_ride_count():
    dbquery = rides.find({})
    num_rides = 0
    count = 0
    for i in dbquery:
        count += 1
    num_rides = count
    li = [num_rides]
    return jsonify(li), 200



if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 8000, debug=True)
