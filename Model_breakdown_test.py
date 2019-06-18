#%%
from sklearn.externals import joblib
import pandas as pd
import numpy as np
import calendar
import datetime
from scipy.optimize import fsolve
import sympy as sp

class Model:
    def __init__(self,year=2014,month=5,day=6,label=0):
        # Import date and models
        #print('loading data and models')
        self.c=calendar.Calendar()
        self.svr_model=joblib.load('svr_all.joblib')
        self.samples=pd.read_csv('test_sample6.csv')
        self.start_date=datetime.datetime(2014,1,1)
        
        # Only use data in Shanghai and Kunshan
        # | (self.samples['City']=='北京') | (self.samples['City']=='深圳')
        #self.place=((self.samples['City']=='上海') | (self.samples['City']=='昆山'))
        self.samples=self.samples[self.samples['label']==label]
        self.samples=self.samples.reset_index()

        #self.lifts_unique=pd.unique(self.samples['equip_no'])
        # Filter data according to the dates
        self.year=year
        self.month=month
        self.day=day
        self.now=datetime.datetime(self.year,self.month,self.day)
        print('->model.now:',self.now)
        self.model_start()
    
    def model_start(self):
        self.lr=self.samples['last_repair']
        self.lr_=[]
        for x in self.lr:
            self.lr_.append(self.now) if x is np.nan else self.lr_.append(datetime.datetime.strptime(str(x),'%Y-%m-%d'))

        self.t=[self.now-e for e in self.lr_]
        self.t=np.array([e.days for e in self.t])# Time between last repair time and now

        ## Get predicted failure dates
        self.dates_=[datetime.datetime.strptime(x,'%Y-%m-%d') for x in self.samples['date']]
        self.dates_=np.array(self.dates_)
        self.train_samples=self.samples[['lowbound','median','mean','upbound']]
        #print('Predicting falure intervals')

        self.beta=self.samples[['Action','Business','ContractType','CityLV','TH','MM_Mini','MM_Mono']]
        self.beta=self.beta.as_matrix()

        self.pred_samples=self.svr_model.predict(self.train_samples)# Time to failure

        self.pred_samples=[int(e) for e in self.pred_samples]
        self.delta=[datetime.timedelta(e) for e in self.pred_samples]
        self.dates=self.dates_+self.delta # Here is the predicted time stamps
        self.pred_samples=np.array(self.pred_samples)


        #self.dates_filter=datetime.datetime(self.year,self.month,self.day)+datetime.timedelta(days=30) # # Filter the predicted failure within this month and next month
        c=calendar.Calendar()
        max_dates=[e for e in c.itermonthdays(self.year,self.month)]
        self.max_dates=np.max(max_dates)
        #self.dates_filter=datetime.datetime(self.year,self.month,self.max_dates)
        self.dates_filter=datetime.datetime(self.year,11,4)
        #print('->model.dates_filter:{:}'.format(self.dates_filter))

        # Variables for optimization
        self.dt=sp.symbols('dt',real=True,positive=True)

        # Final output for GUI
        self.index=((self.dates>=self.now) & (self.dates<=self.dates_filter) )
        self.index=np.where(self.index)[0]
        
        
        # Consider the condition for the elevators instead of records
        self.pred_uniq=self.samples['equip_no'][self.index]
        self.pred_uniq_idx=[np.where(self.pred_uniq==e)[0][-1] for e in self.pred_uniq]
        self.index_unique=pd.unique(self.index[self.pred_uniq_idx])
        self.pred_dates_selected=self.dates[self.index_unique]
        #print('->Number of model.pred_dates_selected:',np.count_nonzero(self.pred_dates_selected))
        #print('Initialization finished')
        #self.pred_{:}_selected=self.{:}[self.index]
    def add_breakdowns(self,breakdown_number):
        # Adding records to self.samples
        # What if breakdowns happens today?
        self.breakdowns=pd.DataFrame([],columns=self.samples.columns)
        for lift in self.lifts_unique[:breakdown_number]:
            idx=np.where(samples['equip_no']==lift)[0][-1]
            infos=self.samples.iloc[idx]
            infos['T']=self.t[idx]
            infos['next_repair']=0
            infos['last_repair']=infos['date']
            infos['TH']+=1
            infos['date']=datetime.datetime(self.now.year,self.now.month-2,self.now.day,0,0,0).strftime('%Y-%m-%d %H:%M:%S')
            self.breakdowns=self.breakdowns.append(infos,ignore_index=True)
        self.samples=self.samples.append(self.breakdowns,ignore_index=True)
        print('Add breakdowns finished!')
        self.model_start()
        print('Model refreshed!')

        

    
    def printSelectedResults(self):
        # This function returns strings to be shown in Reminder Popup
        title='Number\t Last_Repair_Days\t Business_Type\t Description\t City\t Speed\t Equipment_Type\t Predicted_Failure_Days\n'
        body=''
        test_idx=slice(10) #Used for test label widget could not hold all the outputs
        #print('***',self.index)
        '''
        num=self.samples['equip_no'][self.index]
        lrt=self.samples['last_repair'][self.index]
        bstype=self.samples['Business type'][self.index]
        desc=self.samples['Description'][self.index]
        city=self.samples['City'][self.index]
        speed=self.samples['速度'][self.index]
        eqtype=self.samples['设备型号'][self.index]
        '''
        num=self.samples['equip_no'][self.index][test_idx]
        lrt=self.t[self.index][test_idx]
        bstype=self.samples['Business type'][self.index][test_idx]
        desc=self.samples['Description'][self.index][test_idx]
        city=self.samples['City'][self.index][test_idx]
        speed=self.samples['速度'][self.index][test_idx]
        eqtype=self.samples['设备型号'][self.index][test_idx]
        next_rep=self.samples['T'][self.index][test_idx]

        conts=zip(num,lrt,bstype,desc,city,speed,eqtype,next_rep)
        for cont in conts:
            for item in cont:
                body=body+str(item)+' '*5
            body=body+'\n'
        return title+body
    
    def surviveFuncCum(self,dt,t,beta):
        # Weibull cox function, haven't got information of beta
        #print('beta in surviveFuncCum:',beta)
        return np.exp(-0.091*beta[0]+0.015*beta[1]+0.049*beta[2]+0.109*beta[3]+0.051*beta[4]+0.121*beta[5]-0.136*beta[6])*((t+dt)/111.634)**0.651
    
    def costFunc(self,dt,T,t,beta):
        Cp=400
        Cf=800
        #print('***surviveFuncCum results:',self.surviveFuncCum(dt=dt,t=t,beta=beta))
        if T>t:
            return (Cp*((T-t)/dt)+Cf*self.surviveFuncCum(dt=dt,t=t,beta=beta))/(T-t)
        else:
            return (Cp+Cf*self.surviveFuncCum(dt=dt,t=t,beta=beta))/T

    def findBestMaintInterval(self):
        # Function that find the best maintenance date based on selected predicted results
        # For each station
        self.Ct_without=[(2*400+1600**self.surviveFuncCum(dt=self.dt,t=self.t[e],beta=self.beta[e]))/30 for e in self.index_unique]
        self.Ct_without_mean=np.mean(self.Ct_without)
        self.Ct_without_mean_lambda=sp.lambdify(self.dt,self.Ct_without_mean,'numpy')
        self.Ct_without_res=self.Ct_without_mean_lambda(15)

        self.Ct_single=[self.costFunc(dt=self.dt,T=self.pred_samples[e],t=self.t[e],beta=self.beta[e]) for e in self.index_unique]

        self.Ct=np.mean(self.Ct_single)
        self.Ct_diff=sp.diff(self.Ct)
        self.Ct_lambda=sp.lambdify(self.dt,self.Ct,'numpy')


        self.Ct_diff_lambda=sp.lambdify(self.dt,self.Ct_diff,'numpy')

        self.res=[]
        for i in range(self.max_dates):
            #print(self.Ct_lambda(i))
            self.res.append(self.Ct_lambda(i)) if self.Ct_lambda(i) is not np.nan else self.res.append(-1)
        self.res=np.array(self.res)
        if len(self.res[self.res>0])>0:
            print('->Maintenance interval:',np.where(self.res==np.min(self.res[self.res>0])),' days with money',np.min(self.res[self.res>0]))
            #for test
            #print('->model.Ct',self.Ct)
            #print('->model.Ct_diff:',self.Ct_diff)
            #print('->model.fsolve result:',fsolve(self.Ct_diff_lambda,15))
            return int(np.where(self.res==np.min(self.res[self.res>0]))[0])
        else:
            return 0

