import re
import time
from datetime import datetime
from datetime import timedelta
class check_print_time():
    def __int__(self):

        self.day=0
        self.hour=0
        self.minute=0

        self.start_time_day=0
        self.start_time_hour=0
        self.start_time_minute=0

        self.endtime=0
        self.remain_min=0
        self.pause_time=0
        self.start_time=0
    def print_time(self,file):
        gc=open(file)
        test='Print time:2 days 1 hour 13 minutes'
        r=r"\d{1,2}"
        for line in gc:
            if 'Print time' in line:
                

                time=re.findall(r,line)
                if 'day' in line:
                    self.day=int(time[0])
                    self.hour=int(time[1])
                    self.minute=int(time[2])
                    
                    print('Print time: {} day {}  hour {} minute'.format(self.day,self.hour,self.minute))
                    return self.day,self.hour,self.minute
                    break
                if 'hour' in line:
                    self.hour=int(time[0])
                    self.minute=int(time[1])
                    
                   
                    print('Print time: {}  hour {} minute'.format(self.hour,self.minute))
                    return self.hour,self.minute
                    break
                if 'min' in line:
                    
                    self.minute=int(time[0])
                    
                    print('Print time: {} minute'.format(self.minute))
                    
                    return self.minute
                    break
                    

    def start_time(self):
        
        self.start_time=datetime.now()
        
        return self.start_time

    def end_time(self):

        self.endtime=self.start_time+timedelta(days=self.day,hours=self.hour,minutes=self.minute)

        print((self.endtime))
        

    def remaining_time(self):

        self.remain_min=(self.endtime-datetime.now()).minute

        print(self.remain_min)

        
    def time_pause(self):

        self.pause_time=datetime.now()

        self.remain_min=(self.remain_min-(self.pause_time-self.start_time).minute)

        return  self.remain_min



