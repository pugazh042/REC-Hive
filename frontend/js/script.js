(function () {
  const form      = document.getElementById('loginForm');
  const emailInp  = document.getElementById('email');
  const passInp   = document.getElementById('password');
  const emailGrp  = document.getElementById('emailGroup');
  const passGrp   = document.getElementById('passwordGroup');
  const emailErr  = document.getElementById('emailError');
  const passErr   = document.getElementById('passwordError');
  const submitBtn = document.getElementById('submitBtn');
  const togglePwd = document.getElementById('togglePwd');
  const eyeIcon   = document.getElementById('eyeIcon');
  const success   = document.getElementById('successOverlay');

  const EYE_OPEN = `<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>`;
  const EYE_SHUT = `<path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/>`;

  function isValidEmail(v) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim());
  }

  function clearError(group, errEl) {
    group.classList.remove('has-error');
    errEl.classList.remove('show');
  }

  function showError(group, errEl, msg) {
    group.classList.add('has-error');
    errEl.textContent = msg;
    errEl.classList.add('show');
  }

  function validateEmail() {
    const val = emailInp.value;
    if (!val) {
      showError(emailGrp, emailErr, 'Email is required.');
      return false;
    }
    if (!isValidEmail(val)) {
      showError(emailGrp, emailErr, 'Please enter a valid email address.');
      return false;
    }
    clearError(emailGrp, emailErr);
    return true;
  }

  function validatePassword() {
    const val = passInp.value;
    if (!val) {
      showError(passGrp, passErr, 'Password is required.');
      return false;
    }
    if (val.length < 6) {
      showError(passGrp, passErr, 'Password must be at least 6 characters.');
      return false;
    }
    clearError(passGrp, passErr);
    return true;
  }

  emailInp.addEventListener('blur', validateEmail);
  passInp.addEventListener('blur', validatePassword);
  emailInp.addEventListener('input', function () { if (emailGrp.classList.contains('has-error')) validateEmail(); });
  passInp.addEventListener('input',  function () { if (passGrp.classList.contains('has-error'))  validatePassword(); });

  togglePwd.addEventListener('click', function () {
    const isPassword = passInp.type === 'password';
    passInp.type = isPassword ? 'text' : 'password';
    eyeIcon.innerHTML = isPassword ? EYE_SHUT : EYE_OPEN;
    togglePwd.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password');
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    const emailOk = validateEmail();
    const passOk  = validatePassword();
    if (!emailOk || !passOk) return;

    submitBtn.classList.add('loading');

    setTimeout(function () {
      submitBtn.classList.remove('loading');
      success.classList.add('show');
    }, 1600);
  });

  document.querySelectorAll('.btn-social').forEach(function (btn) {
    btn.addEventListener('click', function () {
      btn.style.opacity = '0.6';
      btn.style.pointerEvents = 'none';
      setTimeout(function () {
        btn.style.opacity = '';
        btn.style.pointerEvents = '';
      }, 1200);
    });
  });
})();
