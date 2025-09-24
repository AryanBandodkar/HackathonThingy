import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import 'leaflet/dist/leaflet.css';

// Fix for default markers in react-leaflet
import L from 'leaflet';
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

const API_BASE_URL = 'http://localhost:5000';

function App() {
  const [messages, setMessages] = useState([
    {
      type: 'bot',
      content: "Hello! I'm your oceanographic data assistant. Ask me anything about the data, or try one of the sample queries on the left!"
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({
    total_profiles: 'Loading...',
    unique_locations: 'Loading...',
    avg_temp: 'Loading...',
    avg_salinity: 'Loading...'
  });
  const [currentData, setCurrentData] = useState([]);
  const [activeTab, setActiveTab] = useState('map');

  // Load stats on component mount
  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/stats`);
      if (response.data.success) {
        setStats(response.data.stats);
      }
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const sendMessage = async (message = inputValue) => {
    if (!message.trim()) return;

    // Add user message
    const newMessages = [...messages, { type: 'user', content: message }];
    setMessages(newMessages);
    setInputValue('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message: message
      });

      if (response.data.success) {
        // Add bot response
        setMessages([...newMessages, { 
          type: 'bot', 
          content: response.data.response,
          data: response.data.data || []
        }]);
        
        // Update current data for visualization
        if (response.data.data && response.data.data.length > 0) {
          setCurrentData(response.data.data);
        }
      } else {
        setMessages([...newMessages, { 
          type: 'bot', 
          content: `Error: ${response.data.error}`,
          isError: true
        }]);
      }
    } catch (error) {
      setMessages([...newMessages, { 
        type: 'bot', 
        content: `Error: ${error.message}`,
        isError: true
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  const sampleQueries = [
    'Show me a summary of the data',
    'Find profiles with temperature above 15 degrees',
    'What\'s the salinity range?',
    'Show me locations with high pressure',
    'How many profiles are there?',
    'Find profiles near latitude 40 degrees'
  ];

  const renderMap = () => {
    if (!currentData || currentData.length === 0) {
      return <div className="loading">No location data available for mapping.</div>;
    }

    const validData = currentData.filter(item => 
      item.LATITUDE && item.LONGITUDE && 
      !isNaN(item.LATITUDE) && !isNaN(item.LONGITUDE)
    );

    if (validData.length === 0) {
      return <div className="loading">No valid location data available.</div>;
    }

    const centerLat = validData.reduce((sum, item) => sum + item.LATITUDE, 0) / validData.length;
    const centerLon = validData.reduce((sum, item) => sum + item.LONGITUDE, 0) / validData.length;

    return (
      <MapContainer
        center={[centerLat, centerLon]}
        zoom={6}
        className="map-container"
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        {validData.map((item, index) => (
          <Marker key={index} position={[item.LATITUDE, item.LONGITUDE]}>
            <Popup>
              <div>
                <strong>Profile {item.N_PROF || index + 1}</strong><br/>
                Temperature: {item.TEMP ? item.TEMP.toFixed(2) : 'N/A'}°C<br/>
                Salinity: {item.PSAL ? item.PSAL.toFixed(2) : 'N/A'} PSU<br/>
                Pressure: {item.PRES ? item.PRES.toFixed(2) : 'N/A'} dbar<br/>
                Source: {item.SOURCE_FILE || 'N/A'}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    );
  };

  const renderTemperatureChart = () => {
    if (!currentData || currentData.length === 0) {
      return <div className="loading">No temperature data available for plotting.</div>;
    }

    const chartData = currentData
      .filter(item => item.LATITUDE && item.LONGITUDE && item.TEMP)
      .map(item => ({
        x: item.LONGITUDE,
        y: item.LATITUDE,
        temp: item.TEMP,
        salinity: item.PSAL || 0,
        pressure: item.PRES || 0
      }));

    if (chartData.length === 0) {
      return <div className="loading">No valid temperature data available.</div>;
    }

    return (
      <ResponsiveContainer width="100%" height={300}>
        <ScatterChart data={chartData}>
          <CartesianGrid />
          <XAxis 
            type="number" 
            dataKey="x" 
            name="Longitude"
            label={{ value: 'Longitude', position: 'insideBottom', offset: -5 }}
          />
          <YAxis 
            type="number" 
            dataKey="y" 
            name="Latitude"
            label={{ value: 'Latitude', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip 
            formatter={(value, name) => {
              if (name === 'temp') return [`${value.toFixed(2)}°C`, 'Temperature'];
              if (name === 'salinity') return [`${value.toFixed(2)} PSU`, 'Salinity'];
              if (name === 'pressure') return [`${value.toFixed(2)} dbar`, 'Pressure'];
              return [value, name];
            }}
            labelFormatter={(label, payload) => {
              if (payload && payload[0]) {
                return `Location: ${payload[0].payload.x.toFixed(3)}°W, ${payload[0].payload.y.toFixed(3)}°N`;
              }
              return '';
            }}
          />
          <Scatter 
            dataKey="temp" 
            fill="#ff6b6b" 
            name="Temperature"
            r={6}
          />
        </ScatterChart>
      </ResponsiveContainer>
    );
  };

  const renderSalinityChart = () => {
    if (!currentData || currentData.length === 0) {
      return <div className="loading">No salinity data available for plotting.</div>;
    }

    const chartData = currentData
      .filter(item => item.LATITUDE && item.LONGITUDE && item.PSAL)
      .map(item => ({
        x: item.LONGITUDE,
        y: item.LATITUDE,
        temp: item.TEMP || 0,
        salinity: item.PSAL,
        pressure: item.PRES || 0
      }));

    if (chartData.length === 0) {
      return <div className="loading">No valid salinity data available.</div>;
    }

    return (
      <ResponsiveContainer width="100%" height={300}>
        <ScatterChart data={chartData}>
          <CartesianGrid />
          <XAxis 
            type="number" 
            dataKey="x" 
            name="Longitude"
            label={{ value: 'Longitude', position: 'insideBottom', offset: -5 }}
          />
          <YAxis 
            type="number" 
            dataKey="y" 
            name="Latitude"
            label={{ value: 'Latitude', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip 
            formatter={(value, name) => {
              if (name === 'temp') return [`${value.toFixed(2)}°C`, 'Temperature'];
              if (name === 'salinity') return [`${value.toFixed(2)} PSU`, 'Salinity'];
              if (name === 'pressure') return [`${value.toFixed(2)} dbar`, 'Pressure'];
              return [value, name];
            }}
            labelFormatter={(label, payload) => {
              if (payload && payload[0]) {
                return `Location: ${payload[0].payload.x.toFixed(3)}°W, ${payload[0].payload.y.toFixed(3)}°N`;
              }
              return '';
            }}
          />
          <Scatter 
            dataKey="salinity" 
            fill="#4ecdc4" 
            name="Salinity"
            r={6}
          />
        </ScatterChart>
      </ResponsiveContainer>
    );
  };

  return (
    <div className="container">
      <div className="header">
        <h1>🌊 FloatChat</h1>
        <p>Oceanographic Data AI Assistant</p>
      </div>
      
      <div className="main-content">
        <div className="sidebar">
          <div className="stats">
            <h3>📊 Database Stats</h3>
            <div className="stat-item">
              <span>Total Profiles:</span>
              <span>{stats.total_profiles}</span>
            </div>
            <div className="stat-item">
              <span>Unique Locations:</span>
              <span>{stats.unique_locations}</span>
            </div>
            <div className="stat-item">
              <span>Avg Temperature:</span>
              <span>{typeof stats.avg_temp === 'number' ? stats.avg_temp.toFixed(2) + '°C' : stats.avg_temp}</span>
            </div>
            <div className="stat-item">
              <span>Avg Salinity:</span>
              <span>{typeof stats.avg_salinity === 'number' ? stats.avg_salinity.toFixed(2) + ' PSU' : stats.avg_salinity}</span>
            </div>
          </div>
          
          <div className="sample-queries">
            <h3>💡 Sample Queries</h3>
            {sampleQueries.map((query, index) => (
              <button
                key={index}
                className="query-btn"
                onClick={() => sendMessage(query)}
              >
                {query}
              </button>
            ))}
          </div>
        </div>
        
        <div className="chat-area">
          <div className="messages">
            {messages.map((message, index) => (
              <div key={index} className={`message ${message.type}-message`}>
                {message.isError ? (
                  <div className="error">
                    <strong>❌ Error:</strong> {message.content}
                  </div>
                ) : (
                  <>
                    <strong>{message.type === 'user' ? '👤 You:' : '🤖 AI Assistant:'}</strong>{' '}
                    <div dangerouslySetInnerHTML={{ __html: message.content.replace(/\n/g, '<br>') }} />
                  </>
                )}
              </div>
            ))}
            {loading && (
              <div className="loading">
                🤔 Thinking...
              </div>
            )}
          </div>
          
          <div className="input-area">
            <div className="input-group">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything about the oceanographic data..."
              />
              <button className="btn" onClick={() => sendMessage()}>
                Send
              </button>
            </div>
          </div>
        </div>
      </div>

      {currentData && currentData.length > 0 && (
        <div className="visualization-tabs">
          <div className="tab-buttons">
            <button
              className={`tab-button ${activeTab === 'map' ? 'active' : ''}`}
              onClick={() => setActiveTab('map')}
            >
              🗺️ Map View
            </button>
            <button
              className={`tab-button ${activeTab === 'temperature' ? 'active' : ''}`}
              onClick={() => setActiveTab('temperature')}
            >
              🌡️ Temperature
            </button>
            <button
              className={`tab-button ${activeTab === 'salinity' ? 'active' : ''}`}
              onClick={() => setActiveTab('salinity')}
            >
              🧂 Salinity
            </button>
          </div>
          
          <div className="tab-content">
            {activeTab === 'map' && renderMap()}
            {activeTab === 'temperature' && renderTemperatureChart()}
            {activeTab === 'salinity' && renderSalinityChart()}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
