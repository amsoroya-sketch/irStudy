/**
 * Login Page
 */
import React, { useState, useEffect } from "react";
import { useNavigate, Link as RouterLink } from "react-router-dom";
import { Container, TextField, Button, Card, CardContent, Typography, Box, Alert, CircularProgress, FormControlLabel, Checkbox, Link } from "@mui/material";
import { useAuth } from "../context/AuthContext";
import { validateEmail, validatePassword } from "../utils/validation";

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login, isLoading, error, clearError, isAuthenticated } = useAuth();
  const [formData, setFormData] = useState({ email: "", password: "", rememberMe: false });
  const [formErrors, setFormErrors] = useState({ email: "", password: "" });
  const [touched, setTouched] = useState({ email: false, password: false });

  useEffect(() => {
    document.title = 'Login - AMC Clinical Exam';
  }, []);

  useEffect(() => {
    if (isAuthenticated) navigate("/dashboard");
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    if (error) clearError();
  }, [formData.email, formData.password]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, type, checked, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: type === "checkbox" ? checked : value }));
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    const { name } = e.target;
    setTouched((prev) => ({ ...prev, [name]: true }));
    if (name === "email") {
      const err = validateEmail(formData.email);
      setFormErrors((prev) => ({ ...prev, email: err || "" }));
    } else if (name === "password") {
      const err = validatePassword(formData.password);
      setFormErrors((prev) => ({ ...prev, password: err || "" }));
    }
  };

  const isFormValid = !formErrors.email && !formErrors.password && formData.email && formData.password;

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!isFormValid) return;
    try {
      await login({ email: formData.email, password: formData.password, rememberMe: formData.rememberMe });
      // Navigation handled by useEffect watching isAuthenticated (lines 21-23)
    } catch (err) {}
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
        <Card sx={{ width: "100%", boxShadow: 3 }}>
          <CardContent sx={{ padding: 4 }}>
            <Box sx={{ textAlign: "center", marginBottom: 3 }}>
              <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700 }}>irStudy</Typography>
              <Typography variant="body2" color="textSecondary">Medical Education Platform</Typography>
            </Box>
            {error && <Alert severity="error" sx={{ marginBottom: 2 }}>{error}</Alert>}
            <form onSubmit={handleSubmit}>
              <TextField fullWidth label="Email Address" name="email" type="email" value={formData.email} onChange={handleChange} onBlur={handleBlur} error={touched.email && !!formErrors.email} helperText={touched.email && formErrors.email} margin="normal" disabled={isLoading} autoComplete="email" />
              <TextField fullWidth label="Password" name="password" type="password" value={formData.password} onChange={handleChange} onBlur={handleBlur} error={touched.password && !!formErrors.password} helperText={touched.password && formErrors.password} margin="normal" disabled={isLoading} autoComplete="current-password" />
              <FormControlLabel control={<Checkbox name="rememberMe" checked={formData.rememberMe} onChange={handleChange} disabled={isLoading} />} label="Remember me" sx={{ marginY: 1 }} />
              <Box sx={{ textAlign: "right", marginBottom: 2 }}><Link component={RouterLink} to="/forgot-password" variant="body2" sx={{ textDecoration: "none" }}>Forgot password?</Link></Box>
              <Button fullWidth variant="contained" color="primary" type="submit" disabled={!isFormValid || isLoading} sx={{ marginY: 2, height: 48 }}>{isLoading ? <CircularProgress size={24} /> : "Sign In"}</Button>
              <Box sx={{ textAlign: "center", marginTop: 2 }}><Typography variant="body2" color="textSecondary">Don't have an account? <Link component={RouterLink} to="/register" sx={{ textDecoration: "none", fontWeight: 600 }}>Sign up here</Link></Typography></Box>
            </form>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
};

export default Login;
