from flask.globals import session
from .Database import Database


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

    @staticmethod
    def create_event(sessionID, deviceID, value, date):
        sql = "INSERT INTO deviceData (sessionID, deviceID, value, date) VALUES (%s, %s, %s, %s);"
        params = [sessionID, deviceID, value, date]
        return Database.execute_sql(sql, params)
    
    @staticmethod
    def read_voltage(session):
        sql = "select DATE_FORMAT(dd.date, '%Y-%m-%dT%H:%i:%SZ') as Date, dd.value, d.Name, d.measurement from deviceData dd join device d on dd.deviceID = d.deviceID where d.deviceID = 4 and sessionID = %s and dd.value > 30 and month(dd.date) = 5 and day(dd.date) = 26 order by dd.date"
        params = [session]
        return Database.get_rows(sql, params)

    @staticmethod
    def read_current_voltage():
        sql = "select DATE_FORMAT(dd.date, '%Y-%m-%dT%H:%i:%SZ') as Date, dd.value from deviceData dd where dd.deviceID = 4 order by dd.date desc limit 1"
        return Database.get_rows(sql)

    @staticmethod
    def read_basic_stats():
        sql = "select max(s.maxSpeed) as maxSpeed, avg(s.avgSpeed) as avgSpeed, sum(s.distance) as distance, count(s.sessionID) as amount from session s"
        return Database.get_rows(sql)

    @staticmethod
    def read_last_gps():
        sql = "select deviceID, value from deviceData where deviceID = 1 or deviceID = 2 order by date desc limit 2"
        return Database.get_rows(sql)
    
    @staticmethod
    def read_last_sessionid():
        sql = "select sessionID from session order by sessionID desc limit 1"
        return Database.get_rows(sql)
    
    @staticmethod
    def create_session(UserID, startDate):
        sql = "INSERT INTO session (UserID, startDate) VALUES (%s, %s)"
        params = [UserID, startDate]
        return Database.execute_sql(sql, params)

    @staticmethod
    def update_session(endDate, maxSpeed, avgSpeed, distance, sessionID):
        sql = "UPDATE session SET endDate = %s, maxSpeed = %s, avgSpeed = %s, distance = %s WHERE sessionID = %s"
        params = [endDate, maxSpeed, avgSpeed, distance, sessionID]
        print(sql)
        return Database.execute_sql(sql, params)
    
    @staticmethod
    def read_ride(id):
        sql = "select DATE_FORMAT(startDate, '%W, %d %M %Y %H:%i:%S') as startDate, maxSpeed, avgSpeed, distance, description, deviceID, value, DATE_FORMAT(date, '%Y-%m-%dT%H:%i:%SZ') as date, s.sessionID, s.description  from session s join deviceData d on s.sessionID = d.sessionID where d.sessionID = %s"
        params = [id]
        return Database.get_rows(sql, params)

    @staticmethod
    def read_all_rides():
        sql = "select sessionID, DATE_FORMAT(startDate, '%W, %d %M %Y') as startDate from session order by sessionID desc"
        return Database.get_rows(sql)
    
    @staticmethod
    def read_get_last(id):
        sql = "select * from deviceData where sessionID = %s and (deviceID = 1 or deviceID = 2) order by date desc limit 2"
        params = [id]
        return Database.get_rows(sql, params)
    
    @staticmethod
    def read_get_first(id):
        sql = "select * from deviceData where sessionID = %s and (deviceID = 1 or deviceID = 2) order by date asc limit 2"
        params = [id]
        return Database.get_rows(sql, params)
    
    @staticmethod
    def read_speed(id):
        sql = "select max(value)/100*40 as max, avg(value)/100*40 as avg from deviceData where sessionID = %s and deviceID = 5 group by deviceID"
        params = [id]
        return Database.get_rows(sql, params)