# APP CAN BE FOUND AT https://arimatesting.streamlit.app/

## ARIMA Forecasting Test App
In this app, you can copy and paste rows of data from spreadsheets to generate ARIMA forecasts from. You can configure the start period, end period, and complexity of the forecast. Granularity should be set according to the data inputted:
* day     -> season length is a week, separated by 7 days
* week    -> season length is a year, separated by 52 weeks
* month   -> season length is a year, separated by 12 months
* quarter -> season length is a year, separated by 4 quarters
* year    -> season length is a year (no repetitive seasonality captured)

Furthermore, the formatting for the Period markers in each granularity should be as follows:
* day     -> format of %m-%d-%Y ("06-12-2012")
* week    -> format of %m-%d-%Y ("06-12-2012")
* month   -> format of %b-%y ("Jun-12")
* quarter -> custom format of "Q1-2020"
* year    -> format of %Y ("2012")
