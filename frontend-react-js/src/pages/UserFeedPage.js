import './UserFeedPage.css';
import React, { useEffect, useRef, useState, useCallback, useMemo } from "react";
import { useParams } from 'react-router-dom';
import Cookies from 'js-cookie';

import DesktopNavigation from '../components/DesktopNavigation';
import DesktopSidebar from '../components/DesktopSidebar';
import ActivityFeed from '../components/ActivityFeed';
import ActivityForm from '../components/ActivityForm';

export default function UserFeedPage() {
  const [activities, setActivities] = useState([]);
  const [popped, setPopped] = useState([]); // Kept in case ActivityForm uses it
  const [user, setUser] = useState(null);
  const dataFetchedRef = useRef(false);

  const params = useParams();

  const title = useMemo(() => `@${params.handle}`, [params.handle]);

  const loadData = useCallback(async () => {
    try {
      const backend_url = `${process.env.REACT_APP_BACKEND_URL}/api/activities/${title}`;
      const res = await fetch(backend_url, {
        method: "GET"
      });
      const resJson = await res.json();
      if (res.status === 200) {
        setActivities(resJson);
      } else {
        console.warn('Failed to load activities:', res);
      }
    } catch (err) {
      console.error('Fetch error:', err);
    }
  }, [title]);

  const checkAuth = useCallback(() => {
    if (Cookies.get('user.logged_in')) {
      setUser({
        display_name: Cookies.get('user.name'),
        handle: Cookies.get('user.username')
      });
    }
  }, []);

  useEffect(() => {
    if (dataFetchedRef.current) return;
    dataFetchedRef.current = true;

    loadData();
    checkAuth();
  }, [loadData, checkAuth]);

  return (
    <article>
      <DesktopNavigation user={user} active={'profile'} setPopped={setPopped} />
      <div className='content'>
        <ActivityForm popped={popped} setActivities={setActivities} />
        <ActivityFeed title={title} activities={activities} />
      </div>
      <DesktopSidebar user={user} />
    </article>
  );
}
