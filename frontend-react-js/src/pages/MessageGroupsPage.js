import './MessageGroupsPage.css';
import React from "react";
import { useNavigate } from 'react-router-dom';
import DesktopNavigation from '../components/DesktopNavigation';
import MessageGroupFeed from '../components/MessageGroupFeed';
import {checkAuth} from '../lib/CheckAuth';



export default function MessageGroupsPage() {
  const [messageGroups, setMessageGroups] = React.useState([]);
  const [popped, setPopped] = React.useState([]);
  const [user, setUser] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);
  const navigate = useNavigate();
  const dataFetchedRef = React.useRef(false);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No access token');
      }

      const backend_url = `${process.env.REACT_APP_BACKEND_URL}/api/message_groups`;
      const res = await fetch(backend_url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        }
      });

      // Handle non-JSON responses
      const contentType = res.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const text = await res.text();
        throw new Error(`Expected JSON but got: ${text.substring(0, 100)}`);
      }

      const data = await res.json();

      if (!res.ok) {
        const error = new Error(data.message || `HTTP ${res.status}`);
        error.status = res.status;
        error.details = data;
        throw error;
      }

      setMessageGroups(data);
    } catch (err) {
      console.error('Failed to load message groups:', err);
      setError(err);
      
      // Handle specific error cases
      if (err.status === 401) {
        navigate('/signin');
      } else if (err.status === 422) {
        console.error('Validation errors:', err.details);
      }
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    if (dataFetchedRef.current) return;
    dataFetchedRef.current = true;

    const init = async () => {
      await checkAuth(setUser);
      await loadData();
    };
    init();
  }, [navigate]);

  return (
    <article>
      <DesktopNavigation user={user} active={'home'} setPopped={setPopped} />
      <section className='message_groups'>
        {loading && <div className="loading">Loading messages...</div>}
        {error && (
          <div className="error">
            Error: {error.message}
            {error.status === 422 && (
              <pre>{JSON.stringify(error.details, null, 2)}</pre>
            )}
          </div>
        )}
        {!loading && !error && (
          <MessageGroupFeed message_groups={messageGroups} />
        )}
      </section>
    </article>
  );
}