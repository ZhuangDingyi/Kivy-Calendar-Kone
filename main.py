#coding:utf-8
# Thanks to:Kuldeep Singh, student at LNMIIT,Jaipur,India
# import Statements
import calendar
import time
import datetime
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
import numpy as np 
#import pandas as pd 
from math import sin
from kivy.garden.graph import Graph, MeshLinePlot

# Builder used to load all the kivy files to be loaded in the main.py file
Builder.load_file('months.kv')
Builder.load_file('dates.kv')
Builder.load_file('select.kv')
Builder.load_file('status.kv')
Builder.load_file('days.kv')

# class for calender.kv file
class Calender(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        

        

# ------------------------------------------------------------------------------------------------#


# class for status.kv file
class Status(BoxLayout,EventDispatcher):
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        
        
        
        
# ------------------------------------------------------------------------------------------------#


# class for select.kv file
class Select(BoxLayout):
    

    lbl_ = ObjectProperty(None)
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)



# ------------------------------------------------------------------------------------------------#


# class for Reminder in Dates
class Reminder(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        # Elevators information
        self.a=BoxLayout(orientation = 'horizontal' , size_hint = (1,.5))
        self.add_widget(self.a)
        self.a.add_widget(Label(text='Elevators were dangeroues in next 5 days! \n Number    RepairFrequency \n 30146560    10\n 30146563    3'))
        # Plots

        self.graph=Graph(xlabel='X',ylabel='Y',x_ticks_minor=5,
x_ticks_major=25, y_ticks_major=1,
y_grid_label=True, x_grid_label=True, padding=5,
x_grid=True, y_grid=True, xmin=-0, xmax=100, ymin=0, ymax=10)
        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.plot.points = [(x, 10*np.exp(-x / 10.)) for x in range(0, 101)]
        self.graph.add_plot(self.plot)
        self.t=BoxLayout(orientation = 'horizontal' , size_hint = (1,.1))
        self.t.add_widget(Label(text='Survival Curve'))
        self.add_widget(self.t)
        self.add_widget(self.graph)
        # Note for user

        self.b = BoxLayout(orientation = 'horizontal' , size_hint = (1,.15))
        self.add_widget(self.b)
        self.b.add_widget(Label(text = "Press 'ESC' or Click Outside The Window To Close"))
        
    def on_release(self,event):
        print ("Reminder OK Clicked!")

# ------------------------------------------------------------------------------------------------#
# class for dates.kv file
class Dates(GridLayout):
    now = datetime.datetime.now()
    
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.cols = 7
        self.c  = calendar.monthcalendar(2015,5)
        for i in self.c:
            for j in i:
                if j == 0:
                    self.add_widget(Button(on_release = self.on_release,text = '{j}'.format(j='')))
                else:
                    self.add_widget(Button(on_release = self.on_release, text = '{j}'.format(j=j)))
        
    def get_month(self):
        pass
    
    def on_dismiss(self, arg):
        # Do something on close of popup
        print('Popup dismiss')
        pass
    
    def on_release(self,event):
        print ("date clicked :" + event.text)
        event.background_color = 1,0,0,1
        self.popup = Popup(title='Information of Preventive Maintenance',
        content = Reminder(),
        size_hint=(None, None), size=(self.width*3/4, self.height))
        self.popup.bind(on_dismiss = self.on_dismiss)
        self.popup.open() 


# ------------------------------------------------------------------------------------------------#

# class for months.kv file
class Months(BoxLayout):
    def __init__(self,**kwargs):
        super(Months,self).__init__(**kwargs)


# ------------------------------------------------------------------------------------------------#


# mainApp class
class mainApp(App):
    time = StringProperty()
    
    def update(self,*args):
        self.time = str(time.asctime())
        
    def build(self):
        self.title = "KONE Visulization Product"
        self.load_kv('calender.kv')
        Clock.schedule_interval(self.update,1)
        return Calender()

# BoilerPlate
if __name__ =='__main__':
    app = mainApp()
    app.run()