import './HomeFeedPage.css';
import React from "react";

// ✅ Modular v6 imports
import { getCurrentUser, fetchUserAttributes } from '@aws-amplify/auth';

import DesktopNavigation from '../components/DesktopNavigation';
import DesktopSidebar from '../components/DesktopSidebar';
import ActivityFeed from '../components/ActivityFeed';
import ActivityForm from '../components/ActivityForm';
import ReplyForm from '../components/ReplyForm';

export default function HomeFeedPage() {
  const [activities, setActivities] = React.useState([]);
  const [popped, setPopped] = React.useState(false);
  const [poppedReply, setPoppedReply] = React.useState(false);
  const [replyActivity, setReplyActivity] = React.useState({});
  const [user, setUser] = React.useState(null);
  const dataFetchedRef = React.useRef(false);

 const loadData = async () => {
  const token = localStorage.getItem("access_token");
  try {
    const backend_url = `${process.env.REACT_APP_BACKEND_URL}/api/activities/home`;

    const res = await fetch(backend_url, {
      method: "GET",
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      }
    });

    const resJson = await res.json();

    if (res.status === 200) {
      setActivities(resJson);
    } else {
      console.log('Error response:', res);
      console.log('Error body:', resJson); // Add this for debugging
    }
  } catch (err) {
    console.error('Fetch error:', err);
  }
};


  const checkAuth = async () => {
    try {
      const cognitoUser = await getCurrentUser();
      const attributes = await fetchUserAttributes();

      setUser({
        display_name: attributes.name,
        handle: attributes.preferred_username,
      });
    } catch (error) {
      console.log("Not signed in", error);
    }
  };

  React.useEffect(() => {
    if (dataFetchedRef.current) return;
    dataFetchedRef.current = true;

    loadData();
    checkAuth();
  }, []);

  return (
    <article>
      <DesktopNavigation user={user} active={'home'} setPopped={setPopped} />
      <div className='content'>
        <ActivityForm
          popped={popped}
          setPopped={setPopped}
          setActivities={setActivities}
        />
        <ReplyForm
          activity={replyActivity}
          popped={poppedReply}
          setPopped={setPoppedReply}
          setActivities={setActivities}
          activities={activities}
        />
        <ActivityFeed
          title="Home"
          setReplyActivity={setReplyActivity}
          setPopped={setPoppedReply}
          activities={activities}
        />
      </div>
      <DesktopSidebar user={user} />
    </article>
  );
}
