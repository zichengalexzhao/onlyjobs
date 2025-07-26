# Tableau Setup Guide for Dashboard Creator

Hi! Your dashboard embedding is almost working, but we need you to configure a few settings on your Tableau Cloud account to make it work properly.

## 🚨 Current Issue
We're getting a **401 Unauthorized** error when trying to embed your dashboard. This means there are some permission/configuration issues that need to be fixed on your Tableau side.

## ✅ What You Need to Do

### 1. **Update Connected App Domain Allowlist** (CRITICAL)
Your Connected App needs to allow our development domain.

**Steps:**
1. Go to your Tableau Cloud: `https://10ay.online.tableau.com/t/dgwang-bd5f29535a`
2. Click **Settings** (gear icon, top right)
3. Click **Connected Apps** in the left sidebar
4. Find your Connected App (should be named something like "OnlyJobs Dashboard" or similar)
5. Click **Edit** on that Connected App
6. In the **Domain Allowlist** field, add these domains (one per line):
   ```
   http://localhost:3000
   http://localhost:3001
   https://localhost:3000
   https://localhost:3001
   ```
7. Click **Save**

### 2. **Verify Connected App Settings**
Make sure your Connected App has these exact settings:

**Steps:**
1. In the same Connected App edit screen
2. Verify these settings:
   - **Name**: Whatever you named it (e.g., "OnlyJobs Dashboard")
   - **Domain Allowlist**: Should include the localhost domains from step 1
   - **Project Level**: Should be "All Projects" OR the specific project containing your dashboard
   - **Enabled**: Should be checked ✅

### 3. **Check Dashboard Permissions**
Make sure your dashboard is properly published and accessible.

**Steps:**
1. Go to your dashboard: `https://10ay.online.tableau.com/t/dgwang-bd5f29535a/views/Onlyjobs/Dashboard`
2. Verify you can see it when logged into your account
3. Check the **Permissions** on the dashboard:
   - Right-click on your dashboard in the "Views" or "Workbooks" section
   - Click **Permissions**
   - Make sure it allows **View** access (at minimum)

### 4. **Row-Level Security Setup** (If You Haven't Already)
This filters data so each user only sees their own job applications.

**Steps:**
1. Open your workbook in **Tableau Desktop**
2. Go to the **Data Source** tab (bottom left)
3. Create a **Calculated Field**:
   - Right-click in the Data pane → "Create Calculated Field"
   - Name: `User Filter`
   - Formula: `USERNAME() = [firebase_uid]` 
   - *(Replace `[firebase_uid]` with your actual Firebase UID column name)*
4. **Apply as Data Source Filter**:
   - In the Filters shelf (top right), click **Add...**
   - Select your `User Filter` calculated field
   - Select **True** (this option should be available now)
   - Click **OK**
5. **Republish** your workbook to Tableau Cloud

### 5. **Test Direct Access**
Please try accessing your dashboard directly and let us know what happens:

1. Go to: `https://10ay.online.tableau.com/t/dgwang-bd5f29535a/views/Onlyjobs/Dashboard`
2. Can you see the dashboard? (Yes/No)
3. If no, what error message do you see?

## 📝 **Information We Need Back**

Please answer these questions and send back:

1. **Connected App Domain Allowlist**: Did you successfully add the localhost domains? (Yes/No)

2. **Connected App Name**: What is the exact name of your Connected App?

3. **Direct Dashboard Access**: Can you access the dashboard directly at the URL above? (Yes/No)
   - If No: What error do you see?

4. **Row-Level Security**: 
   - Did you set up the User Filter calculated field? (Yes/No)
   - What is the exact name of your Firebase UID column in your data?
   - Can you select "True" for the filter now? (Yes/No)

5. **Project Information**: 
   - What project is your dashboard published to? (Default/Other name?)
   - Is your Connected App set to "All Projects" or a specific project?

## 🔧 **Common Issues & Solutions**

**Issue**: Can't find Connected Apps in Settings
- **Solution**: Make sure you're logged in as a site admin

**Issue**: Can't select "True" for the User Filter
- **Solution**: Republish your dashboard first, then go back to the data source filter

**Issue**: Dashboard shows "You don't have permission"
- **Solution**: Check dashboard permissions and make sure it's published correctly

## 📞 **If You Need Help**
If you get stuck on any step, please:
1. Take a screenshot of what you're seeing
2. Tell us exactly which step you're having trouble with
3. Copy any error messages you see

The integration is working perfectly on our end - we just need these Tableau Cloud settings configured correctly!

---

**Expected Result**: Once these are configured, users should be able to see your dashboard embedded in our React app, with each user only seeing their own data based on their Firebase UID.