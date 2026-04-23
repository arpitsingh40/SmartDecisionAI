import React, { useState } from 'react';
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel,
  DropdownMenuSeparator, DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Moon, Sun, Sparkles, LogOut, User, LogIn, UserPlus } from 'lucide-react';
import { useTheme } from '@/components/ThemeProvider';
import { useAuth } from '@/context/AuthContext';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

const initials = (nameOrEmail) => {
  if (!nameOrEmail) return '?';
  const s = nameOrEmail.split('@')[0];
  const parts = s.replace(/[^a-zA-Z0-9\s]/g, ' ').trim().split(/\s+/).slice(0, 2);
  return parts.map((p) => p[0]?.toUpperCase() || '').join('') || s[0].toUpperCase();
};

const TopNav = () => {
  const { theme, toggleTheme } = useTheme();
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    toast.success('Logged out');
    navigate('/');
  };

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

          {user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="h-9 gap-2 px-2" data-testid="nav-user-menu-button">
                  <span className="grid h-7 w-7 place-items-center rounded-full bg-primary/15 text-xs font-semibold text-primary ring-1 ring-primary/30">
                    {initials(user.name || user.email)}
                  </span>
                  <span className="hidden max-w-[120px] truncate text-sm sm:inline">{user.name || user.email}</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel className="truncate">
                  <div className="text-xs text-muted-foreground">Signed in as</div>
                  <div className="truncate text-sm font-medium">{user.email}</div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link to="/saved" data-testid="nav-user-menu-saved">
                    <User className="mr-2 h-4 w-4" /> My decisions
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} data-testid="nav-user-menu-logout">
                  <LogOut className="mr-2 h-4 w-4" /> Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <>
              <Link to="/auth?mode=login" className="hidden sm:block" data-testid="nav-login-link">
                <Button variant="ghost" className="h-9 gap-1.5">
                  <LogIn className="h-4 w-4" /> Log in
                </Button>
              </Link>
              <Link to="/auth?mode=signup" data-testid="nav-signup-link">
                <Button className="h-9 gap-1.5">
                  <UserPlus className="h-4 w-4" /> Sign up
                </Button>
              </Link>
            </>
          )}

          {location.pathname !== '/wizard' && user && (
            <Link to="/wizard" data-testid="nav-start-cta-link" className="hidden lg:block">
              <Button variant="secondary" className="h-9" data-testid="nav-start-cta-button">
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
