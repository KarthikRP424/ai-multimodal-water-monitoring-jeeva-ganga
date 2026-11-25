const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// In‑memory store for sensor data
let sensorState = {
  motion: false,   // PIR
  distance: null,  // ultrasonic (cm)
  camUrl: null    // ESP‑Cam stream URL
};

// POST endpoints ---------------------------------------------------
app.post('/api/pir', (req, res) => {
  sensorState.motion = !!req.body.motion;
  console.log('🔔 PIR update:', sensorState.motion);
  res.sendStatus(200);
});

app.post('/api/ultrasonic', (req, res) => {
  sensorState.distance = Number(req.body.distance);
  console.log('📏 Ultrasonic update:', sensorState.distance);
  res.sendStatus(200);
});

app.post('/api/cam', (req, res) => {
  sensorState.camUrl = req.body.url;
  console.log('📹 Camera URL received:', sensorState.camUrl);
  res.sendStatus(200);
});

// GET endpoint for the front‑end ----------------------------------
app.get('/api/state', (req, res) => {
  res.json(sensorState);
});

const PORT = 4000;
app.listen(PORT, () => {
  console.log(`🛜 Backend listening on http://localhost:${PORT}`);
});
