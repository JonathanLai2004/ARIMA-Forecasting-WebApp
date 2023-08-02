# Libraries for function
import pandas as pd
import pmdarima as pm

# Libraries for streamlit app
import streamlit as st
import time
import plotly.graph_objects as go

############ Data import and settings ############
# In the Quantegy app, these settings will be    #
# pulled to populate default arguments of the    #
# function.                                      #
#                                                #
# In this streamlit app, they are only here as   #
# a placeholder                                  #
snapshot_values = [0]                            #
model_settings = {                               #
"model_setting": {'time_period_labels':['Jan-20', 'Feb-20', 'Mar-20', 'Apr-20', 'May-20', 'Jun-20', 'Jul-20', 'Aug-20', 'Sep-20', 'Oct-20', 'Nov-20', 'Dec-20'], 'forecast_start': 'Jul-20', 'time_granularity': 'Month', 'time_period_labels_agg_quarter': ['Jan-20', 'Apr-20', 'Jul-20', 'Oct-20'], 'time_period_labels_agg_year': ['2020']},
"header_data": "['id', 'Parameter', 'Format', 'Scenario', 'Source', 'Dependencies', 'Formula', 'Jan-20', 'Feb-20', 'Mar-20', 'Apr-20', 'May-20', 'Jun-20', 'Jul-20', 'Aug-20', 'Sep-20', 'Oct-20', 'Nov-20', 'Dec-20']",
"time_granularity": "month",                     #
"number_of_period": "12",                        #
"start_date": "Wed Jan 01 2020",                 #
"start_forecasts": "Jul-20"}                     #                       #
##################################################

############ Function to create a table of forecasted values using ARIMA ############

def forecast(end_period = len(model_settings["model_setting"]['time_period_labels'])-1,   # user-configurable, int input (5)
             start_period = model_settings["model_setting"]['time_period_labels'].index(model_settings["start_forecasts"]),  # user-configurable, int input (10)
             complexity = "default",                                                      # user-configurable, options   ('medium')
             data = snapshot_values,                                                      # import list input            ([2,4,8,4,8,16])
             granularity = model_settings["time_granularity"],                            # import string input          ('month')
             data_start = model_settings["model_setting"]['time_period_labels'][0]):      # import string input          ('Jun-12)
    
    ###### Creating two main components of the output as separate lists
    
    dates_of_forecast_values = []
    forecast_values = []
    
    ###### Creating formatted dates for the result table (uses end_period, start_period, data_start)
    
    if granularity == "day":                                    # format of %m-%d-%Y ("06-12-2012")
        seasonality_length = 7
        data_start = pd.to_datetime(data_start)                   
        for period in range(start_period,end_period+1):
            new_date_obj = data_start + pd.DateOffset(days=period)
            new_date_str = new_date_obj.strftime("%m-%d-%Y")
            dates_of_forecast_values.append(new_date_str)
    if granularity == "week":                                    # format of %m-%d-%Y ("06-12-2012")
        seasonality_length = 52
        data_start = pd.to_datetime(data_start)
        for period in range(start_period,end_period+1):
            new_date_obj = data_start + pd.DateOffset(weeks=period)
            new_date_str = new_date_obj.strftime("%m-%d-%Y")
            dates_of_forecast_values.append(new_date_str)
    if granularity == "month":                                   # format of %b-%y ("Jun-12")
        seasonality_length = 12
        data_start = pd.to_datetime(data_start, format="%b-%y")
        data_start_month_year = data_start.strftime("%b-%y")
        for period in range(start_period, end_period+1):      
            dates_of_forecast_values.append((data_start + pd.DateOffset(months=period)).strftime("%b-%y"))
    if granularity == "quarter":                                 # custom format of "Q1-2020"
        seasonality_length = 4
        quarter, year = data_start.split("-")
        year = int(year)
        quarter_to_month = {
            "Q1": 1,
            "Q2": 4,
            "Q3": 7,
            "Q4": 10
        }
        start_month = quarter_to_month[quarter]
        start_date = pd.to_datetime(f"{start_month}-01-{year}", format="%m-%d-%Y")
        for period in range(start_period,end_period+1):
            new_date_obj = start_date + pd.DateOffset(months=period * 3)
            new_quarter = (new_date_obj.month - 1) // 3 + 1
            new_quarter_year_str = f"Q{new_quarter}-{new_date_obj.year}"
            dates_of_forecast_values.append(new_quarter_year_str)
    if granularity == "year":                                     # format of %Y ("2012")
        seasonality_length = 1
        data_start = pd.to_datetime(data_start, format="%Y")
        data_start_year = data_start.year
        for period in range(start_period, end_period+1):      
            dates_of_forecast_values.append(data_start_year + period)
    
    ###### Complexity and order settings for auto_arima (uses complexity)
    
    if complexity == "default":
        start_p = 2
        max_p = 5
        max_order = 5
        D = None
    elif complexity == "low":
        start_p = 1
        max_p = 3
        max_order = 4
        D = 0
    elif complexity == "medium":
        start_p = 3
        max_p = 6
        max_order = 7
        D = 1
    elif complexity == "high":
        start_p = 6
        max_p = 9
        max_order = 10
        D = 2
    
    ###### ARIMA modeling
    
    # set training data
    training_data = data[:start_period]
    
    # determine best p,d,q ARIMA order values using pmdarima
    arima_model = pm.auto_arima(training_data, m = seasonality_length, start_p = start_p, max_p = max_p, max_order = max_order, D = D)
    
    # fit the model on the data
    arima_model.fit(training_data)
    
    # forecast the values for the specified periods
    forecast_values = arima_model.predict(n_periods = end_period - start_period + 1)
    
    ###### Combine the two into a pandas table with both the period labels and predicted values
    
    forecast_table = {
    'Period': dates_of_forecast_values,
    'Predicted': forecast_values
    }

    forecast_table = pd.DataFrame(forecast_table)
    
    return(forecast_table)

