import './ConfirmationPage.css';
import React, { useEffect, useState } from "react";
import { useLocation } from 'react-router-dom';
import { confirmSignUp, resendSignUpCode } from 'aws-amplify/auth';
import { ReactComponent as Logo } from '../components/svg/logo.svg';

export default function ConfirmationPage() {
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [errors, setErrors] = useState('');
  const [codeSent, setCodeSent] = useState(false);

  const location = useLocation();

  useEffect(() => {
    if (location.state?.email) {
      setEmail(location.state.email);
    }
  }, [location.state]);

  const onsubmit = async (event) => {
    event.preventDefault();
    setErrors('');
    try {
      await confirmSignUp({ username: email, confirmationCode: code });
      window.location.href = '/';
    } catch (err) {
      setErrors(err.message);
    }
  };

  const resend_code = async () => {
    setErrors('');
    try {
      await resendSignUpCode({ username: email });
      setCodeSent(true);
    } catch (err) {
      setErrors(err.message);
    }
  };

  return (
    <article className="confirm-article">
      <div className='recover-info'>
        <Logo className='logo' />
      </div>
      <div className='recover-wrapper'>
        <form className='confirm_form' onSubmit={onsubmit}>
          <h2>Confirm your Email</h2>
          <div className='fields'>
            <div className='field text_field email'>
              <label>Email</label>
              <input type="text" value={email} onChange={e => setEmail(e.target.value)} />
            </div>
            <div className='field text_field code'>
              <label>Confirmation Code</label>
              <input type="text" value={code} onChange={e => setCode(e.target.value)} />
            </div>
          </div>
          {errors && <div className='errors'>{errors}</div>}
          <div className='submit'>
            <button type='submit'>Confirm Email</button>
          </div>
        </form>
        {codeSent
          ? <div className="sent-message">A new activation code has been sent to your email</div>
          : <button className="resend" onClick={resend_code}>Resend Activation Code</button>
        }
      </div>
    </article>
  );
}
