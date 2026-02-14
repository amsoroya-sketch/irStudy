/**
 * Register Page
 */
import React, { useState, useEffect } from "react";
import { useNavigate, Link as RouterLink } from "react-router-dom";
import { Container, TextField, Button, Card, CardContent, Typography, Box, Alert, CircularProgress, FormControlLabel, Checkbox, Link, LinearProgress } from "@mui/material";
import { useAuth } from "../context/AuthContext";
import { validateEmail, validatePassword, validatePasswordMatch, validateFullName, validateAcceptTerms, getPasswordStrength } from "../utils/validation";

const Register: React.FC = () => {
  const navigate = useNavigate();
  const { register, isLoading, error, clearError, isAuthenticated } = useAuth();
  const [formData, setFormData] = useState({ email: "", password: "", confirmPassword: "", fullName: "", acceptTerms: false });
  const [formErrors, setFormErrors] = useState({ email: "", password: "", confirmPassword: "", fullName: "", acceptTerms: "" });
  const [touched, setTouched] = useState({ email: false, password: false, confirmPassword: false, fullName: false, acceptTerms: false });
  const [passwordStrength, setPasswordStrength] = useState({ score: 0, label: "Weak", color: "error" });
  const [successMessage, setSuccessMessage] = useState("");

  useEffect(() => {
    if (isAuthenticated) navigate("/dashboard");
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    if (error) clearError();
  }, [formData.email, formData.password, formData.fullName]);

  useEffect(() => {
    const strength = getPasswordStrength(formData.password);
    setPasswordStrength(strength);
  }, [formData.password]);

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
    } else if (name === "confirmPassword") {
      const err = validatePasswordMatch(formData.password, formData.confirmPassword);
      setFormErrors((prev) => ({ ...prev, confirmPassword: err || "" }));
    } else if (name === "fullName") {
      const err = validateFullName(formData.fullName);
      setFormErrors((prev) => ({ ...prev, fullName: err || "" }));
    }
  };

  const isFormValid = !formErrors.email && !formErrors.password && !formErrors.confirmPassword && !formErrors.fullName && !formErrors.acceptTerms && formData.email && formData.password && formData.confirmPassword && formData.fullName && formData.acceptTerms;

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!isFormValid) return;

    try {
      await register({ email: formData.email, password: formData.password, confirmPassword: formData.confirmPassword, fullName: formData.fullName, acceptTerms: formData.acceptTerms });
      setSuccessMessage("Registration successful! Redirecting to login...");
      setTimeout(() => navigate("/login"), 2000);
    } catch (err) {}
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
        <Card sx={{ width: "100%", boxShadow: 3 }}>
          <CardContent sx={{ padding: 4 }}>
            <Box sx={{ textAlign: "center", marginBottom: 3 }}>
              <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700 }}>Create Account</Typography>
              <Typography variant="body2" color="textSecondary">Join irStudy Medical Education</Typography>
            </Box>

            {error && <Alert severity="error" sx={{ marginBottom: 2 }}>{error}</Alert>}
            {successMessage && <Alert severity="success" sx={{ marginBottom: 2 }}>{successMessage}</Alert>}

            <form onSubmit={handleSubmit}>
              <TextField fullWidth label="Full Name" name="fullName" value={formData.fullName} onChange={handleChange} onBlur={handleBlur} error={touched.fullName && !!formErrors.fullName} helperText={touched.fullName && formErrors.fullName} margin="normal" disabled={isLoading} />

              <TextField fullWidth label="Email Address" name="email" type="email" value={formData.email} onChange={handleChange} onBlur={handleBlur} error={touched.email && !!formErrors.email} helperText={touched.email && formErrors.email} margin="normal" disabled={isLoading} autoComplete="email" />

              <TextField fullWidth label="Password" name="password" type="password" value={formData.password} onChange={handleChange} onBlur={handleBlur} error={touched.password && !!formErrors.password} helperText={touched.password && formErrors.password} margin="normal" disabled={isLoading} />

              {formData.password && <Box sx={{ marginTop: 1, marginBottom: 2 }}><Typography variant="caption">Password Strength: {passwordStrength.label}</Typography><LinearProgress variant="determinate" value={passwordStrength.score * 16.67} color={passwordStrength.color} /></Box>}

              <TextField fullWidth label="Confirm Password" name="confirmPassword" type="password" value={formData.confirmPassword} onChange={handleChange} onBlur={handleBlur} error={touched.confirmPassword && !!formErrors.confirmPassword} helperText={touched.confirmPassword && formErrors.confirmPassword} margin="normal" disabled={isLoading} />

              <FormControlLabel control={<Checkbox name="acceptTerms" checked={formData.acceptTerms} onChange={handleChange} disabled={isLoading} />} label="I accept the terms and conditions" sx={{ marginY: 2 }} />

              <Button fullWidth variant="contained" color="primary" type="submit" disabled={!isFormValid || isLoading} sx={{ marginY: 2, height: 48 }}>{isLoading ? <CircularProgress size={24} /> : "Create Account"}</Button>

              <Box sx={{ textAlign: "center", marginTop: 2 }}><Typography variant="body2" color="textSecondary">Already have an account? <Link component={RouterLink} to="/login" sx={{ textDecoration: "none", fontWeight: 600 }}>Sign in here</Link></Typography></Box>
            </form>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
};

export default Register;
