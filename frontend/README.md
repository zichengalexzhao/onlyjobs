# OnlyJobs Frontend

Modern React TypeScript application for the OnlyJobs AI-powered job application tracker. Features a beautiful Material-UI interface with Firebase authentication and real-time data visualization.

## 🚀 Features

- **🎨 Modern UI**: Clean Material-UI design with custom orange theme
- **🔐 Authentication**: Firebase Auth with Google OAuth and email/password login
- **📊 Dashboard**: Interactive job application tracking with charts and analytics
- **📱 Responsive**: Mobile-first design that works on all devices
- **⚡ Real-time**: Live data updates from Firestore
- **🎯 Type-Safe**: Full TypeScript implementation

## 🛠️ Tech Stack

- **Framework**: React 18 with TypeScript
- **UI Library**: Material-UI (MUI) v7
- **Authentication**: Firebase Auth
- **Charts**: Recharts for data visualization
- **Routing**: React Router v7
- **State Management**: React Context + Hooks
- **Build Tool**: Create React App
- **Package Manager**: npm

## 📁 Project Structure

```
src/
├── components/           # Reusable UI components
│   ├── LoadingSpinner.tsx
│   └── ProtectedRoute.tsx
├── contexts/            # React contexts
│   └── AuthContext.tsx  # Firebase authentication context
├── hooks/               # Custom React hooks
│   ├── useApi.ts
│   ├── useGmailSync.ts
│   └── useLocalStorage.ts
├── pages/               # Route components
│   ├── Dashboard.tsx    # Main application dashboard
│   ├── LandingPage.tsx  # Marketing landing page
│   ├── LoginPage.tsx    # Authentication page
│   ├── SignupPage.tsx   # User registration
│   ├── ForgotPassword.tsx
│   ├── VerifyEmail.tsx
│   ├── Settings.tsx
│   └── NotFound.tsx
├── services/            # External API services
│   ├── api.service.ts
│   ├── auth.service.ts
│   └── gmail.service.ts
├── types/               # TypeScript type definitions
│   ├── api.types.ts
│   ├── auth.types.ts
│   └── user.types.ts
├── utils/               # Utility functions
│   ├── auth.utils.ts
│   ├── date.utils.ts
│   └── validation.utils.ts
├── config/              # Configuration files
│   └── firebase.ts      # Firebase configuration
├── App.tsx              # Main application component
└── index.tsx            # Application entry point
```

## 🎨 Design System

### Color Palette
- **Primary Orange**: `#FF7043` - Main accent color for buttons and highlights
- **Light Orange**: `#FFD7B5` - Sidebar and card backgrounds
- **White**: `#FFFFFF` - Main background
- **Text**: `#202020` - Primary text color
- **Secondary Text**: `#666666` - Muted text

### Typography
- **Headings**: Roboto with bold weights (700, 600)
- **Body Text**: Roboto regular (400)
- **Hierarchy**: Clear size progression from h2 to body2

### Components
- **Cards**: Rounded corners (borderRadius: 3) with subtle shadows
- **Buttons**: Custom orange styling with hover effects
- **Forms**: Material-UI TextFields with orange focus states
- **Charts**: Recharts with custom orange color scheme

## 📊 Dashboard Features

### Summary Cards
- Total Applications count
- Interviews scheduled
- Offers received
- Rejections tracked

### Applications Table
- Company names and logos
- Application status with colored badges
- Date applied and last update timestamps
- Sortable and searchable interface

### Data Visualization
- **Bar Chart**: Applications by status
- **Pie Chart**: Status distribution
- **Responsive**: Charts adapt to screen size
- **Interactive**: Hover tooltips and animations

### Sidebar Navigation
- Dashboard overview
- Applications management
- Data visualizations
- User profile settings

## 🔐 Authentication Features

### Login Options
- **Google OAuth**: One-click sign-in with Google account
- **Apple Sign-In**: One-click sign-in with Apple ID
- **Email/Password**: Traditional authentication
- **Forgot Password**: Password reset via email
- **Remember Me**: Persistent login sessions

### Security Features
- Email verification required
- Protected routes with automatic redirects
- Secure token handling
- Session management

### User Experience
- Loading states for all auth operations
- Clear error messages with user-friendly text
- Automatic redirects after authentication
- Responsive forms that work on mobile

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn
- Firebase project with Authentication enabled

### Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Set up environment variables**:
   Create `.env.local` in the frontend root:
   ```env
   REACT_APP_FIREBASE_API_KEY=your_firebase_api_key
   REACT_APP_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
   REACT_APP_FIREBASE_PROJECT_ID=your_project_id
   REACT_APP_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
   REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
   REACT_APP_FIREBASE_APP_ID=your_app_id
   REACT_APP_API_BASE_URL=http://localhost:8080
   ```

