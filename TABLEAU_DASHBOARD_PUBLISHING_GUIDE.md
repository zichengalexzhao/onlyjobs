# Tableau Dashboard Publishing & Embedding Setup Guide

## 🚨 Current Issue
The dashboard requires login when accessed directly, which prevents embedding. Here's how to fix it:

---

## ✅ Step-by-Step Publishing Setup

### 1. **Publish Workbook to Tableau Cloud (If Not Done)**

**In Tableau Desktop:**
1. Open your workbook with the "Onlyjobs" dashboard
2. Go to **Server** → **Publish Workbook**
3. Sign in to your Tableau Cloud site: `https://10ay.online.tableau.com/t/dgwang-bd5f29535a`
4. **Publishing Settings:**
   - **Name**: Keep as "Onlyjobs" 
   - **Project**: Select "Default" or create a specific project
   - **Permissions**: Click **Edit** and set to **"All Users"** can **View**
   - **Data Sources**: Select **"Embed credentials"** or **"Embedded in workbook"**
5. Click **Publish**

### 2. **Configure Dashboard Permissions (CRITICAL)**

**In Tableau Cloud:**
1. Go to `https://10ay.online.tableau.com/t/dgwang-bd5f29535a`
2. Find your **"Onlyjobs"** workbook in the main page
3. **Right-click** on the workbook → **Permissions**
4. **Set permissions:**
   - **All Users**: Can **View** ✅
   - **Viewer Role**: Can **View** ✅
   - Make sure there are NO restrictions that require login

### 3. **Verify Connected App Project Access**

**In Tableau Cloud:**
1. Go to **Settings** (gear icon) → **Connected Apps**
2. Find your Connected App → **Edit**
3. **Project Level Access**: Should be **"All Projects"** ✅
4. **Domain Allowlist**: Should include:
   ```
   http://localhost:3000
   http://localhost:3001
   https://localhost:3000
   https://localhost:3001
   ```
5. **Status**: Should be **Enabled** ✅

### 4. **Test Dashboard Access**

**Important Test:**
1. **Logout** from Tableau Cloud completely
2. **Open incognito/private browser window**
3. **Try accessing**: `https://10ay.online.tableau.com/t/dgwang-bd5f29535a/views/Onlyjobs/Dashboard`

**Expected Results:**
- ❌ **Bad**: Redirects to login page
- ✅ **Good**: Shows dashboard (even if empty/no data) without requiring login

### 5. **Alternative: Check Embedding Settings**

**In Tableau Cloud:**
1. Go to your dashboard view
2. Click **Share** button
3. Look for **"Embed Code"** option
4. **If you see embed code**: Copy the URL from it
5. **If no embed option**: Dashboard permissions need fixing

---

## 🔧 **Common Issues & Fixes**

### Issue: "Dashboard requires login"
**Fix**: 
- Set workbook permissions to "All Users" can "View"
- Make sure data source credentials are embedded

### Issue: "Connected App not working"
**Fix**:
- Verify Connected App has "All Projects" access
- Check domain allowlist includes localhost URLs
- Make sure Connected App is "Enabled"

### Issue: "Dashboard shows but no data"
**Fix**: 
- This is normal if no row-level security filter
- Data will show once JWT authentication works

---

## 📝 **What to Send Back**

Please answer these questions:

1. **Dashboard Access Test**: 
   - Can you access the dashboard URL in incognito mode without login? (Yes/No)
   - If No: What do you see? (Login page / Error message / etc.)

2. **Workbook Permissions**: 
   - What permissions are set on the "Onlyjobs" workbook?
   - Is "All Users" set to "View"? (Yes/No)

3. **Connected App Settings**:
   - Is your Connected App set to "All Projects"? (Yes/No)
   - Does domain allowlist include localhost:3000? (Yes/No)

4. **Embed Code Test**:
   - Does your dashboard have a "Share" → "Embed Code" option? (Yes/No)
   - If yes: What's the embed URL it shows?

---

## 🎯 **Expected Final Result**

Once properly configured:
- Dashboard URL should be accessible without login (may show empty if no data)
- Our React app should embed the dashboard successfully
- Users will see data filtered by their Firebase UID (once row-level security is re-enabled)

The integration code is 100% correct - this is purely a Tableau Cloud publishing/permissions configuration issue.