import { Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import Jobs from './pages/Jobs';
import Applications from './pages/Applications';
import Digest from './pages/Digest';

function App() {
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    // Check for stored user ID
    const storedUserId = localStorage.getItem('jobcopilot_user_id');
    if (storedUserId) {
      setUserId(storedUserId);
    }
  }, []);

  const handleProfileCreated = (newUserId: string) => {
    localStorage.setItem('jobcopilot_user_id', newUserId);
    setUserId(newUserId);
  };

  const handleLogout = () => {
    localStorage.removeItem('jobcopilot_user_id');
    setUserId(null);
  };

  return (
    <Layout userId={userId} onLogout={handleLogout}>
      <Routes>
        <Route
          path="/"
          element={
            userId ? (
              <Dashboard userId={userId} />
            ) : (
              <Navigate to="/profile" replace />
            )
          }
        />
        <Route
          path="/profile"
          element={
            <Profile
              userId={userId}
              onProfileCreated={handleProfileCreated}
            />
          }
        />
        <Route
          path="/jobs"
          element={
            userId ? (
              <Jobs userId={userId} />
            ) : (
              <Navigate to="/profile" replace />
            )
          }
        />
        <Route
          path="/applications"
          element={
            userId ? (
              <Applications userId={userId} />
            ) : (
              <Navigate to="/profile" replace />
            )
          }
        />
        <Route
          path="/digest"
          element={
            userId ? (
              <Digest userId={userId} />
            ) : (
              <Navigate to="/profile" replace />
            )
          }
        />
      </Routes>
    </Layout>
  );
}

export default App;
