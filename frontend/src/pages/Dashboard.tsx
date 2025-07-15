import React, { useState } from "react";
import {
  Box,
  CssBaseline,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  Button,
  Avatar,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  CircularProgress,
  Alert,
  Snackbar,
  Menu,
  MenuItem,
  IconButton,
  Tooltip
} from "@mui/material";
import { 
  Home, 
  Assignment, 
  BarChart, 
  Person, 
  Mail, 
  Check, 
  Settings,
  AccountCircle,
  Logout,
  KeyboardArrowDown,
  Tune
} from "@mui/icons-material";
import { useAuth, getAuthErrorMessage } from "../contexts/AuthContext";
import { AuthError } from "firebase/auth";
import { useNavigate } from "react-router-dom";
import {
  PieChart,
  Pie,
  Cell,
  BarChart as BarChartC,
  Bar,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
  ResponsiveContainer
} from "recharts";

// Dummy Data
const summary = [
  { label: "Total Applications", value: 24 },
  { label: "Interviews", value: 8 },
  { label: "Offers", value: 3 },
  { label: "Rejections", value: 12 }
];

const applications = [
  { company: "Discord", position: "In Review", date: "03/30/2021", lastUpdate: "03/31/2021" },
  { company: "HubSpot", position: "Interview", date: "05/26/2021", lastUpdate: "07/23/2021" },
  { company: "Google", position: "Rejected", date: "05/27/2021", lastUpdate: "03/19/2021" },
  { company: "Netflix", position: "Applied", date: "06/14/2021", lastUpdate: "02/17/2021" },
  { company: "Microsoft", position: "Applied", date: "05/23/2021", lastUpdate: "03/17/2021" },
  { company: "Spotify", position: "Applied", date: "03/16/2021", lastUpdate: "03/17/2021" }
];

const statusData = [
  { name: "Applied", value: 4 },
  { name: "In Review", value: 1 },
  { name: "Interview", value: 1 },
  { name: "Rejected", value: 1 }
];

const COLORS = ["#FF7043", "#FFD7B5", "#FF5E62", "#F4B183"];

const barData = [
  { name: "Applied", count: 4 },
  { name: "In Review", count: 1 },
  { name: "Interview", count: 1 },
  { name: "Rejected", count: 1 }
];

// Theme colors
const sidebarColor = "#FFD7B5";
const accent = "#FF7043";
const white = "#fff";
const textColor = "#202020";

// Sidebar items
const sidebarItems = [
  { text: "Dashboard", icon: <Home />, active: true },
  { text: "Applications", icon: <Assignment />, active: false },
  { text: "Visualizations", icon: <BarChart />, active: false },
  { text: "Profile", icon: <Person />, active: false },
  { text: "Settings", icon: <Settings />, active: false }
];

