import React from 'react';
import { Link, NavLink, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Moon, Sun, Sparkles } from 'lucide-react';
import { useTheme } from '@/components/ThemeProvider';
import { motion } from 'framer-motion';

const TopNav = () => {
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();

  return (
    <header
      className="sticky top-0 z-50 h-14 border-b border-border/70 backdrop-blur supports-[backdrop-filter]:bg-background/70"
      data-testid="top-nav"
    >
      <div className="mx-auto flex h-full w-full max-w-6xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link to="/" className="flex items-center gap-2 group" data-testid="nav-logo-link">
          <motion.span
            initial={{ rotate: -8, scale: 0.8, opacity: 0 }}
            animate={{ rotate: 0, scale: 1, opacity: 1 }}
            transition={{ duration: 0.4 }}
            className="grid h-8 w-8 place-items-center rounded-lg bg-primary/12 text-primary ring-1 ring-primary/30"
          >
            <Sparkles className="h-4 w-4" />
          </motion.span>
          <span className="font-display text-base font-semibold tracking-tight">
            Smart Decision <span className="text-primary">AI</span>
          </span>
        </Link>

        <nav className="hidden items-center gap-1 sm:flex">
          <NavLink
            to="/wizard"
            className={({ isActive }) =>
              `rounded-md px-3 py-1.5 text-sm transition-colors ${
                isActive ? 'text-foreground' : 'text-muted-foreground hover:text-foreground'
              }`
            }
            data-testid="nav-new-decision-link"
          >
            New Decision
          </NavLink>
          <NavLink
            to="/saved"
            className={({ isActive }) =>
              `rounded-md px-3 py-1.5 text-sm transition-colors ${
                isActive ? 'text-foreground' : 'text-muted-foreground hover:text-foreground'
              }`
            }
            data-testid="nav-saved-decisions-link"
          >
            Saved
          </NavLink>
        </nav>

        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            aria-label="Toggle theme"
            data-testid="theme-toggle"
            className="h-9 w-9"
          >
            {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>
          {location.pathname !== '/wizard' && (
            <Link to="/wizard" data-testid="nav-start-cta-link">
              <Button className="h-9" data-testid="nav-start-cta-button">
                Start
              </Button>
            </Link>
          )}
        </div>
      </div>
    </header>
  );
};

export default TopNav;
