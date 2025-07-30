import './MessageGroupFeed.css';
import MessageGroupItem from './MessageGroupItem';
import { useState } from 'react';

export default function MessageGroupFeed(props) {
  const [showModal, setShowModal] = useState(false);
  const [groupName, setGroupName] = useState('');

  const handleCreateGroup = () => {
    // Here you would typically call an API to create the group
    console.log("Creating group:", groupName);
    // Add your logic to create the group
    // Then close the modal and reset the input
    setShowModal(false);
    setGroupName('');
  };

  return (
    <div className='message_group_feed'>
      <div className='message_group_feed_heading'>
        <div className='title'>Messages</div>
        <div className='heading_actions'>
          <button 
            className='create_group_button'
            onClick={() => setShowModal(true)}
          >
            + New Group
          </button>
        </div>
      </div>
      <div className='message_group_feed_collection'>
        {props.message_groups.map(message_group => {
          return <MessageGroupItem key={message_group.uuid} message_group={message_group} />
        })}
      </div>

      {/* Modal for creating new group */}
      {showModal && (
        <div className="modal_overlay">
          <div className="modal_content">
            <h3>Create New Group</h3>
            <input
              type="text"
              placeholder="Enter group name"
              value={groupName}
              onChange={(e) => setGroupName(e.target.value)}
              className="group_name_input"
            />
            <div className="modal_actions">
              <button 
                onClick={() => setShowModal(false)}
                className="cancel_button"
              >
                Cancel
              </button>
              <button 
                onClick={handleCreateGroup}
                className="create_button"
                disabled={!groupName.trim()}
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}