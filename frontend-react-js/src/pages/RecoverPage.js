import './RecoverPage.css';
import React from "react";
import { ReactComponent as Logo } from '../components/svg/logo.svg';
import { Link } from "react-router-dom";
import { resetPassword, confirmResetPassword } from 'aws-amplify/auth';

export default function RecoverPage() {
  // Username is Email
  const [username, setUsername] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [passwordAgain, setPasswordAgain] = React.useState('');
  const [code, setCode] = React.useState('');
  const [errors, setErrors] = React.useState('');
  const [formState, setFormState] = React.useState('send_code');

  const onsubmit_send_code = async (event) => {
    event.preventDefault();
    setErrors('');
    try {
      const output = await resetPassword({ username });
      const { nextStep } = output;
      if (nextStep.resetPasswordStep === 'CONFIRM_RESET_PASSWORD_WITH_CODE') {
        setFormState('confirm_code');
      } else if (nextStep.resetPasswordStep === 'DONE') {
        setFormState('success');
      }
    } catch (err) {
      setErrors(err.message);
    }
    return false;
  };

  const onsubmit_confirm_code = async (event) => {
    event.preventDefault();
    setErrors('');
    if (password !== passwordAgain) {
      setErrors('Passwords do not match');
      return false;
    }

    try {
      await confirmResetPassword({
        username,
        confirmationCode: code,
        newPassword: password,
      });
      setFormState('success');
    } catch (err) {
      setErrors(err.message);
    }
    return false;
  };

  const username_onchange = (event) => setUsername(event.target.value);
  const password_onchange = (event) => setPassword(event.target.value);
  const password_again_onchange = (event) => setPasswordAgain(event.target.value);
  const code_onchange = (event) => setCode(event.target.value);

  const el_errors = errors ? <div className='errors'>{errors}</div> : null;

  const send_code = () => (
    <form className='recover_form' onSubmit={onsubmit_send_code}>
      <h2>Recover your Password</h2>
      <div className='fields'>
        <div className='field text_field username'>
          <label>Email</label>
          <input
            type="text"
            value={username}
            onChange={username_onchange}
            required
          />
        </div>
      </div>
      {el_errors}
      <div className='submit'>
        <button type='submit'>Send Recovery Code</button>
      </div>
    </form>
  );

  const confirm_code = () => (
    <form className='recover_form' onSubmit={onsubmit_confirm_code}>
      <h2>Recover your Password</h2>
      <div className='fields'>
        <div className='field text_field code'>
          <label>Reset Password Code</label>
          <input
            type="text"
            value={code}
            onChange={code_onchange}
            required
          />
        </div>
        <div className='field text_field password'>
          <label>New Password</label>
          <input
            type="password"
            value={password}
            onChange={password_onchange}
            required
          />
        </div>
        <div className='field text_field password_again'>
          <label>New Password Again</label>
          <input
            type="password"
            value={passwordAgain}
            onChange={password_again_onchange}
            required
          />
        </div>
      </div>
      {el_errors}
      <div className='submit'>
        <button type='submit'>Reset Password</button>
      </div>
    </form>
  );

  const success = () => (
    <form className='recover_form'>
      <p>Your password has been successfully reset!</p>
      <Link to="/signin" className="proceed">Proceed to Sign In</Link>
    </form>
  );

  let form;
  if (formState === 'send_code') {
    form = send_code();
  } else if (formState === 'confirm_code') {
    form = confirm_code();
  } else if (formState === 'success') {
    form = success();
  }

  return (
    <article className="recover-article">
      <div className='recover-info'>
        <Logo className='logo' />
      </div>
      <div className='recover-wrapper'>
        {form}
      </div>
    </article>
  );
}
