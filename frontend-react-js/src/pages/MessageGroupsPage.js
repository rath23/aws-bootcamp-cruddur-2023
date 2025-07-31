import './MessageGroupsPage.css';
import React from 'react';
import { useNavigate } from 'react-router-dom';

import DesktopNavigation from '../components/DesktopNavigation';
import MessageGroupFeed from '../components/MessageGroupFeed';
import { checkAuth } from '../lib/CheckAuth';

const fetchWithAuth = async (url, signal) => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    throw new Error('No access token present');
  }

  const res = await fetch(url, {
    method: 'GET',
    signal,
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  const payload = await res.json().catch(() => null);
  if (!res.ok) {
    const err = new Error(`Request failed: ${res.status}`);
    err.status = res.status;
    err.payload = payload;
    throw err;
  }
  return payload;
};

export default function MessageGroupsPage() {
  const [messageGroups, setMessageGroups] = React.useState([]);
  const [user, setUser] = React.useState(undefined); // undefined = auth pending, null = unauthenticated
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);
  const [popped, setPopped] = React.useState([]);
  const navigate = useNavigate();

  // Run auth once, then load message groups if authenticated
  React.useEffect(() => {
    let cancelled = false;
    const init = async () => {
      try {
        await checkAuth(setUser); // existing function; it sets user or null
      } catch (e) {
        console.warn('checkAuth threw unexpectedly', e);
        setUser(null);
      }
    };
    init();

    return () => {
      cancelled = true;
    };
  }, []);

  // Fetch message groups after auth resolves
  React.useEffect(() => {
    // wait until checkAuth has run; user === undefined means still pending
    if (user === undefined) return;

    if (user === null) {
      // unauthenticated
      navigate('/signin');
      return;
    }

    const controller = new AbortController();
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const backendUrl = `${process.env.REACT_APP_BACKEND_URL}/api/message_groups`;
        const data = await fetchWithAuth(backendUrl, controller.signal);
        setMessageGroups(data);
      } catch (err) {
        if (err.name !== 'AbortError') {
          setError(err);
          console.error('Error loading message groups:', err, err.payload);
        }
      } finally {
        setLoading(false);
      }
    };
    load();
    return () => controller.abort();
  }, [user, navigate]);

  return (
    <article className="message-groups-page">
      <DesktopNavigation user={user && user !== null ? user : null} active="home" setPopped={setPopped} />

      <section className="message_groups">
        {user === undefined && <div className="status">Checking authentication...</div>}
        {user === null && <div className="status error">Not authenticated. Redirecting...</div>}

        {user && (
          <>
            {loading && <div className="status">Loading message groups...</div>}
            {error && (
              <div className="status error">
                Failed to load: {error.payload?.message || error.message}
                {error.payload && (
                  <pre style={{ fontSize: '0.7em', whiteSpace: 'pre-wrap' }}>
                    {JSON.stringify(error.payload, null, 2)}
                  </pre>
                )}
              </div>
            )}
            {!loading && !error && (
              <MessageGroupFeed message_groups={messageGroups} />
            )}
          </>
        )}
      </section>

      <div className="content">{/* Reserved for future UI (e.g., preview, details) */}</div>
    </article>
  );
}
