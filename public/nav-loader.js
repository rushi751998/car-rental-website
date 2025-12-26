// Navigation Loader - Loads shared navigation bar on all pages
(function() {
  'use strict';
  
  // Load navigation HTML
  async function loadNavigation() {
    try {
      const response = await fetch('/public/nav.html');
      const navHTML = await response.text();
      
      // Find the nav-placeholder and insert navigation
      const placeholder = document.getElementById('nav-placeholder');
      if (placeholder) {
        placeholder.innerHTML = navHTML;
        
        // Initialize menu toggle after navigation is loaded
        initializeMenuToggle();
      }
    } catch (error) {
      console.error('Failed to load navigation:', error);
    }
  }
  
  // Initialize mobile menu toggle
  function initializeMenuToggle() {
    const menuToggle = document.getElementById('menuToggle');
    const navLinks = document.getElementById('navLinks');
    
    if (menuToggle && navLinks) {
      menuToggle.addEventListener('click', () => {
        navLinks.classList.toggle('active');
      });
    }
  }
  
  // Load navigation when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadNavigation);
  } else {
    loadNavigation();
  }
})();
