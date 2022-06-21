
import psycopg2
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import time
from sqlalchemy import create_engine


pio.renderers.default = 'browser'
url = r'https://www.tgju.org/profile/price_eur/history'
name_table = 'prices'

class kilid():
    
    
    def __init__(self,database , username , password ):
        self.database = database
        self.username = username
        self.password = password


    def connect_sql(self):

        conn_string = f'postgresql://{self.username}:{self.password}@localhost:5432/{self.database}'
        try:
            print('Connecting to Database...')
            conn = create_engine(conn_string,echo=True).connect()
            print('Connecting Succesful')
            return conn
        except:
            print('Connecting Failed')
        
    
    def create_table(self,conn,data):

        conn.execute(f'DROP TABLE IF EXISTS %s'%(name_table))

        data.to_sql(name_table,con=conn ,if_exists = 'replace',index = False)

        return 

    def retrive_data(self,conn,query):
        
        price_data= []
        results = conn.execute(query)
        for item in results:
            price_data.append(item)
        
        df = pd.DataFrame(price_data)
        df.set_index('date',inplace = True)

        return df

    def crawl(self,url,chromedrive_path):

        chrome_options = Options()
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        driver = webdriver.Chrome(executable_path= chromedrive_path, options=chrome_options)
        driver.get(url)
        
        results = []
        
        try:
            for _ in range(10):
                time.sleep(5)
                soup = bs(driver.page_source,parser = 'html.parser')
                for tr in soup.find_all('tr')[1:]:
                    tds = tr.find_all('td')
                    results.append([i.text.strip() for i in tds])
                
                time.sleep(5)
                element_presence = EC.presence_of_element_located((By.CLASS_NAME , "paginate_button.next"))
                button=WebDriverWait(driver,5).until(element_presence)
                button.click()
                
        except:
            driver.quit()
        
        df = pd.DataFrame(results,columns = ['open','min_price','max_price','close','change','change-pct','date','persian_date']) 
        df['open'] = df['open'].str.replace(',','')
        df['min_price'] = df['min_price'].str.replace(',','').astype('float32')
        df['max_price'] = df['max_price'].str.replace(',','').astype('float32')
        df['close'] = df['close'].str.replace(',','').astype('float32')
        df['date'] = pd.to_datetime(df['date'])
        

        driver.quit()
        return df

    
    def plotting(self,data):
        
        #Plotting data
        fig = make_subplots(rows=2,cols = 1 , subplot_titles=('Final daily close values','Daily candlestick chart'))
        #Plot Scatter chart
        #if you want to see values based on Gregorian calendar change x value from persian_date to "date"
        fig.add_trace(go.Scatter(x = data.index, y = data['close'] , name = 'Final daily close' , mode= 'lines',marker_color='#00B5F7',
                                 hovertemplate = 'Price: %{y:$}<extra></extra>') 
                      , row =1 , col = 1)
        
        #Plot Candlestick chart
        fig.add_trace(go.Candlestick(
                  x=data.index , 
                  open = data['open'],
                  high = data['max_price'],
                  low = data['min_price'],
                  close= data['close'],
                  increasing_line_color = '#00B5F7' , decreasing_line_color = '#FD3216' , name = 'Daily Values candle',
                  yhoverformat  = 'open: %{y:$}<extra></extra>' + 'high: %{y:$}' + 'low: %{y:$}'+'close: %{y:$}'),
                  row=2 , col=1 )
        
        
        fig.update_layout(height = 1200 , width = 1500)
                          
        fig.update_xaxes(rangeslider=  {'visible':False} , row=2 , col =1 )
        
        fig.show()


db=kilid('database','user','password')
conn = db.connect_sql()
data = db.crawl(url,chromedrive_path=r'\chromedriver')
table = db.create_table(conn,data)
retrived_data = db.retrive_data(conn,r'query')
db.plotting(retrived_data)
