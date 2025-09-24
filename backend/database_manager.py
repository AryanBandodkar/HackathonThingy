import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

class DatabaseManager:
    def __init__(self, db_path: str = "argo_profiles.db"):
        self.db_path = Path(db_path)
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for database operations"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def get_connection(self):
        """Get database connection with proper settings"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn
    
    def create_sample_data(self):
        """Create sample data for testing if database is empty"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
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
        )
        """)
        
        # Check if data exists
        cursor.execute("SELECT COUNT(*) FROM profiles")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Insert sample data
            sample_data = [
                (1, 150, 2456789.5, 40.5, -70.2, 10.5, 15.2, 35.1, 10.3, 15.0, 35.0, "D20250922_prof_0.nc"),
                (2, 200, 2456790.5, 41.0, -69.8, 15.2, 14.8, 34.9, 15.0, 14.5, 34.8, "D20250923_prof_0.nc"),
                (3, 180, 2456791.5, 39.8, -70.5, 8.7, 16.1, 35.3, 8.5, 15.9, 35.2, "R20250921_prof_0.nc"),
                (4, 220, 2456792.5, 40.2, -69.5, 12.3, 15.5, 35.0, 12.0, 15.3, 34.9, "R20250922_prof_0.nc"),
                (5, 190, 2456793.5, 40.8, -70.0, 9.8, 15.8, 35.2, 9.5, 15.6, 35.1, "D20250924_prof_0.nc"),
            ]
            
            cursor.executemany("""
            INSERT INTO profiles (N_PROF, N_LEVELS, JULD, LATITUDE, LONGITUDE, 
                                PRES, TEMP, PSAL, PRES_ADJUSTED, TEMP_ADJUSTED, PSAL_ADJUSTED, SOURCE_FILE)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_data)
            
            conn.commit()
            self.logger.info(f"Inserted {len(sample_data)} sample records")
        
        conn.close()
        return count
    
    def get_table_schema(self) -> List[Dict[str, str]]:
        """Get table schema information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(profiles)")
        columns = cursor.fetchall()
        
        schema = []
        for col in columns:
            schema.append({
                'name': col[1],
                'type': col[2],
                'nullable': not col[3],
                'default': col[4],
                'primary_key': bool(col[5])
            })
        
        conn.close()
        return schema
    
    def execute_query(self, query: str) -> Dict[str, Any]:
        """Execute SQL query and return results"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Execute query
            cursor.execute(query)
            
            # Get column names
            columns = [description[0] for description in cursor.description] if cursor.description else []
            
            # Get data
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            results = []
            for row in rows:
                results.append(dict(zip(columns, row)))
            
            conn.close()
            
            return {
                'success': True,
                'data': results,
                'columns': columns,
                'row_count': len(results)
            }
            
        except Exception as e:
            self.logger.error(f"Query execution failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'data': [],
                'columns': [],
                'row_count': 0
            }
    
    def get_sample_queries(self) -> List[str]:
        """Get sample queries for the AI to understand the data structure"""
        return [
            "SELECT COUNT(*) as total_profiles FROM profiles",
            "SELECT * FROM profiles LIMIT 5",
            "SELECT LATITUDE, LONGITUDE, TEMP, PSAL FROM profiles WHERE TEMP > 15",
            "SELECT SOURCE_FILE, COUNT(*) as profile_count FROM profiles GROUP BY SOURCE_FILE",
            "SELECT AVG(TEMP) as avg_temp, AVG(PSAL) as avg_salinity FROM profiles",
            "SELECT MIN(LATITUDE) as min_lat, MAX(LATITUDE) as max_lat, MIN(LONGITUDE) as min_lon, MAX(LONGITUDE) as max_lon FROM profiles"
        ]
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary statistics about the data"""
        summary_queries = {
            'total_profiles': "SELECT COUNT(*) as count FROM profiles",
            'unique_locations': "SELECT COUNT(DISTINCT LATITUDE || ',' || LONGITUDE) as count FROM profiles",
            'temp_range': "SELECT MIN(TEMP) as min_temp, MAX(TEMP) as max_temp, AVG(TEMP) as avg_temp FROM profiles",
            'salinity_range': "SELECT MIN(PSAL) as min_salinity, MAX(PSAL) as max_salinity, AVG(PSAL) as avg_salinity FROM profiles",
            'pressure_range': "SELECT MIN(PRES) as min_pressure, MAX(PRES) as max_pressure, AVG(PRES) as avg_pressure FROM profiles",
            'source_files': "SELECT SOURCE_FILE, COUNT(*) as count FROM profiles GROUP BY SOURCE_FILE"
        }
        
        summary = {}
        for key, query in summary_queries.items():
            result = self.execute_query(query)
            if result['success'] and result['data']:
                summary[key] = result['data'][0]
            else:
                summary[key] = {'error': result.get('error', 'Unknown error')}
        
        return summary

if __name__ == "__main__":
    # Test the database manager
    db = DatabaseManager()
    db.create_sample_data()
    
    print("Database Schema:")
    schema = db.get_table_schema()
    for col in schema:
        print(f"  {col['name']}: {col['type']}")
    
    print("\nData Summary:")
    summary = db.get_data_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