#%%
model=Model(year=2014,month=8,day=2,label=0)
model.findBestMaintInterval()
#%%
# 时间间隔随着故障次数变化图
from matplotlib import pyplot as plt
fig, ax = plt.subplots()
x_ticks=[]
for lab in range(0,6):
    model=Model(year=2014,month=10,day=4,label=lab)
    ax.bar(lab,np.mean(model.pred_samples))
    x_ticks.append(len(model.samples))
ax.set_xticks(range(0,6))
ax.set_xticklabels(x_ticks)
#%%
# 生存函数随着故障次数变化图
fig, ax = plt.subplots()
x_ticks=[]
for lab in range(0,6):
    model=Model(year=2014,month=10,day=30,label=lab)
    ax.bar(lab,np.mean([model.surviveFuncCum(dt=0,t=model.t[e],beta=model.beta[e]) for e in model.index]))
    x_ticks.append(len(model.samples))
ax.set_xticks(range(0,6))
ax.set_xticklabels(x_ticks)
#%%
#最优维保日期随着故障次数变化图
fig, ax = plt.subplots()
x_ticks=[]
for lab in range(0,6):
    model=Model(year=2014,month=10,day=2,label=lab)
    ax.bar(lab,2+model.findBestMaintInterval())
    x_ticks.append(len(model.samples))
