import React from "react";
import { useNavigate } from "react-router-dom";
import { AppBar, Toolbar, Button, Typography } from "@mui/material";

const Navbar = ({ setToken }) => {
  const navigate = useNavigate();
  const token = localStorage.getItem("token"); // Get token from local storage

  const handleLogout = () => {
    localStorage.removeItem("token"); // Clear token from localStorage
    setToken(null); // Reset token state in the parent component
    navigate("/login"); // Redirect to login page
  };

  const handleLogin = () => {
    navigate("/login"); // Navigate to login page if not logged in
  };

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" style={{ flexGrow: 1 }}>
          Smart Parking System
        </Typography>
        
        {/* Conditional rendering for Login/Logout buttons */}
        {token ? (
          <Button color="inherit" onClick={handleLogout}>
            Logout
          </Button>
        ) : (
          <Button color="inherit" onClick={handleLogin}>
            Login
          </Button>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
