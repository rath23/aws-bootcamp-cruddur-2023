import './SigninPage.css';
import React, { useEffect, useState } from "react";
import { ReactComponent as Logo } from '../components/svg/logo.svg';
import { Link, useNavigate } from "react-router-dom";
import { signIn, fetchAuthSession, getCurrentUser, signOut } from '@aws-amplify/auth';

export default function SigninPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState('');

  const navigate = useNavigate();


const onsubmit = async (event) => {
  event.preventDefault();
  setErrors('');

  try {
    // Optional: Sign out any previously signed-in user
    try {
      const existingUser = await getCurrentUser();
      if (existingUser) {
        await signOut();
      }
    } catch (e) {
      // No user signed in, ignore
    }

    const user = await signIn({ username: email, password });
    console.log("🧪 User returned from signIn:", user);

    if (user?.nextStep?.signInStep !== "DONE") {
      throw new Error(`Unexpected signIn step: ${user.nextStep.signInStep}`);
    }

    // ✅ Fetch session and get token
    const session = await fetchAuthSession();
    const token = session.tokens?.accessToken?.toString();

    if (!token) {
      throw new Error("Sign in failed: No token received from session.");
    }

    // Store token if needed
    localStorage.setItem("access_token", token);

    // Navigate to home
    navigate("/");
  } catch (error) {
    console.error("Sign in error:", error);

    if (error.name === 'UserNotConfirmedException') {
      navigate("/confirm");
    } else if (error.name === 'NotAuthorizedException') {
      setErrors("Incorrect email or password");
    } else {
      setErrors(error.message || "An unknown error occurred");
    }
  }
};


  const email_onchange = (event) => setEmail(event.target.value);
  const password_onchange = (event) => setPassword(event.target.value);

  return (
    <article className="signin-article">
      <div className='signin-info'>
        <Logo className='logo' />
      </div>
      <div className='signin-wrapper'>
        <form className='signin_form' onSubmit={onsubmit}>
          <h2>Sign into your Cruddur account</h2>

          <div className='fields'>
            <div className='field text_field username'>
              <label>Email</label>
              <input
                type="text"
                value={email}
                onChange={email_onchange}
              />
            </div>
            <div className='field text_field password'>
              <label>Password</label>
              <input
                type="password"
                value={password}
                onChange={password_onchange}
              />
            </div>
          </div>

          {errors && <div className='errors'>{errors}</div>}

          <div className='submit'>
            <Link to="/forgot" className="forgot-link">Forgot Password?</Link>
            <button type='submit' disabled={!email || !password}>Sign In</button>
          </div>
        </form>

        <div className="dont-have-an-account">
          <span>Don't have an account?</span>
          <Link to="/signup">Sign up!</Link>
        </div>
      </div>
    </article>
  );
}