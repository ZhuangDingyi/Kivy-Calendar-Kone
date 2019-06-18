#coding:utf-8
# Thanks to:Kuldeep Singh, student at LNMIIT,Jaipur,India
# import Statements
import calendar
import time
import datetime
from kivy import resources
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ListProperty
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.event import EventDispatcher
from kivy.uix.textinput import TextInput
from sklearn.externals import joblib
from kivy.uix.image import Image
import pandas as pd
import numpy as np
from model import Model
from kivy.garden.graph import Graph, MeshLinePlot
from kivy.uix.scrollview import ScrollView
from datetime import  timedelta
# Add source for Chinese characters
resources.resource_add_path("C:\\Windows\\Fonts")
font_name=resources.resource_find('WeiRuanZhengHeiTi-2.ttc')

color_shadow_blue=(.53125,.66796875,.7890625,1)
color_sky_blue=(1/256,158/256,213/256,1)
color_deep_blue=(17/256,64/256,108/256,1)
color_light_blue=(38/256,188/256,213/256,1)
# Builder used to load all the kivy files to be loaded in the main.py file
Builder.load_file('months.kv')
Builder.load_file('dates.kv')
Builder.load_file('select.kv')
Builder.load_file('status.kv')
Builder.load_file('days.kv')
Builder.load_file('calender.kv')

