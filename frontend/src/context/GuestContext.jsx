import React, { createContext, useContext, useEffect, useState } from 'react';
import { ensureGuestSession } from '@/lib/api';

const GuestContext = createContext({ guestId: null, ready: false });

export const GuestProvider = ({ children }) => {
  const [guestId, setGuestId] = useState(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    (async () => {
      const id = await ensureGuestSession();
      setGuestId(id);
      setReady(true);
    })();
  }, []);

  return (
    <GuestContext.Provider value={{ guestId, ready }}>
      {children}
    </GuestContext.Provider>
  );
};

export const useGuest = () => useContext(GuestContext);
