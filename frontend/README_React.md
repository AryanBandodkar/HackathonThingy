# 🌊 FloatChat React Frontend

A modern React frontend for the FloatChat oceanographic data AI assistant.

## Features

- 🤖 **AI Chat Interface**: Natural language interaction with oceanographic data
- 🗺️ **Interactive Maps**: Visualize data points on maps using Leaflet
- 📊 **Data Charts**: Temperature and salinity distribution plots using Recharts
- 📱 **Responsive Design**: Works on desktop and mobile devices
- ⚡ **Real-time Updates**: Live database statistics and query results

## Prerequisites

- **Node.js** (version 14 or higher)
- **npm** (comes with Node.js)
- **Python 3** (for the backend API)

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Start the Python API Server

In one terminal:
```bash
python api_server.py
```

### 3. Start the React Development Server

In another terminal:
```bash
npm start
```

### 4. Open Your Browser

Navigate to `http://localhost:3000`

## Project Structure

```
src/
├── App.js              # Main React component
├── index.js            # React entry point
├── index.css           # Global styles
public/
├── index.html          # HTML template
package.json            # Dependencies and scripts
api_server.py           # Python API server (no Flask required)
```

## Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

## API Endpoints

The React app communicates with the Python API server:

- `GET /stats` - Get database statistics
- `POST /chat` - Send chat messages to AI assistant

## Features Overview

### Chat Interface
- Natural language queries about oceanographic data
- Sample query buttons for easy testing
- Real-time AI responses with formatted output
- Conversation history

### Visualizations
- **Map View**: Interactive maps showing data locations
- **Temperature Chart**: Scatter plot of temperature distribution
- **Salinity Chart**: Scatter plot of salinity distribution

### Database Statistics
- Total number of profiles
- Unique locations count
- Average temperature and salinity
- Real-time updates

## Sample Queries

Try these sample queries in the chat interface:

- "Show me a summary of the data"
- "Find profiles with temperature above 15 degrees"
- "What's the salinity range?"
- "Show me locations with high pressure"
- "How many profiles are there?"
- "Find profiles near latitude 40 degrees"

## Customization

### Adding New Visualizations

1. Create a new chart component in `App.js`
2. Add a new tab button in the `tab-buttons` section
3. Add the corresponding content in the `tab-content` section

### Styling

Modify `src/index.css` to customize the appearance:
- Colors and gradients
- Layout and spacing
- Typography
- Component styles

### API Integration

The app uses Axios for HTTP requests. Modify the `API_BASE_URL` in `App.js` to point to a different backend.

## Troubleshooting

### Common Issues

1. **API Connection Error**
   - Ensure the Python API server is running on port 5000
   - Check that `api_server.py` is running without errors

2. **Dependencies Not Installing**
   - Make sure Node.js and npm are properly installed
   - Try deleting `node_modules` and running `npm install` again

3. **Port Already in Use**
   - The React app runs on port 3000 by default
   - The API server runs on port 5000
   - Change ports in the respective configuration files if needed

### Development Tips

- Use browser developer tools to debug API calls
- Check the console for error messages
- The Python API server logs requests (minimal logging enabled)

## Production Deployment

1. Build the React app:
   ```bash
   npm run build
   ```

2. Serve the `build` folder with a web server

3. Deploy the Python API server separately

## Technology Stack

- **React 18** - Frontend framework
- **Recharts** - Data visualization
- **Leaflet** - Interactive maps
- **Axios** - HTTP client
- **Python HTTP Server** - Backend API (no Flask required)

## License

This project is open source and available under the MIT License.

---

**FloatChat React Frontend** - Modern web interface for oceanographic data analysis! 🌊⚛️
