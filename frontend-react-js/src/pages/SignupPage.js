import './SignupPage.css';
import React from "react";
import {ReactComponent as Logo} from '../components/svg/logo.svg';
import { Link , useNavigate} from "react-router-dom";



// [TODO] Authenication
import { signUp } from '@aws-amplify/auth';

export default function SignupPage() {

  const navigate = useNavigate();

  // Username is Eamil
  const [name, setName] = React.useState('');
  const [email, setEmail] = React.useState('');
  const [username, setUsername] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [errors, setErrors] = React.useState('');

  // const onsubmit = async (event) => {
  //   event.preventDefault();
  //   console.log('SignupPage.onsubmit')
  //   // [TODO] Authenication
  //   Cookies.set('user.name', name)
  //   Cookies.set('user.username', username)
  //   Cookies.set('user.email', email)
  //   Cookies.set('user.password', password)
  //   Cookies.set('user.confirmation_code',1234)
  //   window.location.href = `/confirm?email=${email}`
  //   return false
  // }

const onsubmit = async (event) => {
  event.preventDefault();
  setErrors('');
  try {
    const response = await signUp({
      username: email,
      password: password,
      options: {
        userAttributes: {
          name: name,
          email: email,
          preferred_username: username
        }
      }
    });

    console.log('Signup success', response);
    // Redirect to confirm page with email
    navigate('/confirm', { state: { email } }); 
  } catch (error) {
    console.log('Signup error', error);
    if (error.code === 'UsernameExistsException') {
      setErrors('This username or email is already registered.');
    } else {
      setErrors(error.message || 'Signup failed');
    }
  }
  return false;
};


  

  const name_onchange = (event) => {
    setName(event.target.value);
  }
  const email_onchange = (event) => {
    setEmail(event.target.value);
  }
  const username_onchange = (event) => {
    setUsername(event.target.value);
  }
  const password_onchange = (event) => {
    setPassword(event.target.value);
  }

  let el_errors;
  if (errors){
    el_errors = <div className='errors'>{errors}</div>;
  }

  return (
    <article className='signup-article'>
      <div className='signup-info'>
        <Logo className='logo' />
      </div>
      <div className='signup-wrapper'>
        <form 
          className='signup_form'
          onSubmit={onsubmit}
        >
          <h2>Sign up to create a Cruddur account</h2>
          <div className='fields'>
            <div className='field text_field name'>
              <label>Name</label>
              <input
                type="text"
                value={name}
                onChange={name_onchange} 
              />
            </div>

            <div className='field text_field email'>
              <label>Email</label>
              <input
                type="text"
                value={email}
                onChange={email_onchange} 
              />
            </div>

            <div className='field text_field username'>
              <label>Username</label>
              <input
                type="text"
                value={username}
                onChange={username_onchange} 
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
          {el_errors}
          <div className='submit'>
            <button type='submit'>Sign Up</button>
          </div>
        </form>
        <div className="already-have-an-account">
          <span>
            Already have an account?
          </span>
          <Link to="/signin">Sign in!</Link>
        </div>
      </div>
    </article>
  );
}