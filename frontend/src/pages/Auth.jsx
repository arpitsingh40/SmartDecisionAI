import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Sparkles, Mail, Lock, User as UserIcon, ArrowRight, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { useAuth } from '@/context/AuthContext';

const Auth = () => {
  const { login, signup } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mode, setMode] = useState(new URLSearchParams(location.search).get('mode') === 'signup' ? 'signup' : 'login');
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({ email: '', password: '', name: '' });

  const onChange = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const validate = () => {
    if (!form.email || !/.+@.+\..+/.test(form.email)) return 'Enter a valid email address';
    if (!form.password || form.password.length < 6) return 'Password must be at least 6 characters';
    return null;
  };

  const submit = async (e) => {
    e.preventDefault();
    const err = validate();
    if (err) {
      toast.error(err);
      return;
    }
    setLoading(true);
    try {
      if (mode === 'signup') {
        await signup({ email: form.email.trim(), password: form.password, name: form.name?.trim() || undefined });
        toast.success('Welcome aboard!');
      } else {
        await login({ email: form.email.trim(), password: form.password });
        toast.success('Welcome back');
      }
      const from = location.state?.from || '/';
      navigate(from, { replace: true });
    } catch (e) {
      const msg = e?.response?.data?.detail || e.message || 'Authentication failed';
      toast.error(typeof msg === 'string' ? msg : 'Auth failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="relative mx-auto flex min-h-[calc(100vh-56px)] w-full max-w-md items-center justify-center px-4 py-10" data-testid="auth-page">
      <div className="hero-glow pointer-events-none absolute inset-0 -z-10" />
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full"
      >
        <Card className="rounded-2xl border-border/70 bg-card/60 p-6 shadow-[var(--shadow-2)] backdrop-blur sm:p-8">
          <div className="mb-6 flex items-center gap-2">
            <div className="grid h-9 w-9 place-items-center rounded-lg bg-primary/15 text-primary ring-1 ring-primary/30">
              <Sparkles className="h-4 w-4" />
            </div>
            <div className="font-display text-lg font-semibold tracking-tight">
              Smart Decision <span className="text-primary">AI</span>
            </div>
          </div>

          <Tabs value={mode} onValueChange={setMode} className="w-full">
            <TabsList className="mb-6 w-full">
              <TabsTrigger value="login" className="flex-1" data-testid="auth-tab-login">Log in</TabsTrigger>
              <TabsTrigger value="signup" className="flex-1" data-testid="auth-tab-signup">Sign up</TabsTrigger>
            </TabsList>

            <TabsContent value="login">
              <h1 className="text-2xl font-semibold tracking-tight">Welcome back</h1>
              <p className="mt-1 text-sm text-muted-foreground">Log in to access your saved decisions.</p>
            </TabsContent>
            <TabsContent value="signup">
              <h1 className="text-2xl font-semibold tracking-tight">Create your account</h1>
              <p className="mt-1 text-sm text-muted-foreground">Save decisions, revisit them, and export reports.</p>
            </TabsContent>
          </Tabs>

          <form onSubmit={submit} className="mt-6 space-y-4">
            {mode === 'signup' && (
              <div>
                <Label htmlFor="name" className="text-xs uppercase tracking-wider text-muted-foreground">Name (optional)</Label>
                <div className="relative mt-1">
                  <UserIcon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="name"
                    type="text"
                    className="pl-10"
                    placeholder="Jane Doe"
                    value={form.name}
                    onChange={onChange('name')}
                    data-testid="auth-name-input"
                    autoComplete="name"
                  />
                </div>
              </div>
            )}
            <div>
              <Label htmlFor="email" className="text-xs uppercase tracking-wider text-muted-foreground">Email</Label>
              <div className="relative mt-1">
                <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="email"
                  type="email"
                  className="pl-10"
                  placeholder="you@example.com"
                  value={form.email}
                  onChange={onChange('email')}
                  data-testid="auth-email-input"
                  autoComplete="email"
                  required
                />
              </div>
            </div>
            <div>
              <Label htmlFor="password" className="text-xs uppercase tracking-wider text-muted-foreground">Password</Label>
              <div className="relative mt-1">
                <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="password"
                  type="password"
                  className="pl-10"
                  placeholder={mode === 'signup' ? 'At least 6 characters' : 'Your password'}
                  value={form.password}
                  onChange={onChange('password')}
                  data-testid="auth-password-input"
                  autoComplete={mode === 'signup' ? 'new-password' : 'current-password'}
                  required
                />
              </div>
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="h-11 w-full gap-2"
              data-testid="auth-submit-button"
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <ArrowRight className="h-4 w-4" />}
              {loading ? 'Please wait…' : mode === 'signup' ? 'Create account' : 'Log in'}
            </Button>
          </form>

          <div className="mt-6 text-center text-sm text-muted-foreground">
            or
            <Link to="/wizard" className="ml-2 font-medium text-primary underline-offset-4 hover:underline" data-testid="auth-guest-link">
              continue as guest
            </Link>
          </div>
        </Card>
      </motion.div>
    </section>
  );
};

export default Auth;
