import React, { useState } from "react";
import axios from "axios";
import { TextField, Button, Container, Typography, Box } from "@mui/material";

const Register = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  // Handle registration
  const handleRegister = async () => {
    setLoading(true); // Set loading state to true
    setMessage(""); // Reset any previous message

    try {
      // Make POST request to backend to register user
      const response = await axios.post("http://127.0.0.1:5000/register", { email, password });

      // Display success message
      setMessage("User registered successfully! You can now log in.");
    } catch (err) {
      // Check if error is due to missing fields or backend issues
      if (err.response && err.response.data && err.response.data.error) {
        setMessage(err.response.data.error);
      } else {
        setMessage("Error registering user. Please try again.");
      }
    } finally {
      setLoading(false); // Set loading state to false after request
    }
  };

  return (
    <Container>
      <Typography variant="h4" gutterBottom>
        Register
      </Typography>

      {/* Display success or error message */}
      {message && (
        <Typography color={message.includes("successfully") ? "green" : "red"}>{message}</Typography>
      )}

      {/* Email input */}
      <Box mb={2}>
        <TextField
          label="Email"
          fullWidth
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          variant="outlined"
          required
        />
      </Box>

      {/* Password input */}
      <Box mb={2}>
        <TextField
          label="Password"
          type="password"
          fullWidth
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          variant="outlined"
          required
        />
      </Box>

      {/* Register Button */}
      <Button
        variant="contained"
        color="primary"
        onClick={handleRegister}
        disabled={loading} // Disable the button when loading
      >
        {loading ? "Registering..." : "Register"}
      </Button>
    </Container>
  );
};

export default Register;
