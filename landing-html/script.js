// Pentest.red Landing Page - JavaScript

// Header scroll effect
window.addEventListener('scroll', function() {
  const header = document.getElementById('header');
  if (window.scrollY > 20) {
    header.classList.add('scrolled');
  } else {
    header.classList.remove('scrolled');
  }
});

// Mobile menu toggle
function toggleMobileMenu() {
  const menu = document.getElementById('mobile-menu');
  const menuIcon = document.getElementById('menu-icon');
  const closeIcon = document.getElementById('close-icon');
  
  menu.classList.toggle('open');
  menuIcon.classList.toggle('hidden');
  closeIcon.classList.toggle('hidden');
}

// Login Modal
function openLoginModal() {
  const modal = document.getElementById('login-modal');
  modal.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeLoginModal() {
  const modal = document.getElementById('login-modal');
  modal.classList.remove('open');
  document.body.style.overflow = '';
}

// Demo Modal
function openDemoModal() {
  const modal = document.getElementById('demo-modal');
  modal.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeDemoModal() {
  const modal = document.getElementById('demo-modal');
  modal.classList.remove('open');
  document.body.style.overflow = '';
  
  // Reset form
  const form = document.getElementById('demo-form');
  const success = document.getElementById('demo-success');
  form.reset();
  form.classList.remove('hidden');
  success.classList.add('hidden');
}

// Login form handler
document.getElementById('login-form').addEventListener('submit', async function(e) {
  e.preventDefault();
  
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const errorDiv = document.getElementById('login-error');
  const btnText = document.getElementById('login-btn-text');
  const form = this;
  
  errorDiv.classList.add('hidden');
  btnText.textContent = 'Logging in...';
  form.querySelector('button[type="submit"]').disabled = true;
  
  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });
    
    const data = await response.json();
    
    if (!response.ok || !data.success) {
      throw new Error(data.error || 'Login failed. Please check your credentials.');
    }
    
    // Save token
    localStorage.setItem('authToken', data.token);
    
    // Redirect to /app
    window.location.href = '/app';
  } catch (error) {
    errorDiv.textContent = error.message || 'Login failed. Please check your username and password.';
    errorDiv.classList.remove('hidden');
    btnText.textContent = 'Login';
    form.querySelector('button[type="submit"]').disabled = false;
  }
});

// Demo form handler
document.getElementById('demo-form').addEventListener('submit', async function(e) {
  e.preventDefault();
  
  const name = document.getElementById('name').value;
  const phone = document.getElementById('phone').value;
  const errorDiv = document.getElementById('demo-error');
  const successDiv = document.getElementById('demo-success');
  const btnText = document.getElementById('demo-btn-text');
  const form = this;
  
  errorDiv.classList.add('hidden');
  btnText.textContent = 'Submitting...';
  form.querySelector('button[type="submit"]').disabled = true;
  
  try {
    const response = await fetch('/api/demo-requests', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name, phone }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to submit request');
    }
    
    // Show success
    form.classList.add('hidden');
    successDiv.classList.remove('hidden');
    
    // Close modal after 2 seconds
    setTimeout(() => {
      closeDemoModal();
    }, 2000);
  } catch (error) {
    errorDiv.textContent = 'An error occurred. Please try again.';
    errorDiv.classList.remove('hidden');
    btnText.textContent = 'Submit';
    form.querySelector('button[type="submit"]').disabled = false;
  }
});

// Sticky CTA
let stickyCTAVisible = false;
let stickyCTADismissed = false;

window.addEventListener('scroll', function() {
  if (stickyCTADismissed) return;
  
  const shouldShow = window.scrollY > 600;
  const stickyCTA = document.getElementById('sticky-cta');
  
  if (shouldShow && !stickyCTAVisible) {
    stickyCTA.classList.remove('hidden');
    stickyCTAVisible = true;
  } else if (!shouldShow && stickyCTAVisible) {
    stickyCTA.classList.add('hidden');
    stickyCTAVisible = false;
  }
});

function dismissStickyCTA() {
  const stickyCTA = document.getElementById('sticky-cta');
  stickyCTA.classList.add('hidden');
  stickyCTADismissed = true;
}

// Close modals on backdrop click
document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
  backdrop.addEventListener('click', function(e) {
    if (e.target === this) {
      const modal = this.closest('.modal');
      if (modal.id === 'login-modal') {
        closeLoginModal();
      } else if (modal.id === 'demo-modal') {
        closeDemoModal();
      }
    }
  });
});

// Close modals on Escape key
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    closeLoginModal();
    closeDemoModal();
  }
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    const href = this.getAttribute('href');
    if (href === '#') return;
    
    e.preventDefault();
    const target = document.querySelector(href);
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  });
});
