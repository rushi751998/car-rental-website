// Navigation User Display - Shows logged-in user's name in navigation bar
(function() {
  'use strict';
  
  // Check if user is logged in and update navigation
  function updateNavWithUser() {
    const userFullName = localStorage.getItem('user_full_name');
    const userToken = localStorage.getItem('user_token');
    const navLinks = document.getElementById('navLinks');
    
    if (!navLinks) return;
    
    // Check if user info exists in navigation already
    const existingUserInfo = document.getElementById('navUserInfo');
    if (existingUserInfo) {
      existingUserInfo.remove();
    }
    
    if (userFullName && userToken) {
      // User is logged in - show name and logout button
      const userLi = document.createElement('li');
      userLi.id = 'navUserInfo';
      userLi.style.cssText = 'display:flex;align-items:center;gap:1rem;';
      
      userLi.innerHTML = `
        <span style="color:#fff;font-weight:600;">👤 ${userFullName}</span>
        <a href="#" onclick="handleLogout(event)" style="color:#fff;text-decoration:none;background:rgba(255,255,255,0.2);padding:0.4rem 0.8rem;border-radius:4px;">Logout</a>
      `;
      
      navLinks.appendChild(userLi);
    } else {
      // User not logged in - show login button
      const loginLi = document.createElement('li');
      loginLi.id = 'navUserInfo';
      loginLi.innerHTML = `<a href="login.html" style="color:#fff;text-decoration:none;background:rgba(255,255,255,0.2);padding:0.4rem 0.8rem;border-radius:4px;">Login</a>`;
      navLinks.appendChild(loginLi);
    }
  }
  
  // Logout handler
  window.handleLogout = function(event) {
    event.preventDefault();
    
    // Clear all user data from localStorage
    localStorage.removeItem('user_token');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_password');
    localStorage.removeItem('user_full_name');
    
    // Redirect to home page
    window.location.href = 'index.html';
  };
  
  // Run on page load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', updateNavWithUser);
  } else {
    updateNavWithUser();
  }
})();
