import psycopg2
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

pio.renderers.default = 'browser'


conn = psycopg2.connect(database = 'dollar',user = 'postgres' , password = 'sina316' , host = '127.0.0.1' , port = '5432')


cursor = conn.cursor()



cursor.execute('DROP TABLE IF EXISTS prices')


create_tabel = '''CREATE TABLE prices (reopen integer , min_price integer , 
               max_price integer , last_price integer , change integer , change_percentage numeric,
               date TIMESTAMP , persian_date CHAR(10))'''

cursor.execute(create_tabel)


with open('C:\\Users\\Nima\\Desktop\\dollar.csv', 'r') as f:
  
    next(f) #  To Skip the header row.
    cursor.copy_from(f, 'prices', sep=',')

conn.commit()



data = pd.read_sql_query('SELECT * FROM prices',conn).sort_values(by = 'persian_date')



conn.close()


#Plotting data
fig = make_subplots(rows=2,cols = 1 , subplot_titles=('Final daily close values','Daily candlestick chart'))
#Plot Scatter chart
#if you want to see values based on Gregorian calendar change x value from persian_date to "date"
fig.add_trace(go.Scatter(x = data['persian_date'] , y = data['last_price'] , name = 'Final daily close' , mode= 'lines',marker_color='#00B5F7',
                         hovertemplate = 'Price: %{y:$}<extra></extra>') 
              , row =1 , col = 1)

#Plot Candlestick chart
fig.add_trace(go.Candlestick(
          x=data['persian_date'] , 
          open = data['reopen'],
          high = data['max_price'],
          low = data['min_price'],
          close= data['last_price'],
          increasing_line_color = '#00B5F7' , decreasing_line_color = '#FD3216' , name = 'Daily Values candle',
          yhoverformat  = 'open: %{y:$}<extra></extra>' + 'high: %{y:$}' + 'low: %{y:$}'+'close: %{y:$}'),
          row=2 , col=1 )


fig.update_layout(height = 900 , width = 1500)
                  
fig.update_xaxes(rangeslider=  {'visible':False} , row=2 , col =1 )

fig.show()
