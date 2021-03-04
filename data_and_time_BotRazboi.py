import datetime
dt = datetime.datetime.strptime('20170124T1815', '%Y%m%dT%H%M%S')

ut = dt.timestamp()

now_time = str(datetime.datetime.now())

print(now_time)

