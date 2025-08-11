import './HomeFeedPage.css';
import React from "react";

import { checkAuth } from '../lib/CheckAuth';
import DesktopNavigation from '../components/DesktopNavigation';
import DesktopSidebar from '../components/DesktopSidebar';
import ActivityFeed from '../components/ActivityFeed';
import ActivityForm from '../components/ActivityForm';
import ReplyForm from '../components/ReplyForm';
import { getAuthToken } from '../lib/GetAuthToken';

export default function HomeFeedPage() {
  const [activities, setActivities] = React.useState([]);
  const [popped, setPopped] = React.useState(false);
  const [poppedReply, setPoppedReply] = React.useState(false);
  const [replyActivity, setReplyActivity] = React.useState({});
  const [user, setUser] = React.useState(null);
  const dataFetchedRef = React.useRef(false);

  const loadData = async () => {
    // const token = localStorage.getItem("access_token");
    const token = await getAuthToken();
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




  React.useEffect(() => {
    if (dataFetchedRef.current) return;
    dataFetchedRef.current = true;

    loadData();
    async function init() {
      await checkAuth(setUser);
      console.log("User state set in HomeFeedPage:", user);
    }
    init();

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
        <div className='activity_feed'>
          <div className='activity_feed_heading'>
            <div className='title'>Home</div>
          </div>
          <ActivityFeed 
            setReplyActivity={setReplyActivity} 
            setPopped={setPoppedReply} 
            activities={activities} 
          />
        </div>
      </div>
      <DesktopSidebar user={user} />
    </article>
  );
}