ax.set_xticks(range(0,6))
ax.set_xticklabels(x_ticks)
#%%
a=model.Ct_lambda
a(1)

#%%
for i in range(2,10):
    model=Model(year=2014,month=5,day=i)
    model.findBestMaintInterval()
#%%
from matplotlib import pyplot as plt
x=np.linspace(0,50,1000)
plt.plot(x,a(x))
#%%
dt=sp.symbols('dt',real=True,positive=True)
#ctt=6.1221930834716*dt**0.652 + 2.43033432473495*(0.00895784438432736*dt - 0.0985362882276009)**0.652 + 2.12129940982935*(0.00895784438432736*dt - 0.0716627550746188)**0.652 
ctt=(0.00895784438432736*dt - 0.0985362882276009)**0.652
ctt_lam=sp.lambdify(dt,ctt)

print(ctt_lam(1))
#%%
model.surviveFuncCum(model.dt,model.t,model.beta)

#%%
c=calendar.Calendar()
mons_best_int=[]
mons_Ct_lam=[] 
for i in range(1,13):
    days=[]
    ct=[]
    for j in c.itermonthdays(2014,i):
        if j != 0:
            model=Model(year=2014,month=i,day=j)
            days.append(model.findBestMaintInterval())
            ct.append(model.Ct_lambda)
        else:
            pass

    mons_best_int.append(days)
    mons_Ct_lam.append(ct)
#joblib.dump(mons_best_int,'mons_best_int.asv')
#joblib.dump(mons_Ct_lam,'mons_Ct_lam.asv')
#%%
# 画不同时间维保图
mon_cnt=1
plt.rcParams['axes.facecolor'] = 'white'
fig,ax=plt.subplots(1,1,figsize=(8,6))

for mon in mons_best_int:
    ax.plot(mon,label=str(mon_cnt))
    mon_cnt+=1
plt.legend()
plt.xlabel('日期')
plt.savefig('最优维保间隔优化结果图.png')
#%%
# 如果有新的故障怎么办


#%%
3 4  5  6  7  8  9  10 11 12
9 15 12 20 15 17 17 14 20 11

3 4 5 7 10 11
6 8 9 11