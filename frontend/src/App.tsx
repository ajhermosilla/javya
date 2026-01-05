import { useState } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { ProtectedRoute } from './components/ProtectedRoute'
import { Layout } from './components/Layout'
import { SongList } from './pages/SongList'
import { SetlistList } from './pages/SetlistList'
import { AvailabilityPage } from './pages/AvailabilityPage'
import { SchedulingPage } from './pages/SchedulingPage'
import { LoginPage } from './pages/LoginPage'
import './App.css'

type Page = 'songs' | 'setlists' | 'availability' | 'scheduling';

function AppContent() {
  const [currentPage, setCurrentPage] = useState<Page>('songs');

  return (
    <Layout currentPage={currentPage} onNavigate={setCurrentPage}>
      {currentPage === 'songs' && <SongList />}
      {currentPage === 'setlists' && <SetlistList />}
      {currentPage === 'availability' && <AvailabilityPage />}
      {currentPage === 'scheduling' && <SchedulingPage />}
    </Layout>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <AppContent />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
