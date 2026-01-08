// src/components/ParkingForm.js
import React, { useState } from 'react';
import axios, { HttpStatusCode } from 'axios';
import './ParkingForm.css';

const ParkingForm = () => {
  const [location, setLocation] = useState('');
  const [postcode, setPostcode] = useState('');
  const [parkingData, setParkingData] = useState(null);
  const [error, setError] = useState(null);

  const handleEnableLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const { latitude, longitude } = position.coords;
          try {
            const response = await axios.get(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`);
            setLocation(response.data.display_name || '');
            setPostcode(response.data.address.postcode || '');
          } catch (err) {
            setError('Failed to retrieve location data');
            console.error(err);
          }
        },
        () => setError('Location access denied')
      );
    } else {
      setError('Geolocation is not supported by this browser');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!location || !postcode) {
      setError('Please provide both location and postcode');
      return;
    }

    try {
      const response = await axios.post("http://127.0.0.1:5000/get_parking_slots", {
        location,
        postcode
      });
      setParkingData(response.data);
      setError(null);
    } catch (err) {

      setError('Failed to fetch parking data');
      console.error(err);
    }
  };

  return (
    <div className="parking-form-container">
      <h2>Find Nearby Parking</h2>
      <form onSubmit={handleSubmit} className="parking-form">
        <div className="input-group">
          <label>Location:</label>
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="input-field"
            placeholder="Enter your address"
            name="longitude"
            id="longitude"
          />
        </div>
        <div className="input-group">
          <label>Postcode:</label>
          <input
            type="text"
            value={postcode}
            onChange={(e) => setPostcode(e.target.value)}
            className="input-field"
            placeholder="Enter postcode"
            name="latitude"
            id="latitude"
          />
        </div>
        <button type="button" onClick={handleEnableLocation} className="enable-location-button">
          Enable Current Location
        </button>
        <button type="submit" className="submit-button">Get Parking Slots</button>
      </form>

      {error && <p className="error-message">{error}</p>}

      {parkingData && (
        <div className="parking-info">
          <h3>Parking Slots Prediction</h3>
          <pre>{JSON.stringify(parkingData, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default ParkingForm;
