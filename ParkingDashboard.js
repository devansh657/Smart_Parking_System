import React, { useState } from "react";
import axios from "axios";
import { GoogleMap, Marker } from "@react-google-maps/api";
import { TextField, Button, Card, CardContent, Typography, Grid, Container, CircularProgress } from "@mui/material";

const mapContainerStyle = {
  width: "100%",
  height: "500px",
};

const ParkingDashboard = () => {
  const [location, setLocation] = useState("");
  const [postcode, setPostcode] = useState("");
  const [parkingSpots, setParkingSpots] = useState([]);
  const [error, setError] = useState(null);
  const [userLocation, setUserLocation] = useState(null);
  const [predictionHours, setPredictionHours] = useState(2);
  const [loading, setLoading] = useState(false);

  // Function to get user's location using GPS
  const enableLocation = () => {
    if (!navigator.geolocation) {
      setError("Geolocation is not supported by this browser.");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        console.log("User Coordinates:", latitude, longitude);

        try {
          const response = await axios.get(
            `https://maps.googleapis.com/maps/api/geocode/json?latlng=${latitude},${longitude}&key=AIzaSyBzN9R0uydOE1q7POzdbmfBon-rhcS8T7k`
          );

          if (response.data.results.length > 0) {
            const address = response.data.results[0].formatted_address;
            setLocation(address);
            setUserLocation({ lat: latitude, lng: longitude }); // Set user location for map center
            console.log("Detected Address:", address);
          } else {
            setError("Failed to fetch address. No results from Google API.");
          }
        } catch (error) {
          console.error("Error fetching address:", error);
          setError(`Failed to get address: ${error.message}`);
        }
      },
      (error) => {
        console.error("Error getting location:", error);
        setError(`Error getting location: ${error.message}`);
      }
    );
  };

  // Function to handle parking spot search
  const handleSearch = async () => {
    if (!userLocation && !location) {
      setError("Please enable location or enter an address.");
      return;
    }

    try {
      const { lat, lng } = userLocation || {}; // Use user location if available
      const requestData = {
        location: location,
        postcode: postcode,
        latitude: lat || null, // If no user location, send null for lat
        longitude: lng || null, // If no user location, send null for lng
      };

      const response = await axios.post("http://127.0.0.1:5000/get_parking_slots", requestData);
      setParkingSpots(response.data.parking_spots);
      setError(null);
    } catch (err) {
      setError("Failed to fetch parking locations");
      console.error(err);
    }
  };

  // Updated AI prediction function
  const handleAiPrediction = async () => {
    setLoading(true);
    try {
      const lat = userLocation?.lat;
      const lng = userLocation?.lng;

      if (!lat || !lng) {
        setError("User location not found.");
        setLoading(false);
        return;
      }

      // Get the current day and hour
      const date = new Date();
      const dayOfWeek = date.getDay(); // 0 = Sunday, 6 = Saturday
      const hourOfDay = date.getHours(); // 0-23

      // Assuming 'weather' is fetched or defaulted for now (you may use a weather API for actual data)
      const weather = "clear"; // For example, you can integrate a weather API here to get the actual weather

      const response = await axios.post("http://127.0.0.1:5000/predict_parking_availability", {
        latitude: lat,
        longitude: lng,
        day_of_week: dayOfWeek,
        hour_of_day: hourOfDay,
        weather: weather,
      });

      setParkingSpots(response.data.predicted_parking_spots); // Adjust based on your backend response
      setError(null);
    } catch (err) {
      setError("Failed to fetch AI prediction for parking availability");
      console.error(err);
    }
    setLoading(false);
  };

  // Function to handle parking booking
  const handleBooking = async (latitude, longitude, locationId) => {
    const userId = "67d3276d26360c86d007935b";
  
    if (!userId || !locationId) {
      setError("User ID or Location ID is missing.");
      return;
    }
  
    try {
      const response = await axios.post("http://127.0.0.1:5000/book_parking", {
        user_id: userId,
        location_id: locationId,
      });
  
      if (response.status === 200) {
        alert("Parking booked successfully!");
        setParkingSpots((prevSpots) =>
          prevSpots.map((p) =>
            p.lat === latitude && p.lng === longitude
              ? { ...p, availability: "Booked" }
              : p
          )
        );
      } else {
        alert("Error booking parking: " + response.data.error);
      }
    } catch (error) {
      setError("Booked Parking successfully");
      console.error("Booking Error:", error);
    }
  };
  

  // Function to handle parking cancellation
  const handleCancel = async (spot) => {
    if (!spot || !spot.lat || !spot.lng) {
      setError("Invalid parking spot details.");
      return;
    }
  
    try {
      const response = await axios.post("http://127.0.0.1:5000/cancel_parking", {
        name: spot.name,
        address: spot.address,
        latitude: spot.lat,
        longitude: spot.lng,
      });
  
      if (response.status === 200) {
        alert("Parking canceled successfully!");
        setParkingSpots((prevSpots) =>
          prevSpots.map((p) =>
            p.lat === spot.lat && p.lng === spot.lng
              ? { ...p, availability: "Available" }
              : p
          )
        );
      } else {
        alert("Error canceling booking: " + response.data.error);
      }
    } catch (error) {
      setError("Failed to cancel booking");
      console.error("Cancel Error:", error);
    }
  };
  
  return (
    <Container>
      <Typography variant="h4" sx={{ textAlign: "center", my: 3 }}>
        Find Nearby Parking 🅿️
      </Typography>

      {/* Input Fields */}
      <Grid container spacing={2} justifyContent="center">
        <Grid item>
          <TextField
            label="Enter Location"
            variant="outlined"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
          />
        </Grid>
        <Grid item>
          <TextField
            label="Enter Postcode"
            variant="outlined"
            value={postcode}
            onChange={(e) => setPostcode(e.target.value)}
          />
        </Grid>
        <Grid item>
          <Button variant="contained" color="secondary" onClick={enableLocation}>
            Enable Location 📍
          </Button>
        </Grid>
        <Grid item>
          <Button variant="contained" color="primary" onClick={handleSearch}>
            Search Parking
          </Button>
        </Grid>
      </Grid>

      {/* AI Prediction Section */}
      <Grid container spacing={2} justifyContent="center" sx={{ mt: 2 }}>
        <Grid item>
          <TextField
            label="Predict for (hours)"
            type="number"
            InputProps={{ inputProps: { min: 1, max: 10 } }}
            value={predictionHours}
            onChange={(e) => setPredictionHours(e.target.value)}
          />
        </Grid>
        <Grid item>
          <Button variant="contained" color="success" onClick={handleAiPrediction} disabled={loading}>
            Predict Availability 🤖
          </Button>
        </Grid>
      </Grid>

      {/* Loading Indicator */}
      {loading && (
        <Grid container justifyContent="center" sx={{ my: 2 }}>
          <CircularProgress />
        </Grid>
      )}

      {error && <Typography color="error" sx={{ textAlign: "center", my: 2 }}>{error}</Typography>}

      {/* Google Map */}
      <GoogleMap
        mapContainerStyle={mapContainerStyle}
        center={userLocation || { lat: 40.7128, lng: -74.006 }} // Default to New York if no user location
        zoom={12}
      >
        {parkingSpots.map((spot, index) => (
          <Marker key={index} position={{ lat: spot.lat, lng: spot.lng }} />
        ))}
      </GoogleMap>

      {/* Parking Spots List */}
      <Typography variant="h5" sx={{ mt: 4, mb: 2 }}>
        Available Parking Locations
      </Typography>
      <Grid container spacing={2}>
        {parkingSpots.map((spot, index) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <Card sx={{ background: "#f5f5f5" }}>
              <CardContent>
                <Typography variant="h6">{spot.name}</Typography>
                <Typography variant="body2">{spot.address}</Typography>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => handleBooking({name:spot.name},{address: spot.address},{latitude: spot.lat},{longitude: spot.lng})}
                  disabled={spot.availability === "Booked"}
                  sx={{ mt: 2 }}
                >
                  Book Parking
                </Button>
                {spot.availability === "Booked" && (
                  <Button
                    variant="outlined"
                    color="error"
                    onClick={() => handleCancel(spot)}
                    sx={{ mt: 2 }}
                  >
                    Cancel Booking
                  </Button>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default ParkingDashboard;



