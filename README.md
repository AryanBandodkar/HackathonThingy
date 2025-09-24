# 🌊 FloatChat - Oceanographic Data AI Assistant

FloatChat is an AI-powered chatbot that can analyze oceanographic data stored in a SQLite database. It provides natural language querying capabilities and interactive visualizations for oceanographic profiles.

## Features

- 🤖 **AI Chatbot**: Natural language interface for querying oceanographic data
- 🗺️ **Interactive Maps**: Visualize data points on interactive maps using Folium
- 📊 **Data Visualizations**: Temperature and salinity distribution plots using Plotly
- 💬 **Conversational Interface**: Chat-based interaction with conversation history
- 🔍 **Smart Query Generation**: Automatically generates SQL queries from natural language
- 📈 **Real-time Analytics**: Live database statistics and summaries

## Data Structure

The application works with oceanographic profile data containing:
- **Location**: Latitude and longitude coordinates
- **Temperature**: Water temperature measurements
- **Salinity**: Salinity measurements (PSU)
- **Pressure**: Pressure measurements (dbar)
- **Profile Information**: Profile numbers, levels, and source files

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd FloatChat
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python run_app.py
   ```

The application will:
- Install any missing dependencies
- Set up the SQLite database with sample data
- Launch the Streamlit web interface

## Usage

### Starting the Application

Run the main launcher:
```bash
python run_app.py
```

Or run the Streamlit app directly:
```bash
streamlit run frontend/streamlit_app.py
```

### Using the Chatbot

1. **Open your browser** to `http://localhost:8501`
2. **Ask questions** in natural language, such as:
   - "Show me a summary of the data"
   - "Find profiles with temperature above 15 degrees"
   - "What's the salinity range?"
   - "Show me locations with high pressure"
   - "How many profiles are there?"

3. **View visualizations**:
   - Interactive maps showing data locations
   - Temperature distribution plots
   - Salinity distribution plots

### Sample Queries

- **Data Summary**: "Show me a summary of the data"
- **Temperature Queries**: "Find profiles with temperature above 15 degrees"
- **Salinity Queries**: "What's the salinity range?"
- **Location Queries**: "Show me profiles near latitude 40 degrees"
- **Pressure Queries**: "Find profiles with pressure below 100 dbar"
- **Range Queries**: "What's the temperature range?"

## Architecture

### Backend Components

- **`database_manager.py`**: Handles SQLite database operations
- **`ai_chatbot.py`**: AI chatbot logic and query generation
- **`app.py`**: Background scheduler and ETL pipeline

### Frontend Components

- **`streamlit_app.py`**: Main Streamlit web application
- **Interactive visualizations**: Maps, charts, and plots
- **Chat interface**: Conversational UI with message history

### Database Schema

```sql
CREATE TABLE profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    N_PROF INTEGER,
    N_LEVELS INTEGER,
    JULD REAL,
    LATITUDE REAL,
    LONGITUDE REAL,
    PRES REAL,
    TEMP REAL,
    PSAL REAL,
    PRES_ADJUSTED REAL,
    TEMP_ADJUSTED REAL,
    PSAL_ADJUSTED REAL,
    SOURCE_FILE TEXT
);
```

## AI Chatbot Features

### Intent Recognition
The chatbot recognizes various intents:
- Data summary requests
- Temperature queries
- Salinity queries
- Location queries
- Pressure queries
- Range queries
- Visualization requests

### Query Generation
- Automatically generates SQL queries from natural language
- Handles comparison operators (>, <, =)
- Supports numerical value extraction
- Generates appropriate WHERE clauses and ORDER BY statements

### Response Generation
- Human-readable responses with emojis and formatting
- Data summaries with key statistics
- Tabular data presentation
- Error handling and user guidance

## Visualization Features

### Interactive Maps
- Folium-based interactive maps
- Color-coded markers by temperature
- Hover information for each data point
- Automatic zoom and centering

### Data Plots
- Temperature distribution scatter plots
- Salinity distribution scatter plots
- Color-coded by data values
- Hover information and tooltips

## Development

### Adding New Query Types

1. **Update intent patterns** in `ai_chatbot.py`:
   ```python
   intents = {
       'new_query_type': ['keyword1', 'keyword2'],
       # ... existing intents
   }
   ```

2. **Add query generation logic**:
   ```python
   if 'new_query_type' in intents:
       # Add WHERE conditions
       where_conditions.append("COLUMN_NAME IS NOT NULL")
   ```

3. **Update response generation**:
   ```python
   if 'new_query_type' in intents:
       # Add response formatting
   ```

### Adding New Visualizations

1. **Create visualization function**:
   ```python
   def create_new_plot(data):
       # Create plot using Plotly or other library
       return fig
   ```

2. **Add to Streamlit app**:
   ```python
   with st.tabs(["Tab1", "Tab2", "New Tab"]):
       with new_tab:
           st.plotly_chart(create_new_plot(data))
   ```

## Troubleshooting

### Common Issues

1. **Missing dependencies**: Run `pip install -r requirements.txt`
2. **Database not found**: The app will create sample data automatically
3. **Port already in use**: Change the port in `run_app.py`
4. **Import errors**: Ensure all files are in the correct directories

### Logs

Check the `logs/` directory for:
- Database operations: `db_load.log`
- ETL processes: `etl.log`
- General errors: `errors.log`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs
3. Create an issue in the repository

---

**FloatChat** - Making oceanographic data analysis accessible through AI! 🌊🤖
