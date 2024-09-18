import React, { useState, useEffect } from 'react';
import { useGoogleLogin } from '@react-oauth/google';
import axios from 'axios';
import './App.css';
import companyLogo from './assets/companylogo.png'; // Ensure this path is correct

function Login({ onLoginSuccess }) {
  const [user, setUser] = useState(null);

  const login = useGoogleLogin({
    onSuccess: (codeResponse) => setUser(codeResponse),
    onError: (error) => console.log('Login Failed:', error)
  });

  useEffect(() => {
    if (user) {
      axios
        .get(`https://www.googleapis.com/oauth2/v1/userinfo?access_token=${user.access_token}`, {
          headers: {
            Authorization: `Bearer ${user.access_token}`,
            Accept: 'application/json'
          }
        })
        .then((res) => {
          onLoginSuccess(res.data);
        })
        .catch((err) => console.log(err));
    }
  }, [user, onLoginSuccess]);

  return (
    <div className="login-container">
      <div className="login-box">
        <img src={companyLogo} alt="Company Logo" className="company-logo" />
        <h2>Login with Google</h2>
        <button onClick={() => login()} className="login-button">
          <img src="https://developers.google.com/identity/images/g-logo.png" alt="Google logo" className="google-logo" />
          Sign in with Google
        </button>
      </div>
    </div>
  );
}

export default Login;

