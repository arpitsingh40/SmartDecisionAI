import React, { createContext, useContext, useEffect, useState } from 'react';

const ThemeContext = createContext({ theme: 'dark', setTheme: () => {}, toggleTheme: () => {} });

const THEME_KEY = 'sda_theme';

// Read stored theme synchronously to avoid a flash / wrong initial class
const readInitialTheme = () => {
  if (typeof window === 'undefined') return 'dark';
  try {
    const stored = window.localStorage.getItem(THEME_KEY);
    if (stored === 'light' || stored === 'dark') return stored;
  } catch {}
  return 'dark'; // dark-first default
};

// Apply theme class to <html> immediately on page load (before React mounts fully)
if (typeof document !== 'undefined') {
  const initial = readInitialTheme();
  if (initial === 'dark') document.documentElement.classList.add('dark');
  else document.documentElement.classList.remove('dark');
}

export const ThemeProvider = ({ children }) => {
  const [theme, setThemeState] = useState(readInitialTheme);

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') root.classList.add('dark');
    else root.classList.remove('dark');
    try {
      window.localStorage.setItem(THEME_KEY, theme);
    } catch {}
  }, [theme]);

  const setTheme = (t) => setThemeState(t);
  const toggleTheme = () => setThemeState((t) => (t === 'dark' ? 'light' : 'dark'));

  return (
    <ThemeContext.Provider value={{ theme, setTheme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => useContext(ThemeContext);