#------Kivy GUI Configuration--
# class for calender.kv file
class Calender(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        # Integrating other classes
        self.select_=Select()
        self.months_=Months()
        self.days_=Days()
        self.dates_=Dates()
        self.status_=Status()
        # Adding layout
        self.layout_1=BoxLayout(size_hint=(1,.1))
        self.layout_1.add_widget(self.select_)

        self.layout_2=BoxLayout()
        self.layout_3=BoxLayout(orientation='vertical')
        self.layout_3.add_widget(self.days_)
        self.layout_3.add_widget(self.dates_)
        self.layout_2.add_widget(self.months_)
        self.layout_2.add_widget(self.layout_3)

        self.layout_4=BoxLayout(size_hint=(1,.1))
        self.layout_4.add_widget(self.status_)

        self.add_widget(self.layout_1)
        self.add_widget(self.layout_2)
        self.add_widget(self.layout_4)                

# ------------------------------------------------------------------------------------------------#
class Content(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.orientation='horizontal'
        
        self.layout_num=BoxLayout(orientation='vertical',size_hint=(1,1))
        self.layout_time=BoxLayout(orientation='vertical',size_hint=(1,1))
        self.layout_action=BoxLayout(orientation='vertical',size_hint=(1,1))

        self.layout_num.add_widget(Label(text='故障电梯编号',font_name=font_name,font_size='20sp'))
        self.layout_time.add_widget(Label(text='故障时间',font_name=font_name,font_size='20sp'))
        self.layout_action.add_widget(Label(text='采取操作',font_name=font_name,font_size='20sp'))

        self.textinput_num=TextInput(multiline=False)
        self.textinput_time=TextInput(multiline=False)
        self.textinput_time.text=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        self.textinput_action=TextInput(multiline=False)

        self.layout_num.add_widget(self.textinput_num)
        self.layout_time.add_widget(self.textinput_time)
        self.layout_action.add_widget(self.textinput_action)

        self.add_widget(self.layout_num)
        self.add_widget(self.layout_time)
        self.add_widget(self.layout_action)

        self.add_widget(Button(text='确认',font_size='20sp',color=(0,0,0,1),font_name=font_name,on_press=self.ct_on_press))

    def ct_on_press(self,event):
        self.app_=App.get_running_app()
        self.model_=self.app_.calendar_.dates_.model_

        self.num=self.textinput_num.text
        self.time=self.textinput_time.text
        self.action=self.textinput_action.text

        elevators=self.model_.samples
        if self.num is not '':
            idx=np.where(elevators['equip_no']==int(self.num))[0]
            body=self.num+'\t'+self.time+'\t'+self.action+'\t'
            if len(idx)>0:

                infos=elevators[['Business type','Description','City','速度','设备型号','T']].iloc[idx[0]]
                for info in infos:
                    body=body+str(info)+'\t'
            body=body+'\n'
            file_name='Log-New-Breakdown.tsv'
            f=open(file_name,'a',encoding="utf-8")
            f.write(body)
            f.close()
            print('成功输入新数据！')
        else:
            pass
        self.textinput_num.text=''
        self.textinput_time.text=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        self.textinput_action.text=''

# class for status.kv file
class Status(BoxLayout,EventDispatcher):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.orientation='horizontal'

        self.add_widget(Button(on_press=self.on_press,text='输入走修数据',font_name=font_name,background_color=color_deep_blue,background_normal='',font_size='20sp',color=(1,1,1,1)))

        
    def on_dismiss(self, arg):
        pass

    def on_press(self,event):
        self.popup = Popup(title='Input Data',
        content = Content(),
        size_hint=(0.8,0.8))
        self.popup.bind(on_dismiss=self.on_dismiss)
        self.popup.open() 
    

        

        
# ------------------------------------------------------------------------------------------------#


# class for Days.kv file
class Days(GridLayout):   
    def __init__(self,**kwargs):
        super().__init__(**kwargs)     
        
        
# ------------------------------------------------------------------------------------------------#


# class for select.kv file
class Select(BoxLayout):
    

    lbl_ = ObjectProperty(None)
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.lbl_.text='通力电梯公司维保可视化产品'
        self.lbl_.font_name=font_name



# class for Reminder in Dates
class Reminder(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.app_=App.get_running_app()
        # Get the dates clicked
        self.model_=self.app_.calendar_.dates_.model_
        # Information to be added
        self.body=self.model_.printSelectedResults()


        # Layout arrangementw
        self.orientation = 'vertical'
        # Elevators information
        self.layout_comp=BoxLayout(orientation = 'horizontal' , size_hint = (1,1))
        self.layout_map=BoxLayout(orientation = 'horizontal' , size_hint = (1,1))
        
        self.img_comp_1=Image(source='component_1.png',keep_ratio=False,size_hint=(1,1),allow_stretch=False,mipmap=True)
        self.img_comp_2=Image(source='component_2.png',keep_ratio=False,size_hint=(1,1),allow_stretch=False,mipmap=True)
        self.layout_comp.add_widget(self.img_comp_1)
        self.layout_comp.add_widget(self.img_comp_2)

        self.img_map_1=Image(source='map_kunshan.png',keep_ratio=False,size_hint=(1,1),allow_stretch=True)
        self.img_map_2=Image(source='map_sh.png',keep_ratio=False,size_hint=(1,1),allow_stretch=True)
        self.layout_map.add_widget(self.img_map_1)
        self.layout_map.add_widget(Label(size_hint=(0.1,1),text='昆\n山\n地\n区\n电\n梯\n分\n布\n图',font_name=font_name,font_size='20sp',color=(0,0,0,1)))
        self.layout_map.add_widget(self.img_map_2)
        self.layout_map.add_widget(Label(size_hint=(0.1,1),text='上\n海\n地\n区\n电\n梯\n分\n布\n图',font_name=font_name,font_size='20sp',color=(0,0,0,1)))

        self.layout_fig=BoxLayout(orientation = 'vertical' , size_hint = (1,0.7))
        #self.layout_fig.add_widget(self.layout_comp)
        self.layout_fig.add_widget(self.layout_map)
        self.add_widget(self.layout_fig)

        #self.layout_scroll_lb=Label(text=self.body,size_hint=(1,None))
        #self.layout_scroll_lb.height=self.layout_scroll_lb.texture_size[1]
        #self.layout_scroll=ScrollableLabel(text=self.body)
        #self.layout_scroll.add_widget(self.layout_scroll_lb)

        #self.layout1_title=Label(text='以下电梯预测将在30天内发生故障：\n'+self.body,font_name=font_name)
        #self.layout1_title.size=self.layout1_title.texture_size
        #self.layout1.add_widget(self.layout1_title)
        #self.layout1.add_widget(self.layout_scroll)
        # Plots
        self.graph_theme = {
            'label_options': {
                'color': (0,0,0,1),  # color of tick labels and titles
                'bold': True},

            'tick_color': (0,0,0,1)}  # ticks and grid

        self.graph=Graph(xlabel='Current time',ylabel='Maintenance date',
x_ticks_major=5, y_ticks_major=5,
y_grid_label=True, x_grid_label=True, padding=5,
x_grid=True, y_grid=True, xmin=-0, xmax=31, ymin=-0, ymax=31,**self.graph_theme)


        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.best_maint_dates=joblib.load('mon_best_int_np.asv')
        self.best_maint_dates=self.best_maint_dates[self.model_.month-1]
        self.plot.points = [(x+1, x+1+self.best_maint_dates[x]) for x in range(len(self.best_maint_dates))]
        self.graph.add_plot(self.plot)

        self.layout_graph=BoxLayout(orientation = 'vertical' , size_hint = (0.7,1))
        self.layout_graph.add_widget(Label(text='本月最优维保日期随时间变化图',font_name=font_name,size_hint=(1,0.1),font_size='16sp',color=(0,0,0,1)))
        self.layout_graph.add_widget(self.graph)

        # Note for user
        self.layout_info=BoxLayout(orientation = 'vertical' , size_hint = (0.3,1))
        self.layout_info.add_widget(Label(text='待预防性维护电梯信息：\n设备编号\n设备所在区域类型\n故障信息\n所在城市\n电梯运行速度\n设备型号\n距离上一次维修天数',font_name=font_name,pos_hint={'x': 0.5, 'center_y': .5},font_size='16sp',color=(0,0,0,1)))


        self.layout_note=BoxLayout(orientation = 'vertical' , size_hint = (0.5,0.8))
        self.layout_note.add_widget(Button(on_press = self.on_press,text='输出\n电梯\n信息',font_name=font_name,pos_hint={'x': .5, 'y': 1},size_hint=(0.4,0.2),font_size='20sp',color=(0,0,0,1),background_color=color_shadow_blue))


        self.layout_graph_note=BoxLayout(orientation = 'horizontal' , size_hint = (1,0.5))
        self.layout_graph_note.add_widget(self.layout_graph)
        self.layout_graph_note.add_widget(self.layout_info)
        self.layout_graph_note.add_widget(self.layout_note)

        self.add_widget(self.layout_graph_note)


        self.layout2 = BoxLayout(orientation = 'horizontal' , size_hint = (1,.15))
        self.add_widget(self.layout2)
        self.layout2.add_widget(Label(text = "请按 'ESC'键或点击窗外以关闭窗口",font_name=font_name,font_size='20sp',color=(1,0,0,1)))
        
    def on_release(self,event):
        print ("Reminder OK Clicked!")
    
    def on_press(self,event):
        file_name='Log-{:}-{:}-{:}.tsv'.format(self.model_.year,self.model_.month,self.model_.day)
        f=open(file_name,'w',encoding="utf-8")
        f.write(self.body)
        f.close()

# ------------------------------------------------------------------------------------------------#
# class for dates.kv file
class Dates(GridLayout):                
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.cols = 7
        self.month_=Months()# In order to get current month and day
        self.model_=Model(year=self.month_.year,month=self.month_.month,day=self.month_.day)
        # Best maintainance date
        self.maintainance_timedelta=datetime.timedelta(days=self.model_.findBestMaintInterval())

        self.best_maint_date=datetime.datetime(self.month_.year,self.month_.month,self.month_.day)
        self.best_maint_date=self.best_maint_date+self.maintainance_timedelta
        print('Best maintenance interval: {:} and best maintenance date: {:}'.format(self.maintainance_timedelta,self.best_maint_date))
        
        # Update dates paddle when choose different months
        self.update_dates(self.month_.year,self.month_.month)
    
    def update_dates(self,year,month):
        print('Update dates!')
        self.clear_widgets()
        c  = calendar.monthcalendar(year,month)
        # Show the best maintenance date if current month is clicked
        if self.best_maint_date.month is month:
            for i in c:
                for j in i:
                    if j == 0:
                        self.add_widget(Button(on_press = self.on_press,on_release=self.on_release,text = '{j}'.format(j=''),font_size='20sp',color=(0,0,0,1)))
                    elif j==self.best_maint_date.day:
                        self.add_widget(Button(on_press = self.on_press,on_release=self.on_release,text = '{j}'.format(j=j),background_color=(1,0,0,1),font_size='20sp',color=(0,0,0,1)))
                    else:
                        self.add_widget(Button(on_press = self.on_press, on_release=self.on_release,text = '{j}'.format(j=j),font_size='20sp',color=(0,0,0,1)))
        else:
            for i in c:
                for j in i:
                    if j == 0:
                        self.add_widget(Button(on_press = self.on_press,on_release=self.on_release,text = '{j}'.format(j=''),font_size='20sp',color=(0,0,0,1)))
                    else:
                        self.add_widget(Button(on_press = self.on_press, on_release=self.on_release,text = '{j}'.format(j=j),font_size='20sp',color=(0,0,0,1)))

    
    def on_dismiss(self, arg):
        # Do something on close of popup
        print('Popup dismiss')
        pass
    
    def on_release(self,event):
        event.background_color = 154/256,226/256,248/256,1
    
    def on_press(self,event):
        print ("date clicked :" + event.text)
        event.background_color = 1,0,0,1
        self.popup = Popup(title='Preventive Maintenance Information',title_color=(0,0,0,1),
        content = Reminder(),
        size_hint=(0.9,0.9),background='background.png')
        self.popup.bind(on_dismiss = self.on_dismiss)
        self.popup.open() 


# ------------------------------------------------------------------------------------------------#

# class for months.kv file
class Months(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        # Displayed time is defined here
        self.now=datetime.datetime.now()
        self.year=2014 # Suppose to be self.now.year but change it into year
        self.month=8
        self.day=1
        # An pointer to current month button
        self.now_btn=Button()
        self.btn_color=(17/256,64/256,108/256,1)


    def month_btn_press(self,instance):
        # Renew previous button
        self.now_btn.background_color=(17/256,64/256,108/256,1)
        instance.background_color=1,0,0,1
        #Update the month of the button
        self.month=self.get_month(instance.text)
        self.now_btn=instance
    
    def month_btn_release(self,instance):
        #instance.background_color=0.1,.5,.5,1
        #instance.bind(on_release= lambda instance : Dates.update_dates())
        app_=App.get_running_app()
        dates_=app_.calendar_.dates_
        dates_.update_dates(self.year,self.month)
        pass

    def get_month(self,month_name):
        month_names=['Null','Jan','Feb','Mar','April','May','June','July','Aug','Sept','Oct','Nov','Dec']
        return month_names.index(month_name)




# ------------------------------------------------------------------------------------------------#


# mainApp class
class mainApp(App):
    time = StringProperty()
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.calendar_=Calender()
        #self.model_=Model() # Place model into Dates()
        self.year=self.calendar_.months_.year
        self.month=self.calendar_.months_.month
        self.day=self.calendar_.months_.day
               
    
    def update(self,*args):
        self.now_real=datetime.datetime.now()
        self.t=datetime.datetime(self.year,self.month,self.day,self.now_real.hour,self.now_real.minute,self.now_real.second)
        self.time=self.t.strftime('%Y-%m-%d %H:%M:%S')
        
    def build(self):
        self.title = "KONE通力电梯可视化产品"
        self.font_name=font_name
        Clock.schedule_interval(self.update,1)       
        return self.calendar_

if __name__ =='__main__':
    app = mainApp()
    app.run()
