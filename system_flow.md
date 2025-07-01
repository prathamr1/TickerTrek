# TickerTrek
___
### Main Streamlit app (entry point)

├── app.py   
### Dependencies
├── requirements.txt           
 
***

### Configuration and constants
├── config/
│   ── __init__.py
│   ── settings.py           

***

### Stock data fetching and processing
├── data/
│   ├── __init__.py
│   ├── stock_data.py

### Data caching utilities
│   └── cache_manager.py      

***

### Analytics and Indicators
├── analysis/
│   ├── __init__.py
│   ├── technical_indicators.py
### Statistical calculations
│   ├── statistics.py   
### Financial metrics calculations
│   └── metrics.py           	   

***

### Chart creation functions
├── visualization/
│   ├── __init__.py
│   ├── charts.py            
│   ├── plotly_charts.py    
│   └── styling.py           

***

### Sidebar components
├── components/
│   ├── __init__.py
│   ├── sidebar.py           
│   ├── metrics_display.py   
### Data table components
│   └── data_table.py        

***
### Helper functions and Validation
├── utils/
│   ├── __init__.py
│   ├── helpers.py           
│   └── validators.py        

***
***

└── tests/
    ├── __init__.py
    ├── test_data.py
    ├── test_analysis.py
    └── test_components.py