import React, { useState } from "react";
import {
  Box,
  CssBaseline,
  Typography,
  Button,
  Container,
  Card,
  CardContent,
  TextField,
  Divider,
  Alert,
  CircularProgress,
  Link
} from "@mui/material";
import { Google, Apple } from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { useAuth, getAuthErrorMessage } from "../contexts/AuthContext";
import { AuthError } from "firebase/auth";

const accent = "#FF7043";
const white = "#fff";
const textColor = "#202020";

export default function LoginPage() {
  const navigate = useNavigate();
  const { login, loginWithGoogle, loginWithApple } = useAuth();
  
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) {
      setError("Please fill in all fields");
      return;
    }

    try {
      setError("");
      setLoading(true);
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(getAuthErrorMessage(err as AuthError));
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    try {
      setError("");
      setLoading(true);
      await loginWithGoogle();
      navigate("/dashboard");
    } catch (err) {
      setError(getAuthErrorMessage(err as AuthError));
    } finally {
      setLoading(false);
    }
  };

  const handleAppleLogin = async () => {
    try {
      setError("");
      setLoading(true);
      await loginWithApple();
      navigate("/dashboard");
    } catch (err) {
      setError(getAuthErrorMessage(err as AuthError));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: "100vh", background: white, display: "flex", alignItems: "center" }}>
      <CssBaseline />
      
      <Container maxWidth="sm">
        {/* Header */}
        <Box sx={{ textAlign: "center", mb: 4 }}>
          <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 1, mb: 2 }}>
            <span role="img" aria-label="briefcase" style={{ fontSize: 32 }}>💼</span>
            <Typography variant="h4" sx={{ color: accent, fontWeight: 700 }}>
              OnlyJobs
            </Typography>
          </Box>
          <Typography variant="h5" sx={{ color: textColor, fontWeight: 600, mb: 1 }}>
            Welcome Back
          </Typography>
          <Typography variant="body1" sx={{ color: "#666" }}>
            Sign in to continue tracking your job applications
          </Typography>
        </Box>

        {/* Login Card */}
        <Card sx={{ bgcolor: white, borderRadius: 3, boxShadow: 3, overflow: "visible" }}>
          <CardContent sx={{ p: 4 }}>
            {error && (
              <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
                {error}
              </Alert>
            )}

            {/* Social Login Buttons */}
            <Button
              fullWidth
              variant="outlined"
              size="large"
              onClick={handleGoogleLogin}
              disabled={loading}
              startIcon={<Google />}
              sx={{
                borderColor: "#ddd",
                color: textColor,
                borderRadius: 2,
                py: 1.5,
                mb: 2,
                textTransform: "none",
                fontSize: 16,
                "&:hover": {
                  borderColor: accent,
                  background: `${accent}05`
                }
              }}
            >
              {loading ? <CircularProgress size={24} /> : "Continue with Google"}
            </Button>

            <Button
              fullWidth
              variant="outlined"
              size="large"
              onClick={handleAppleLogin}
              disabled={loading}
              startIcon={<Apple />}
              sx={{
                borderColor: "#ddd",
                color: textColor,
                borderRadius: 2,
                py: 1.5,
                mb: 3,
                textTransform: "none",
                fontSize: 16,
                "&:hover": {
                  borderColor: accent,
                  background: `${accent}05`
                }
              }}
            >
              {loading ? <CircularProgress size={24} /> : "Continue with Apple"}
            </Button>

            <Divider sx={{ my: 3 }}>
              <Typography variant="body2" sx={{ color: "#666", px: 2 }}>
                or
              </Typography>
            </Divider>

            {/* Email Login Form */}
            <Box component="form" onSubmit={handleEmailLogin}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
                sx={{
                  mb: 3,
                  "& .MuiOutlinedInput-root": {
                    borderRadius: 2,
                    "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
                      borderColor: accent,
                    },
                  },
                  "& .MuiInputLabel-root.Mui-focused": {
                    color: accent,
                  },
                }}
              />
              
              <TextField
                fullWidth
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                sx={{
                  mb: 3,
                  "& .MuiOutlinedInput-root": {
                    borderRadius: 2,
                    "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
                      borderColor: accent,
                    },
                  },
                  "& .MuiInputLabel-root.Mui-focused": {
                    color: accent,
                  },
                }}
              />

              <Button
                fullWidth
                type="submit"
                variant="contained"
                size="large"
                disabled={loading}
                sx={{
                  background: accent,
                  borderRadius: 2,
                  py: 1.5,
                  fontSize: 16,
                  textTransform: "none",
                  boxShadow: "none",
                  "&:hover": {
                    background: accent,
                    boxShadow: "none",
                  },
                }}
              >
                {loading ? <CircularProgress size={24} color="inherit" /> : "Sign In"}
              </Button>
            </Box>

            {/* Footer Links */}
            <Box sx={{ textAlign: "center", mt: 3 }}>
              <Link
                component="button"
                type="button"
                onClick={() => navigate("/forgot-password")}
                sx={{
                  color: accent,
                  textDecoration: "none",
                  fontSize: 14,
                  "&:hover": { textDecoration: "underline" }
                }}
              >
                Forgot your password?
              </Link>
            </Box>
          </CardContent>
        </Card>

        {/* Sign Up Link */}
        <Box sx={{ textAlign: "center", mt: 3 }}>
          <Typography variant="body2" sx={{ color: "#666" }}>
            Don't have an account?{" "}
            <Link
              component="button"
              type="button"
              onClick={() => navigate("/signup")}
              sx={{
                color: accent,
                textDecoration: "none",
                fontWeight: 600,
                "&:hover": { textDecoration: "underline" }
              }}
            >
              Sign up here
            </Link>
          </Typography>
        </Box>

        {/* Back to Home */}
        <Box sx={{ textAlign: "center", mt: 2 }}>
          <Link
            component="button"
            type="button"
            onClick={() => navigate("/")}
            sx={{
              color: "#666",
              textDecoration: "none",
              fontSize: 14,
              "&:hover": { textDecoration: "underline" }
            }}
          >
            ← Back to Home
          </Link>
        </Box>
      </Container>
    </Box>
  );
} 