export default function Dashboard() {
  const { connectGmail, isGmailConnected, currentUser, logout } = useAuth();
  const navigate = useNavigate();
  const [gmailLoading, setGmailLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: "", severity: "success" as "success" | "error" });
  const [profileMenuAnchor, setProfileMenuAnchor] = useState<null | HTMLElement>(null);

  const handleGmailConnect = async () => {
    try {
      setGmailLoading(true);
      await connectGmail();
      setSnackbar({
        open: true,
        message: "Gmail connected successfully! Your emails will now be processed for job application tracking.",
        severity: "success"
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: getAuthErrorMessage(err as AuthError),
        severity: "error"
      });
    } finally {
      setGmailLoading(false);
    }
  };

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setProfileMenuAnchor(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setProfileMenuAnchor(null);
  };

  const handleNavigateToSettings = () => {
    navigate('/settings');
    handleProfileMenuClose();
  };

  const handleSidebarNavigation = (item: { text: string }) => {
    if (item.text === 'Settings') {
      navigate('/settings');
    } else if (item.text === 'Dashboard') {
      // Already on dashboard
    } else {
      // Add other navigation logic here when those pages are implemented
      console.log(`Navigate to ${item.text}`);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/');
    } catch (error) {
      console.error('Logout failed:', error);
    }
    handleProfileMenuClose();
  };

  return (
    <Box sx={{ display: "flex", height: "100vh", background: white }}>
      <CssBaseline />

      {/* Sidebar */}
      <Drawer
        variant="permanent"
        sx={{
          width: 220,
          flexShrink: 0,
          "& .MuiDrawer-paper": {
            width: 220,
            boxSizing: "border-box",
            background: sidebarColor,
            borderRight: 0,
            color: textColor
          }
        }}
      >
        <Toolbar sx={{ my: 2 }}>
          <Box sx={{ fontWeight: 700, fontSize: 22, color: accent, ml: 1 }}>
            <span role="img" aria-label="briefcase">💼</span> 
          </Box>
        </Toolbar>
        <Divider />
        <List>
          {sidebarItems.map((item, idx) => (
            <ListItem key={item.text} disablePadding sx={{ mb: 1 }}>
              <ListItemButton 
                selected={item.active} 
                sx={{ borderRadius: 2 }}
                onClick={() => handleSidebarNavigation(item)}
              >
                <ListItemIcon sx={{ color: accent }}>{item.icon}</ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Drawer>

      {/* Main Area */}
      <Box sx={{ flexGrow: 1, p: 3 }}>
        {/* Top Bar */}
        <AppBar elevation={0} position="static" sx={{ background: "transparent", boxShadow: "none", mb: 2 }}>
          <Toolbar sx={{ display: "flex", justifyContent: "space-between", p: 0 }}>
            <Typography variant="h5" sx={{ color: textColor, fontWeight: 700 }}>
              Dashboard
            </Typography>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              {/* Gmail Connection Status with Quick Settings Access */}
              <Tooltip title={isGmailConnected ? "Gmail connected - Click to manage" : "Connect Gmail to sync job emails"}>
                <Button 
                  variant="contained" 
                  onClick={isGmailConnected ? handleNavigateToSettings : handleGmailConnect}
                  disabled={gmailLoading}
                  startIcon={
                    gmailLoading ? <CircularProgress size={20} color="inherit" /> : 
                    isGmailConnected ? <Check /> : <Mail />
                  }
                  endIcon={isGmailConnected ? <Tune sx={{ fontSize: 16 }} /> : null}
                  sx={{ 
                    background: isGmailConnected ? "#4caf50" : accent, 
                    borderRadius: 2, 
                    boxShadow: "none", 
                    textTransform: "none",
                    "&:hover": {
                      background: isGmailConnected ? "#388e3c" : accent,
                    },
                    "&:disabled": {
                      background: "#ccc",
                      color: "white"
                    }
                  }}
                >
                  {gmailLoading ? "Connecting..." : isGmailConnected ? "Gmail Connected" : "Connect Gmail"}
                </Button>
              </Tooltip>

              {/* User Profile Dropdown */}
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <IconButton
                  onClick={handleProfileMenuOpen}
                  sx={{ 
                    display: "flex", 
                    alignItems: "center", 
                    gap: 1,
                    color: textColor,
                    "&:hover": { bgcolor: "rgba(0,0,0,0.04)" }
                  }}
                >
                  <Avatar sx={{ bgcolor: accent, width: 36, height: 36 }}>
                    {currentUser?.displayName?.charAt(0) || currentUser?.email?.charAt(0) || 'U'}
                  </Avatar>
                  <KeyboardArrowDown sx={{ fontSize: 20 }} />
                </IconButton>
                
                <Menu
                  anchorEl={profileMenuAnchor}
                  open={Boolean(profileMenuAnchor)}
                  onClose={handleProfileMenuClose}
                  PaperProps={{
                    sx: {
                      mt: 1,
                      borderRadius: 2,
                      minWidth: 200,
                      boxShadow: "0 4px 20px rgba(0,0,0,0.1)"
                    }
                  }}
                >
                  <Box sx={{ px: 2, py: 1.5, borderBottom: "1px solid #eee" }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: textColor }}>
                      {currentUser?.displayName || "User"}
                    </Typography>
                    <Typography variant="body2" sx={{ color: "#666" }}>
                      {currentUser?.email}
                    </Typography>
                  </Box>
                  
                  <MenuItem onClick={handleNavigateToSettings} sx={{ py: 1.5 }}>
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <Settings sx={{ fontSize: 20 }} />
                    </ListItemIcon>
                    <ListItemText primary="Settings" />
                  </MenuItem>
                  
                  <MenuItem onClick={() => handleProfileMenuClose()} sx={{ py: 1.5 }}>
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <AccountCircle sx={{ fontSize: 20 }} />
                    </ListItemIcon>
                    <ListItemText primary="Profile" />
                  </MenuItem>
                  
                  <Divider />
                  
                  <MenuItem onClick={handleLogout} sx={{ py: 1.5, color: "#d32f2f" }}>
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <Logout sx={{ fontSize: 20, color: "#d32f2f" }} />
                    </ListItemIcon>
                    <ListItemText primary="Logout" />
                  </MenuItem>
                </Menu>
              </Box>
            </Box>
          </Toolbar>
        </AppBar>

        {/* Summary Cards */}
        <Box sx={{ display: "flex", gap: 2, mb: 3 }}>
          {summary.map((item, idx) => (
            <Card key={item.label} sx={{ flex: 1, bgcolor: "#FFF7F1", borderRadius: 3, boxShadow: "none" }}>
              <CardContent>
                <Typography sx={{ color: accent, fontWeight: 600 }}>{item.value}</Typography>
                <Typography variant="body2" sx={{ color: "#a17d54" }}>{item.label}</Typography>
              </CardContent>
            </Card>
          ))}
        </Box>

        {/* Gmail Connection Status Banner */}
        {!isGmailConnected && (
          <Card sx={{ 
            mb: 3, 
            bgcolor: "#fff3e0", 
            borderRadius: 3, 
            boxShadow: "none",
            border: "1px solid #ffcc02"
          }}>
            <CardContent sx={{ py: 2 }}>
              <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                  <Mail sx={{ color: "#f57c00" }} />
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: textColor }}>
                      Gmail Not Connected
                    </Typography>
                    <Typography variant="body2" sx={{ color: "#666" }}>
                      Connect your Gmail to automatically track job application emails
                    </Typography>
                  </Box>
                </Box>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <Button
                    variant="contained"
                    size="small"
                    onClick={handleGmailConnect}
                    disabled={gmailLoading}
                    sx={{
                      bgcolor: "#f57c00",
                      textTransform: "none",
                      "&:hover": { bgcolor: "#ef6c00" }
                    }}
                  >
                    Connect Now
                  </Button>
                  <Button
                    variant="text"
                    size="small"
                    onClick={handleNavigateToSettings}
                    sx={{
                      color: "#f57c00",
                      textTransform: "none",
                      "&:hover": { bgcolor: "rgba(245, 124, 0, 0.04)" }
                    }}
                  >
                    Settings
                  </Button>
                </Box>
              </Box>
            </CardContent>
          </Card>
        )}

        {/* Main Content Area */}
        <Box sx={{ display: "flex", gap: 3 }}>
          {/* Applications Table */}
          <Card sx={{ flex: 2, bgcolor: white, borderRadius: 3, p: 2, boxShadow: "none" }}>
            <Typography sx={{ mb: 1.5, fontWeight: 600, color: textColor }}>Applications</Typography>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Company</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Date Applied</TableCell>
                  <TableCell>Last Update</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {applications.map((row) => (
                  <TableRow key={row.company}>
                    <TableCell>{row.company}</TableCell>
                    <TableCell>
                      <Box sx={{ display: "inline-block", px: 1.5, py: 0.5, borderRadius: 2, background: "#FFF4E1", color: accent, fontWeight: 600, fontSize: 14 }}>
                        {row.position}
                      </Box>
                    </TableCell>
                    <TableCell>{row.date}</TableCell>
                    <TableCell>{row.lastUpdate}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>

          {/* Charts */}
          <Box sx={{ flex: 1, display: "flex", flexDirection: "column", gap: 2 }}>
            {/* Bar Chart */}
            <Card sx={{ bgcolor: white, borderRadius: 3, p: 2, boxShadow: "none", height: 180 }}>
              <Typography sx={{ fontWeight: 600, mb: 1, color: textColor }}>Applications by Status</Typography>
              <ResponsiveContainer width="100%" height="70%">
                <BarChartC data={barData}>
                  <XAxis dataKey="name" stroke="#999" />
                  <YAxis />
                  <RechartsTooltip />
                  <Bar dataKey="count" fill={accent} radius={[6, 6, 0, 0]} />
                </BarChartC>
              </ResponsiveContainer>
            </Card>
            {/* Pie Chart */}
            <Card sx={{ bgcolor: white, borderRadius: 3, p: 2, boxShadow: "none", height: 180 }}>
              <Typography sx={{ fontWeight: 600, mb: 1, color: textColor }}>Applications by Status</Typography>
              <ResponsiveContainer width="100%" height="70%">
                <PieChart>
                  <Pie data={statusData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={54} innerRadius={34}>
                    {statusData.map((entry, index) => (
                      <Cell key={index} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            </Card>
          </Box>
        </Box>
      </Box>

      {/* Snackbar for feedback */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleSnackbarClose} 
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
} 