############ Create a streamlit app to test the function ############

# Title of the webpage
st.title("ARIMA Forecast Testing Dashboard")
st.divider()

col1, col2 = st.columns(2)

# Add content to the first column
with col1:
    ###### Data input section
    st.subheader("Import Data")
    st.markdown("*Copy and Paste columns of data below. First column should be Period markers, second column the values.*")
    
    input_table = pd.DataFrame(
        [
        {"Period": "01-01-2020", "snapshot_values": 1},
        {"Period": "Jan-20", "snapshot_values": 1},
        {"Period": "Q1-2020", "snapshot_values": 1},
        {"Period": "2020", "snapshot_values": 1},
    ]
    )
    edited_table = st.data_editor(input_table, num_rows="dynamic")

    snapshot_values = edited_table["snapshot_values"].tolist()
    Periods = edited_table["Period"].tolist()

# Add content to the second column
with col2:
    # Subtitle for Forecast Configuration settings
    st.subheader("Forecast Settings")

    ###### Input elements for the various parameters
    start_period = st.number_input("Start Period (as an index)", value=0, step=1)
    end_period = st.number_input("End Period (as an index)", value=0, step=1)

    complexity_options = ["default", "low", "medium", "high"]
    complexity = st.selectbox("Complexity", complexity_options)

    granularity_options = ["day", "week", "month", "quarter", "year"]
    granularity = st.selectbox("Granularity", granularity_options)

    data_start = edited_table.iloc[0]["Period"]

st.write("")
st.write("")
st.markdown("""Be sure to delete any empty rows before running the forecast by selecting rows and pressing "delete".
            Day-to-day data should have at least 7 rows, weekly data at least 52 rows, monthly data at least 12 rows, 
            quarterly data at least 4 rows, and yearly data at least 2 rows.""")

st.markdown("If you run into unexpected errors while forecasting, try changing start period or complexity settings.")

st.divider()

# Run the forecast when the "Run" button is clicked
if st.button("Run"):
    if snapshot_values and complexity and granularity and data_start and start_period and end_period:
        if (granularity == "day" and len(snapshot_values) >= 7) or (granularity == "week" and len(snapshot_values) >= 52) or (granularity == "month" and len(snapshot_values) >= 12) or (granularity == "quarter" and len(snapshot_values) >= 4) or (granularity == "year" and len(snapshot_values) >= 2):
            data = snapshot_values
            start_time = time.time()
            result = forecast(start_period=start_period,
                            end_period=end_period,
                            complexity=complexity,
                            data=data,
                            granularity=granularity,
                            data_start=data_start)
            end_time = time.time()
            execution_time = end_time - start_time

            # Display execution time
            st.write(f"Execution Time: {execution_time:.4f} seconds")

            # Merge historical data and forecasted data on the "Period" column
            if granularity != "year":
                merged_data = pd.merge(edited_table, result, on="Period", how="outer")
            if granularity == "year":
                merged_data = pd.concat([edited_table, result], axis=0)

            # Plot the line chart using Plotly

            fig = go.Figure()

            fig.add_trace(go.Scatter(x=merged_data["Period"], y=merged_data["snapshot_values"],
                                    mode='lines', name='Historical Data'))

            fig.add_trace(go.Scatter(x=merged_data["Period"], y=merged_data["Predicted"],
                                    mode='lines', name='Forecasted Data'))

            fig.update_layout(title=f'{granularity.capitalize()}ly data, {complexity.capitalize()} complexity',
                            xaxis_title='Period', yaxis_title='Quantity')

            st.plotly_chart(fig)

            # Display the table of forecasted values
            st.subheader("Historical and Forecasted Values")
            st.dataframe(merged_data)
            
        else:
            st.error("Not enough data points to forecast.")

    else:
        st.error("Please provide all the required inputs.")
