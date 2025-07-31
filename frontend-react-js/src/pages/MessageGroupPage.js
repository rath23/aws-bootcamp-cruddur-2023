import './MessageGroupPage.css';
import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';

import { checkAuth } from '../lib/CheckAuth';
import DesktopNavigation from '../components/DesktopNavigation';
import MessageGroupFeed from '../components/MessageGroupFeed';
import MessagesFeed from '../components/MessageFeed';
import MessagesForm from '../components/MessageForm';

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
    const error = new Error(`Request failed with status ${res.status}`);
    error.status = res.status;
    error.payload = payload;
    throw error;
  }
  return payload;
};

export default function MessageGroupPage() {
  const { message_group_uuid } = useParams();
  const navigate = useNavigate();

  const [messageGroups, setMessageGroups] = React.useState([]);
  const [messages, setMessages] = React.useState([]);
  const [user, setUser] = React.useState(undefined); // undefined = auth pending, null = unauthenticated
  const [loadingGroups, setLoadingGroups] = React.useState(false);
  const [loadingMessages, setLoadingMessages] = React.useState(false);
  const [errorGroups, setErrorGroups] = React.useState(null);
  const [errorMessages, setErrorMessages] = React.useState(null);
  const [popped, setPopped] = React.useState([]);

  // Run auth once
  React.useEffect(() => {
    (async () => {
      try {
        await checkAuth(setUser); // existing function mutates user or sets null
      } catch (e) {
        console.warn('checkAuth threw unexpectedly', e);
        setUser(null);
      }
    })();
  }, []);

  // Fetch message groups after auth
  React.useEffect(() => {
    if (user === undefined) return; // still checking
    if (user === null) {
      navigate('/signin');
      return;
    }

    const controller = new AbortController();
    const loadGroups = async () => {
      setLoadingGroups(true);
      setErrorGroups(null);
      try {
        const backendUrl = `${process.env.REACT_APP_BACKEND_URL}/api/message_groups`;
        const data = await fetchWithAuth(backendUrl, controller.signal);
        setMessageGroups(data);
      } catch (err) {
        if (err.name !== 'AbortError') {
          setErrorGroups(err);
          console.error('Failed to load message groups:', err, err.payload);
        }
      } finally {
        setLoadingGroups(false);
      }
    };
    loadGroups();
    return () => controller.abort();
  }, [user, navigate]);

  // Fetch messages for the selected group after auth and when uuid changes
  React.useEffect(() => {
    if (user === undefined) return; // auth pending
    if (user === null) return; // already redirected above

    if (!message_group_uuid) return;

    const controller = new AbortController();
    const loadMessages = async () => {
      setLoadingMessages(true);
      setErrorMessages(null);
      try {
        const backendUrl = `${process.env.REACT_APP_BACKEND_URL}/api/messages/${message_group_uuid}`;
        const data = await fetchWithAuth(backendUrl, controller.signal);
        setMessages(data);
      } catch (err) {
        if (err.name !== 'AbortError') {
          setErrorMessages(err);
          console.error('Failed to load messages:', err, err.payload);
        }
      } finally {
        setLoadingMessages(false);
      }
    };
    loadMessages();
    return () => controller.abort();
  }, [user, message_group_uuid]);

  return (
    <article className="message-group-page">
      <DesktopNavigation user={user && user !== null ? user : null} active="home" setPopped={setPopped} />

      <section className="message_groups">
        {user === undefined && <div className="status">Checking authentication...</div>}
        {user === null && <div className="status error">Not authenticated. Redirecting...</div>}

        {user && (
          <>
            {loadingGroups && <div className="status">Loading message groups...</div>}
            {errorGroups && (
              <div className="status error">
                Error loading groups: {errorGroups.payload?.message || errorGroups.message}
                {errorGroups.payload && (
                  <pre style={{ fontSize: '0.7em', whiteSpace: 'pre-wrap' }}>
                    {JSON.stringify(errorGroups.payload, null, 2)}
                  </pre>
                )}
              </div>
            )}
            {!loadingGroups && !errorGroups && (
              <MessageGroupFeed message_groups={messageGroups} />
            )}
          </>
        )}
      </section>

      <div className="content messages">
        <div className="messages-sidebar">{/* optional sidebar */}</div>

        <div className="messages-main">
          {loadingMessages && <div className="status">Loading messages...</div>}
          {errorMessages && (
            <div className="status error">
              Error loading messages: {errorMessages.payload?.message || errorMessages.message}
              {errorMessages.payload && (
                <pre style={{ fontSize: '0.7em', whiteSpace: 'pre-wrap' }}>
                  {JSON.stringify(errorMessages.payload, null, 2)}
                </pre>
              )}
            </div>
          )}
          {!loadingMessages && !errorMessages && (
            <MessagesFeed messages={messages} />
          )}
          <MessagesForm setMessages={setMessages} currentGroupUUID={message_group_uuid} />
        </div>
      </div>
    </article>
  );
}