3. **Start development server**:
   ```bash
   npm start
   ```
   Opens [http://localhost:3000](http://localhost:3000) in your browser.

### Available Scripts

- **`npm start`**: Runs the app in development mode
- **`npm test`**: Launches the test runner
- **`npm run build`**: Builds the app for production
- **`npm run eject`**: Ejects from Create React App (irreversible)

## 🧪 Testing

### Test Structure
- **Unit Tests**: Component and hook testing with React Testing Library
- **Integration Tests**: Authentication flow and API integration
- **E2E Tests**: User journey testing (planned)

### Running Tests
```bash
# Run all tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run specific test file
npm test Dashboard.test.tsx
```

## 📦 Build & Deployment

### Production Build
```bash
npm run build
```
Creates optimized production build in `/build` folder.

### Deployment Options
- **Firebase Hosting**: `firebase deploy`
- **Netlify**: Connect GitHub repository
- **Vercel**: Import project from Git
- **AWS S3**: Upload build folder

### Build Optimization
- Code splitting with React.lazy()
- Bundle size analysis
- Image optimization
- Service worker for caching

## 🔧 Configuration

### Firebase Setup
1. Create Firebase project at [console.firebase.google.com](https://console.firebase.google.com)
2. Enable Authentication with Google and Email providers
3. Enable Firestore database
4. Copy config to `src/config/firebase.ts`

### Material-UI Theme
Custom theme defined with:
- Orange color palette
- Roboto typography
- Custom component overrides
- Responsive breakpoints

### Router Configuration
Protected routes require authentication:
- `/dashboard` - Main application (requires email verification)
- `/settings` - User settings (requires email verification)
- `/verify-email` - Email verification page (requires login)

Public routes:
- `/` - Landing page
- `/login` - Authentication
- `/signup` - Registration
- `/forgot-password` - Password reset

## 🤝 Contributing

### Code Style
- TypeScript strict mode enabled
- ESLint with React and TypeScript rules
- Prettier for code formatting
- Husky pre-commit hooks

### Development Guidelines
1. Use TypeScript for all new files
2. Follow Material-UI component patterns
3. Implement proper error boundaries
4. Add loading states for async operations
5. Write unit tests for complex logic

### Pull Request Process
1. Create feature branch from `main`
2. Implement changes with tests
3. Update documentation if needed
4. Submit PR with clear description

## 📈 Performance

### Optimization Techniques
- React.memo for expensive components
- useMemo and useCallback for heavy computations
- Lazy loading for route components
- Image optimization and compression
- Bundle splitting and tree shaking

### Monitoring
- React DevTools for component analysis
- Firebase Performance Monitoring
- Web Vitals tracking
- Bundle analyzer for size optimization

## 🔍 Troubleshooting

### Common Issues

**Build failures**:
- Clear node_modules and reinstall dependencies
- Check TypeScript errors in console
- Verify environment variables are set

**Authentication issues**:
- Verify Firebase configuration
- Check browser console for auth errors
- Ensure Firebase Auth is enabled in console

**Styling issues**:
- Check Material-UI version compatibility
- Verify theme provider wraps application
- Clear browser cache and hard refresh

### Getting Help
- Check browser console for errors
- Review Firebase Auth documentation
- Check Material-UI component documentation
- Search GitHub issues for similar problems

## 🎯 Current Status & Next Steps

### ✅ Completed Features
- **Complete UI Suite**: All pages implemented with Material-UI
  - Landing page with marketing content
  - Login/Signup with Google and Apple OAuth
  - Email verification flow
  - Password reset functionality
  - Dashboard with charts and analytics
  - User settings and profile management
  - Terms of Service and Privacy Policy pages
  - Professional 404 error page

- **Authentication**: Full Firebase integration
  - Email/password, Google, and Apple sign-in
  - Protected routes and email verification
  - User session management

- **Design System**: Consistent Material-UI theming
  - Orange color palette (#FF7043)
  - Responsive design for all devices
  - Professional typography and spacing

### 🔄 Waiting for Backend APIs
The frontend is **complete and ready** but currently uses dummy data. Real integration requires:

1. **Job Applications API**:
   ```
   GET /api/applications - Fetch user's applications
   PUT /api/applications/:id - Update application status
   DELETE /api/applications/:id - Remove application
   ```

2. **Dashboard Analytics API**:
   ```
   GET /api/dashboard/stats - Summary statistics
   GET /api/analytics/trends - Application trends data
   ```

3. **Gmail Integration API**:
   ```
   GET /api/gmail/auth-url - OAuth URL
   POST /api/gmail/callback - Handle OAuth
   POST /api/sync/trigger - Manual sync
   GET /api/sync/status - Sync status
   ```

### 🚀 Next Frontend Tasks (After Backend APIs)
1. **Data Integration**: Replace dummy data with real API calls
2. **Real-time Updates**: Implement Firestore subscriptions
3. **Advanced Features**: Add search, filters, and export functionality
4. **Performance**: Add loading states and caching
5. **Testing**: Expand test coverage for all components

### ⚠️ Still Missing (Lower Priority)
- **Profile/Applications Pages**: Waiting for UI/UX designer drafts
- **Advanced Features**: Search, filters, export functionality  
- **Real Data Integration**: Needs backend REST APIs first

### 👨‍💻 Developer Handoff
**Backend Team**: Please implement the REST API endpoints listed above. The frontend is designed to consume these APIs and will work immediately once they're available.

**Frontend Team**: Focus on Profile/Applications pages once UI/UX designs are ready, then advanced features after core APIs are available.

## 📝 License

This project is proprietary and confidential.