import { useEffect } from 'react';
import '@/App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from '@/components/ui/sonner';
import { ThemeProvider } from '@/components/ThemeProvider';
import { GuestProvider } from '@/context/GuestContext';
import { AuthProvider } from '@/context/AuthContext';
import { ensureGuestSession } from '@/lib/api';

import TopNav from '@/components/TopNav';
import Landing from '@/pages/Landing';
import Wizard from '@/pages/Wizard';
import Results from '@/pages/Results';
import SavedDecisions from '@/pages/SavedDecisions';
import DecisionDetail from '@/pages/DecisionDetail';
import Auth from '@/pages/Auth';

function App() {
  useEffect(() => {
    ensureGuestSession().catch(() => {});
  }, []);

  return (
    <ThemeProvider>
      <AuthProvider>
        <GuestProvider>
          <BrowserRouter>
            <div className="min-h-screen bg-background text-foreground app-noise relative">
              <TopNav />
              <main className="relative z-10">
                <Routes>
                  <Route path="/" element={<Landing />} />
                  <Route path="/wizard" element={<Wizard />} />
                  <Route path="/results" element={<Results />} />
                  <Route path="/saved" element={<SavedDecisions />} />
                  <Route path="/saved/:id" element={<DecisionDetail />} />
                  <Route path="/auth" element={<Auth />} />
                </Routes>
              </main>
              <Toaster position="top-right" richColors />
            </div>
          </BrowserRouter>
        </GuestProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
