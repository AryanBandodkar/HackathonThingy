import json
import re
from typing import Dict, List, Any, Optional
from database_manager import DatabaseManager
import logging

class AIChatbot:
    def __init__(self, db_path: str = "argo_profiles.db"):
        self.db_manager = DatabaseManager(db_path)
        self.setup_logging()
        self.conversation_history = []
        
    def setup_logging(self):
        """Setup logging for the chatbot"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def analyze_user_intent(self, user_input: str) -> Dict[str, Any]:
        """Analyze user input to determine intent and extract parameters"""
        user_input_lower = user_input.lower()
        
        # Define intent patterns
        intents = {
            'data_summary': ['summary', 'overview', 'statistics', 'stats', 'total', 'count'],
            'temperature_query': ['temperature', 'temp', 'warm', 'cold', 'hot'],
            'salinity_query': ['salinity', 'salt', 'psal'],
            'location_query': ['location', 'latitude', 'longitude', 'coordinates', 'where', 'position'],
            'pressure_query': ['pressure', 'pres', 'depth'],
            'profile_query': ['profile', 'profiles', 'data points'],
            'source_query': ['source', 'file', 'origin', 'dataset'],
            'range_query': ['range', 'between', 'from', 'to', 'min', 'max', 'average'],
            'visualization': ['map', 'plot', 'chart', 'graph', 'visualize', 'show'],
            'count_query': ['how many', 'number of', 'count of']
        }
        
        detected_intents = []
        for intent, keywords in intents.items():
            if any(keyword in user_input_lower for keyword in keywords):
                detected_intents.append(intent)
        
        # Extract numerical values
        numbers = re.findall(r'-?\d+\.?\d*', user_input)

        # Flags for proximity queries like "near latitude 40" or "near lon -70"
        near_latitude = 'near' in user_input_lower and 'latitude' in user_input_lower
        near_longitude = 'near' in user_input_lower and 'longitude' in user_input_lower
        
        # Extract comparison operators
        operators = []
        if '>' in user_input or 'greater' in user_input_lower or 'above' in user_input_lower:
            operators.append('>')
        if '<' in user_input or 'less' in user_input_lower or 'below' in user_input_lower:
            operators.append('<')
        if '=' in user_input or 'equal' in user_input_lower:
            operators.append('=')

        # Qualifiers for high/low wording
        is_high = 'high' in user_input_lower or 'highest' in user_input_lower or 'max' in user_input_lower
        is_low = 'low' in user_input_lower or 'lowest' in user_input_lower or 'min' in user_input_lower
        
        return {
            'intents': detected_intents,
            'numbers': [float(n) for n in numbers if n],
            'operators': operators,
            'original_input': user_input,
            'near_latitude': near_latitude,
            'near_longitude': near_longitude,
            'is_high': is_high,
            'is_low': is_low
        }
    
    def generate_sql_query(self, intent_analysis: Dict[str, Any]) -> str:
        """Generate SQL query based on intent analysis"""
        intents = intent_analysis['intents']
        numbers = intent_analysis['numbers']
        operators = intent_analysis['operators']
        
        # Base query
        base_query = "SELECT * FROM profiles"
        where_conditions = []
        
        # Handle different intents
        if 'temperature_query' in intents:
            if numbers and operators:
                if '>' in operators:
                    where_conditions.append(f"TEMP > {numbers[0]}")
                elif '<' in operators:
                    where_conditions.append(f"TEMP < {numbers[0]}")
                elif '=' in operators:
                    where_conditions.append(f"TEMP = {numbers[0]}")
            else:
                # Default temperature query
                where_conditions.append("TEMP IS NOT NULL")
        
        if 'salinity_query' in intents:
            if numbers and operators:
                if '>' in operators:
                    where_conditions.append(f"PSAL > {numbers[0]}")
                elif '<' in operators:
                    where_conditions.append(f"PSAL < {numbers[0]}")
                elif '=' in operators:
                    where_conditions.append(f"PSAL = {numbers[0]}")
            else:
                where_conditions.append("PSAL IS NOT NULL")
        
        if 'pressure_query' in intents:
            if numbers and operators:
                if '>' in operators:
                    where_conditions.append(f"PRES > {numbers[0]}")
                elif '<' in operators:
                    where_conditions.append(f"PRES < {numbers[0]}")
                elif '=' in operators:
                    where_conditions.append(f"PRES = {numbers[0]}")
            else:
                where_conditions.append("PRES IS NOT NULL")
        
        if 'location_query' in intents:
            # Handle proximity queries
            if intent_analysis.get('near_latitude') and numbers:
                lat = numbers[0]
                where_conditions.append(f"LATITUDE IS NOT NULL AND ABS(LATITUDE - {lat}) <= 1.0")
            elif intent_analysis.get('near_longitude') and numbers:
                lon = numbers[0]
                where_conditions.append(f"LONGITUDE IS NOT NULL AND ABS(LONGITUDE - {lon}) <= 1.0")
            else:
                where_conditions.append("LATITUDE IS NOT NULL AND LONGITUDE IS NOT NULL")
        
        if 'source_query' in intents:
            where_conditions.append("SOURCE_FILE IS NOT NULL")
        
        # Add WHERE clause if conditions exist
        if where_conditions:
            base_query += " WHERE " + " AND ".join(where_conditions)
        
        # Add ORDER BY for better results and respect high/low wording
        if 'temperature_query' in intents:
            base_query += " ORDER BY TEMP " + ("DESC" if intent_analysis.get('is_high') or not intent_analysis.get('is_low') else "ASC")
        elif 'salinity_query' in intents:
            base_query += " ORDER BY PSAL " + ("DESC" if intent_analysis.get('is_high') or not intent_analysis.get('is_low') else "ASC")
        elif 'pressure_query' in intents:
            base_query += " ORDER BY PRES " + ("DESC" if intent_analysis.get('is_high') or not intent_analysis.get('is_low') else "ASC")

        # Cap result set to reduce response time and payload size
        base_query += " LIMIT 1000"

        return base_query
    
    def generate_summary_query(self, intent_analysis: Dict[str, Any]) -> str:
        """Generate summary/aggregation query"""
        intents = intent_analysis['intents']
        
        if 'data_summary' in intents:
            return """
            SELECT 
                COUNT(*) as total_profiles,
                COUNT(DISTINCT LATITUDE || ',' || LONGITUDE) as unique_locations,
                MIN(TEMP) as min_temperature,
                MAX(TEMP) as max_temperature,
                AVG(TEMP) as avg_temperature,
                MIN(PSAL) as min_salinity,
                MAX(PSAL) as max_salinity,
                AVG(PSAL) as avg_salinity,
                MIN(PRES) as min_pressure,
                MAX(PRES) as max_pressure,
                AVG(PRES) as avg_pressure
            FROM profiles
            """

        # Explicit count requests
        if 'count_query' in intents:
            return "SELECT COUNT(*) as total_profiles FROM profiles"
        
        if 'range_query' in intents and 'salinity_query' in intents:
            # Salinity range specifically
            return """
            SELECT 
                MIN(PSAL) as min_salinity,
                MAX(PSAL) as max_salinity,
                AVG(PSAL) as avg_salinity
            FROM profiles
            """

        if 'range_query' in intents and 'temperature_query' in intents:
            # Temperature range specifically
            return """
            SELECT 
                MIN(TEMP) as min_temperature,
                MAX(TEMP) as max_temperature,
                AVG(TEMP) as avg_temperature
            FROM profiles
            """

        if 'range_query' in intents:
            return """
            SELECT 
                MIN(LATITUDE) as min_latitude,
                MAX(LATITUDE) as max_latitude,
                MIN(LONGITUDE) as min_longitude,
                MAX(LONGITUDE) as max_longitude,
                MIN(TEMP) as min_temperature,
                MAX(TEMP) as max_temperature,
                MIN(PSAL) as min_salinity,
                MAX(PSAL) as max_salinity
            FROM profiles
            """
        
        return "SELECT COUNT(*) as total_profiles FROM profiles"
    
    def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """Process user input and return response"""
        try:
            # Analyze user intent
            intent_analysis = self.analyze_user_intent(user_input)
            
            # Store in conversation history
            self.conversation_history.append({
                'user': user_input,
                'intent_analysis': intent_analysis
            })
            
            # Determine query type
            if (
                'data_summary' in intent_analysis['intents']
                or 'range_query' in intent_analysis['intents']
                or 'count_query' in intent_analysis['intents']
            ):
                query = self.generate_summary_query(intent_analysis)
                query_type = 'summary'
            else:
                query = self.generate_sql_query(intent_analysis)
                query_type = 'data'
            
            # Execute query
            result = self.db_manager.execute_query(query)
            
            # Generate response
            response = self.generate_response(intent_analysis, result, query_type)
            
            return {
                'success': True,
                'response': response,
                'query': query,
                'data': result['data'],
                'intent_analysis': intent_analysis
            }
            
        except Exception as e:
            self.logger.error(f"Error processing user input: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'response': "I'm sorry, I encountered an error processing your request. Please try again."
            }
    
    def generate_response(self, intent_analysis: Dict[str, Any], result: Dict[str, Any], query_type: str) -> str:
        """Generate human-readable response based on query results"""
        if not result['success']:
            return f"I encountered an error: {result['error']}"
        
        data = result['data']
        intents = intent_analysis['intents']

        # Safe number formatter to avoid NoneType format errors
        def fmt_num(value, digits: int = 2):
            try:
                if value is None:
                    return "N/A"
                return f"{float(value):.{digits}f}"
            except Exception:
                return "N/A"
        
        if query_type == 'summary':
            if data and len(data) > 0:
                row = data[0]
                response = "Here's a summary of the oceanographic data:\n\n"
                
                if 'total_profiles' in row:
                    response += f"📊 **Total Profiles**: {row['total_profiles']}\n"
                
                if 'unique_locations' in row:
                    response += f"📍 **Unique Locations**: {row['unique_locations']}\n"
                
                if 'min_temperature' in row and 'max_temperature' in row:
                    response += f"🌡️ **Temperature Range**: {fmt_num(row.get('min_temperature'))}°C to {fmt_num(row.get('max_temperature'))}°C\n"
                
                if 'avg_temperature' in row:
                    response += f"🌡️ **Average Temperature**: {fmt_num(row.get('avg_temperature'))}°C\n"
                
                if 'min_salinity' in row and 'max_salinity' in row:
                    response += f"🧂 **Salinity Range**: {fmt_num(row.get('min_salinity'))} to {fmt_num(row.get('max_salinity'))} PSU\n"
                
                if 'avg_salinity' in row:
                    response += f"🧂 **Average Salinity**: {fmt_num(row.get('avg_salinity'))} PSU\n"
                
                if 'min_pressure' in row and 'max_pressure' in row:
                    response += f"💧 **Pressure Range**: {fmt_num(row.get('min_pressure'))} to {fmt_num(row.get('max_pressure'))} dbar\n"
                
                if 'avg_pressure' in row:
                    response += f"💧 **Average Pressure**: {fmt_num(row.get('avg_pressure'))} dbar\n"
                
                if 'min_latitude' in row and 'max_latitude' in row:
                    response += f"🗺️ **Latitude Range**: {fmt_num(row.get('min_latitude'))}° to {fmt_num(row.get('max_latitude'))}°\n"
                
                if 'min_longitude' in row and 'max_longitude' in row:
                    response += f"🗺️ **Longitude Range**: {fmt_num(row.get('min_longitude'))}° to {fmt_num(row.get('max_longitude'))}°\n"
                
                return response
            else:
                return "No summary data available."
        
        else:  # data query
            if not data:
                return "No data found matching your criteria."
            
            response = f"Found {len(data)} data points matching your query:\n\n"
            
            # Show all results in text (may be long)
            for i, row in enumerate(data):
                response += f"**Profile {i+1}:**\n"
                
                if 'LATITUDE' in row and 'LONGITUDE' in row:
                    response += f"  📍 Location: {fmt_num(row.get('LATITUDE'), 3)}°N, {fmt_num(row.get('LONGITUDE'), 3)}°W\n"
                
                if 'TEMP' in row:
                    response += f"  🌡️ Temperature: {fmt_num(row.get('TEMP'))}°C\n"
                
                if 'PSAL' in row:
                    response += f"  🧂 Salinity: {fmt_num(row.get('PSAL'))} PSU\n"
                
                if 'PRES' in row:
                    response += f"  💧 Pressure: {fmt_num(row.get('PRES'))} dbar\n"
                
                if 'SOURCE_FILE' in row:
                    response += f"  📁 Source: {row['SOURCE_FILE']}\n"
                
                response += "\n"
            
            # No truncation; all results listed
            
            return response
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

if __name__ == "__main__":
    # Test the chatbot
    chatbot = AIChatbot()
    
    # Test queries
    test_queries = [
        "Show me a summary of the data",
        "Find profiles with temperature above 15 degrees",
        "What's the salinity range?",
        "Show me locations with high pressure",
        "How many profiles are there?"
    ]
    
    for query in test_queries:
        print(f"\nUser: {query}")
        result = chatbot.process_user_input(query)
        print(f"Bot: {result['response']}")
        print(f"Query: {result.get('query', 'N/A')}")
