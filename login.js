import React, { useState } from "react";
import axios from "axios";
import { TextField, Button, Container, Typography, Box, CircularProgress } from "@mui/material";
import { useNavigate } from "react-router-dom";

const Login = ({ setToken }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();
  const API_URL = process.env.REACT_APP_BACKEND_URL || "http://127.0.0.1:5000";

  const handleLogin = async () => {
    setLoading(true);
    setError("");

    if (!email || !password) {
      setError("Please enter both email and password.");
      setLoading(false);
      return;
    }

    try {
      const response = await axios.post(`${API_URL}/auth/login`, { email, password });

      console.log("🔹 Login Response:", response.data);

      if (response.data.token) {
        const token = response.data.token;
        setToken(token);
        localStorage.setItem("token", token);
        navigate("/dashboard");
      } else {
        setError("Login failed. Please try again.");
      }
    } catch (err) {
      console.error("❌ Login Error:", err);
      if (err.response) {
        setError(err.response.data.error || "Invalid credentials. Please try again.");
      } else if (err.request) {
        setError("Server is unreachable. Please check your network.");
      } else {
        setError("An unexpected error occurred. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container>
      <Typography variant="h4" gutterBottom>
        Login
      </Typography>

      {error && (
        <Typography color="error" variant="body2">
          {error}
        </Typography>
      )}

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

      <Button
        variant="contained"
        color="primary"
        onClick={handleLogin}
        disabled={loading}
        fullWidth
      >
        {loading ? <CircularProgress size={24} color="inherit" /> : "Login"}
      </Button>
    </Container>
  );
};

export default Login;
