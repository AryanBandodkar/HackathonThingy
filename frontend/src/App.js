import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, Popup, Tooltip as LeafletTooltip } from 'react-leaflet';
import { ScatterChart, Scatter, XAxis, YAxis, ZAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Brush } from 'recharts';
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
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // increase timeout to handle large result sets
  headers: { 'Content-Type': 'application/json' }
});

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
  const [apiHealthy, setApiHealthy] = useState(true);
  const [activeTab, setActiveTab] = useState('map');

  // Always use the latest bot message data for visualizations to match text
  const getLatestBotData = () => {
    for (let i = messages.length - 1; i >= 0; i--) {
      const m = messages[i];
      if (m.type === 'bot' && Array.isArray(m.data) && m.data.length > 0) {
        return m.data;
      }
    }
    return currentData;
  };

  // Small inline map for individual bot responses
  const InlineMap = ({ data }) => {
    if (!data || data.length === 0) return null;

    const valid = data.filter(p => p.LATITUDE != null && p.LONGITUDE != null);
    if (valid.length === 0) return null;

    const centerLat = valid.reduce((s, r) => s + r.LATITUDE, 0) / valid.length;
    const centerLon = valid.reduce((s, r) => s + r.LONGITUDE, 0) / valid.length;

    return (
      <div className="inline-map-card">
        <div className="inline-map-header">
          <span className="pill">🗺️ Map</span>
          <span className="pill pill-secondary">{valid.length} point{valid.length > 1 ? 's' : ''}</span>
        </div>
        <MapContainer center={[centerLat, centerLon]} zoom={6} className="mini-map">
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          {valid.map((item, idx) => (
            <Marker key={idx} position={[item.LATITUDE, item.LONGITUDE]}>
              <LeafletTooltip direction="top" offset={[0, -10]} opacity={0.95} permanent={false}>
                <div>
                  <div><strong>Lat:</strong> {item.LATITUDE.toFixed(3)}°</div>
                  <div><strong>Lon:</strong> {item.LONGITUDE.toFixed(3)}°</div>
                  {item.TEMP != null && (<div><strong>Temp:</strong> {item.TEMP.toFixed(2)}°C</div>)}
                  {item.PSAL != null && (<div><strong>Salinity:</strong> {item.PSAL.toFixed(2)} PSU</div>)}
                  {item.PRES != null && (<div><strong>Pressure:</strong> {item.PRES.toFixed(2)} dbar</div>)}
                </div>
              </LeafletTooltip>
              <Popup>
                <div>
                  <strong>Profile {item.N_PROF || idx + 1}</strong><br/>
                  {item.TEMP != null ? `Temp: ${item.TEMP.toFixed(2)}°C` : ''}<br/>
                  {item.PSAL != null ? `Salinity: ${item.PSAL.toFixed(2)} PSU` : ''}<br/>
                  {item.PRES != null ? `Pressure: ${item.PRES.toFixed(2)} dbar` : ''}
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    );
  };

  // Load stats on component mount
  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await api.get('/stats');
      if (response.data.success) {
        setStats(response.data.stats);
        setApiHealthy(true);
      }
    } catch (error) {
      console.error('Error loading stats:', error);
      setApiHealthy(false);
      setStats({
        total_profiles: 'N/A',
        unique_locations: 'N/A',
        avg_temp: 'N/A',
        avg_salinity: 'N/A'
      });
    }
  };

  const toNumberOrNull = (v) => {
    const n = Number(v);
    return isFinite(n) ? n : null;
  };

  const normalizeData = (rows = []) => {
    return rows.map((r) => ({
      ...r,
      LATITUDE: toNumberOrNull(r.LATITUDE),
      LONGITUDE: toNumberOrNull(r.LONGITUDE),
      TEMP: toNumberOrNull(r.TEMP),
      PSAL: toNumberOrNull(r.PSAL),
      PRES: toNumberOrNull(r.PRES),
    }));
  };

  const sendMessage = async (message = inputValue) => {
    if (!message.trim()) return;

    // Add user message
    const newMessages = [...messages, { type: 'user', content: message }];
    setMessages(newMessages);
    setInputValue('');
    setLoading(true);

    try {
      const response = await api.post('/chat', { message });

      if (response.data.success) {
        const normalized = normalizeData(response.data.data || []);
        // Add bot response
        setMessages([...newMessages, { 
          type: 'bot', 
          content: response.data.response,
          data: normalized
        }]);
        
        // Update current data for visualization
        if (normalized.length > 0) {
          setCurrentData(normalized);
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
        content: `Cannot reach API. Please ensure backend is running on http://localhost:5000. (${error.message})`,
        isError: true
      }]);
      setApiHealthy(false);
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
    const vizData = getLatestBotData();
    if (!vizData || vizData.length === 0) {
      return <div className="loading">No location data available for mapping.</div>;
    }

    const validData = vizData.filter(item => 
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
        key={`${centerLat.toFixed(3)}_${centerLon.toFixed(3)}_${validData.length}`}
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
            <LeafletTooltip direction="top" offset={[0, -10]} opacity={0.95} permanent={false}>
              <div>
                <div><strong>Lat:</strong> {item.LATITUDE.toFixed(3)}°</div>
                <div><strong>Lon:</strong> {item.LONGITUDE.toFixed(3)}°</div>
                {item.TEMP != null && (<div><strong>Temp:</strong> {item.TEMP.toFixed(2)}°C</div>)}
                {item.PSAL != null && (<div><strong>Salinity:</strong> {item.PSAL.toFixed(2)} PSU</div>)}
                {item.PRES != null && (<div><strong>Pressure:</strong> {item.PRES.toFixed(2)} dbar</div>)}
              </div>
            </LeafletTooltip>
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
    const vizData = getLatestBotData();
    if (!vizData || vizData.length === 0) {
      return <div className="loading">No temperature data available for plotting.</div>;
    }

    const jitter = (v, amount = 0.05) => {
      if (v == null || isNaN(v)) return v;
      const rand = (Math.random() - 0.5) * 2 * amount;
      return v + rand;
    };

    const chartData = vizData
      .filter(item => item.LATITUDE != null && item.LONGITUDE != null && item.TEMP != null)
      .map(item => ({
        x: jitter(item.LONGITUDE),
        y: jitter(item.LATITUDE),
        temp: item.TEMP,
        salinity: item.PSAL || 0,
        pressure: item.PRES || 0
      }));

    if (chartData.length === 0) {
      return <div className="loading">No valid temperature data available.</div>;
    }

    const valuesX = chartData.map(d => d.x).filter(v => isFinite(v));
    const valuesY = chartData.map(d => d.y).filter(v => isFinite(v));
    const quantile = (arr, q) => {
      if (!arr.length) return 0;
      const a = [...arr].sort((a,b)=>a-b);
      const pos = (a.length - 1) * q;
      const base = Math.floor(pos);
      const rest = pos - base;
      return a[base] + ((a[base + 1] ?? a[base]) - a[base]) * rest;
    };
    const qx1 = quantile(valuesX, 0.05), qx3 = quantile(valuesX, 0.95);
    const qy1 = quantile(valuesY, 0.05), qy3 = quantile(valuesY, 0.95);
    const padX = (qx3 - qx1) * 0.1 || 1;
    const padY = (qy3 - qy1) * 0.1 || 1;
    const domainX = [qx1 - padX, qx3 + padX];
    const domainY = [qy1 - padY, qy3 + padY];

    return (
      <ResponsiveContainer width="100%" height={340}>
        <ScatterChart margin={{ top: 10, right: 20, bottom: 30, left: 50 }}>
          <CartesianGrid />
          <XAxis 
            type="number" 
            dataKey="x" 
            name="Longitude"
            label={{ value: 'Longitude', position: 'insideBottom', offset: -5 }}
            domain={domainX}
            tickCount={8}
          />
          <YAxis 
            type="number" 
            dataKey="y" 
            name="Latitude"
            label={{ value: 'Latitude', angle: -90, position: 'insideLeft' }}
            domain={domainY}
            tickCount={7}
          />
          <RechartsTooltip 
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
          <Scatter data={chartData} name="Temperature" fill="#ff6b6b" fillOpacity={0.7} />
          <Brush dataKey="x" height={18} stroke="#22ff88" travellerWidth={8} />
        </ScatterChart>
      </ResponsiveContainer>
    );
  };

  const renderSalinityChart = () => {
    const vizData = getLatestBotData();
    if (!vizData || vizData.length === 0) {
      return <div className="loading">No salinity data available for plotting.</div>;
    }

    const jitter = (v, amount = 0.05) => {
      if (v == null || isNaN(v)) return v;
      const rand = (Math.random() - 0.5) * 2 * amount;
      return v + rand;
    };

    const chartData = vizData
      .filter(item => item.LATITUDE != null && item.LONGITUDE != null && item.PSAL != null)
      .map(item => ({
        x: jitter(item.LONGITUDE),
        y: jitter(item.LATITUDE),
        temp: item.TEMP || 0,
        salinity: item.PSAL,
        pressure: item.PRES || 0
      }));

    if (chartData.length === 0) {
      return <div className="loading">No valid salinity data available.</div>;
    }

    const valuesX = chartData.map(d => d.x).filter(v => isFinite(v));
    const valuesY = chartData.map(d => d.y).filter(v => isFinite(v));
    const quantile = (arr, q) => {
      if (!arr.length) return 0;
      const a = [...arr].sort((a,b)=>a-b);
      const pos = (a.length - 1) * q;
      const base = Math.floor(pos);
      const rest = pos - base;
      return a[base] + ((a[base + 1] ?? a[base]) - a[base]) * rest;
    };
    const qx1 = quantile(valuesX, 0.05), qx3 = quantile(valuesX, 0.95);
    const qy1 = quantile(valuesY, 0.05), qy3 = quantile(valuesY, 0.95);
    const padX = (qx3 - qx1) * 0.1 || 1;
    const padY = (qy3 - qy1) * 0.1 || 1;
    const domainX = [qx1 - padX, qx3 + padX];
    const domainY = [qy1 - padY, qy3 + padY];

    return (
      <ResponsiveContainer width="100%" height={340}>
        <ScatterChart margin={{ top: 10, right: 20, bottom: 30, left: 50 }}>
          <CartesianGrid />
          <XAxis 
            type="number" 
            dataKey="x" 
            name="Longitude"
            label={{ value: 'Longitude', position: 'insideBottom', offset: -5 }}
            domain={domainX}
            tickCount={8}
          />
          <YAxis 
            type="number" 
            dataKey="y" 
            name="Latitude"
            label={{ value: 'Latitude', angle: -90, position: 'insideLeft' }}
            domain={domainY}
            tickCount={7}
          />
          <RechartsTooltip 
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
          <Scatter data={chartData} name="Salinity" fill="#4ecdc4" fillOpacity={0.7} />
          <Brush dataKey="x" height={18} stroke="#22ff88" travellerWidth={8} />
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
          {!apiHealthy && (
            <div className="api-alert">
              ⚠️ Backend API not reachable at {API_BASE_URL}. Start it with <code>python api_server.py</code>.
            </div>
          )}
          <div className="messages">
            {messages.map((message, index) => (
              <div key={index} className={`message-card ${message.type}-message`}>
                {message.isError ? (
                  <div className="error">
                    <strong>❌ Error:</strong> {message.content}
                  </div>
                ) : (
                  <>
                    <div className="message-header">
                      <strong>{message.type === 'user' ? '👤 You' : '🤖 AI Assistant'}</strong>
                    </div>
                    <div className="message-body" dangerouslySetInnerHTML={{ __html: message.content.replace(/\n/g, '<br>') }} />
                    {message.type === 'bot' && Array.isArray(message.data) && message.data.length > 0 && (
                      <InlineMap data={message.data} />
                    )}
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

      {getLatestBotData() && getLatestBotData().length > 0 && (
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
