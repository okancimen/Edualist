/**
 * Edualist App Script
 * Controls interactive features: Multilingual translation engine, mobile menu,
 * dynamic scroll animations, form validations, and tab highlights.
 */

document.addEventListener('DOMContentLoaded', () => {
  
  // ==========================================
  // MULTILINGUAL TRANSLATION ENGINE
  // ==========================================
  const langSwitcher = document.getElementById('lang-switcher');
  const langBtns = langSwitcher ? langSwitcher.querySelectorAll('.lang-btn') : [];
  const htmlRoot = document.documentElement;

  // Detect current language from the URL path
  const currentPath = window.location.pathname;
  let pageLang = 'tr';
  if (currentPath.includes('/en/') || currentPath.endsWith('/en')) {
    pageLang = 'en';
  } else if (currentPath.includes('/tr/') || currentPath.endsWith('/tr')) {
    pageLang = 'tr';
  } else {
    pageLang = htmlRoot.getAttribute('lang') || localStorage.getItem('edualist_lang') || 'tr';
  }

  // Placeholder translation mapping
  const placeholders = {
    tr: {
      name: "Örn: Ahmet Yılmaz",
      phone: "+90 555 123 4567",
      details: "Çocuğunuzun yaşını, sınıfını ve eğitim geçmişini belirtiniz..."
    },
    en: {
      name: "e.g. John Doe",
      phone: "e.g. +971 50 123 4567",
      details: "Please share child’s age, grade, language background, etc..."
    }
  };

  function setLanguage(lang) {
    // 1. Set HTML attribute
    htmlRoot.setAttribute('lang', lang);
    
    // 2. Update switcher buttons
    langBtns.forEach(btn => {
      if (btn.getAttribute('data-lang') === lang) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    // 3. Update Form Placeholders dynamically
    const nameInput = document.getElementById('form-name');
    const phoneInput = document.getElementById('form-phone');
    const detailsInput = document.getElementById('form-details');
    const webNameInput = document.getElementById('webinar-name');
    const webPhoneInput = document.getElementById('webinar-phone');

    if (placeholders[lang]) {
      if (nameInput) nameInput.placeholder = placeholders[lang].name;
      if (phoneInput) phoneInput.placeholder = placeholders[lang].phone;
      if (detailsInput) detailsInput.placeholder = placeholders[lang].details;
      if (webNameInput) webNameInput.placeholder = placeholders[lang].name;
      if (webPhoneInput) webPhoneInput.placeholder = placeholders[lang].phone;
    }
  }

  // Event listener for lang switcher buttons
  langBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const selectedLang = btn.getAttribute('data-lang');
      localStorage.setItem('edualist_lang', selectedLang);
      
      // Navigate to the correct subfolder if it is different from the current page language
      if (selectedLang !== pageLang) {
        const hash = window.location.hash || '';
        if (selectedLang === 'en') {
          window.location.href = '../en/' + hash;
        } else {
          window.location.href = '../tr/' + hash;
        }
      } else {
        setLanguage(selectedLang);
      }
    });
  });

  // Initialize page language based on subdirectory context
  setLanguage(pageLang);

  // ==========================================
  // MOBILE MENU TOGGLE
  // ==========================================
  const menuToggle = document.getElementById('menu-toggle');
  const navMenu = document.getElementById('nav-menu');
  const navLinks = navMenu.querySelectorAll('a');

  if (menuToggle && navMenu) {
    menuToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      navMenu.classList.toggle('open');
      menuToggle.classList.toggle('active');
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!navMenu.contains(e.target) && !menuToggle.contains(e.target)) {
        navMenu.classList.remove('open');
        menuToggle.classList.remove('active');
      }
    });

    // Close menu when clicking links
    navLinks.forEach(link => {
      link.addEventListener('click', () => {
        navMenu.classList.remove('open');
        menuToggle.classList.remove('active');
      });
    });
  }

  // ==========================================
  // SHRINKING HEADER SCROLL FALLBACK
  // ==========================================
  const navbar = document.getElementById('navbar');
  const scrollThreshold = 50;

  // Only run JS scroll listener if native CSS scroll-driven animations are unsupported
  if (!CSS.supports('(animation-timeline: scroll()) and (animation-range: 0% 100%)')) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > scrollThreshold) {
        navbar.classList.add('header-scrolled');
      } else {
        navbar.classList.remove('header-scrolled');
      }
    }, { passive: true });
  }

  // ==========================================
  // SCROLL-REVEAL OBSERVER (FALLBACK)
  // ==========================================
  const revealElements = document.querySelectorAll('.scroll-reveal');

  if (!CSS.supports('(animation-timeline: view()) and (animation-range: entry)')) {
    const revealObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('reveal-active');
          revealObserver.unobserve(entry.target);
        }
      });
    }, {
      root: null,
      threshold: 0.15,
      rootMargin: '0px 0px -50px 0px'
    });

    // Defer to next frame — avoids forced reflow during language init on the same frame
    requestAnimationFrame(() => {
      revealElements.forEach(el => {
        el.classList.add('reveal-init');
        revealObserver.observe(el);
      });
    });
  }

  // ==========================================
  // DYNAMIC NAV LINK HIGHLIGHT OBSERVER
  // ==========================================
  const sections = document.querySelectorAll('section[id]');
  const navObserverOptions = {
    root: null,
    rootMargin: '-30% 0px -60% 0px', // Trigger when section occupies the sweet middle spot
    threshold: 0
  };

  const navObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.getAttribute('id');
        navLinks.forEach(link => {
          if (link.getAttribute('href') === `#${id}`) {
            link.classList.add('active');
          } else {
            link.classList.remove('active');
          }
        });
      }
    });
  }, navObserverOptions);

  sections.forEach(section => navObserver.observe(section));

  // ==========================================
  // CONSULTATION FORM HANDLER
  // ==========================================
  const form = document.getElementById('consultation-form');
  const alertBox = document.getElementById('form-alert');

  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();

      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }

      const submitBtn = form.querySelector('[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;

      const data = {
        type: 'consultation',
        name: document.getElementById('form-name').value,
        email: document.getElementById('form-email').value,
        phone: document.getElementById('form-phone').value,
        relocation: document.getElementById('form-relocation').value,
        details: document.getElementById('form-details').value
      };

      fetch('../mail.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
        .then(r => r.json())
        .then(res => {
          if (res.ok && alertBox) {
            alertBox.style.display = 'flex';
            form.reset();
            form.classList.remove('was-validated');
            alertBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            setTimeout(() => { alertBox.style.display = 'none'; }, 5000);
          } else {
            if (submitBtn) submitBtn.disabled = false;
          }
        })
        .catch(() => { if (submitBtn) submitBtn.disabled = false; });
    });
  }

  // ==========================================
  // WEBINAR REGISTRATION FORM HANDLER
  // ==========================================
  const webinarForm = document.getElementById('webinar-form');
  const webinarAlert = document.getElementById('webinar-alert');

  if (webinarForm) {
    webinarForm.addEventListener('submit', (e) => {
      e.preventDefault();

      if (!webinarForm.checkValidity()) {
        webinarForm.reportValidity();
        return;
      }

      const submitBtn = webinarForm.querySelector('[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;

      const data = {
        type: 'webinar',
        name: document.getElementById('webinar-name').value,
        email: document.getElementById('webinar-email').value,
        phone: document.getElementById('webinar-phone').value
      };

      fetch('../mail.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
        .then(r => r.json())
        .then(res => {
          if (res.ok && webinarAlert) {
            webinarAlert.style.display = 'flex';
            webinarForm.reset();
            webinarAlert.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            setTimeout(() => { webinarAlert.style.display = 'none'; }, 5000);
          } else {
            if (submitBtn) submitBtn.disabled = false;
          }
        })
        .catch(() => { if (submitBtn) submitBtn.disabled = false; });
    });
  }
  // ==========================================
  // OPPORTUNITY POPUP LOGIC
  // ==========================================
  const oppDialog = document.getElementById('opp-dialog');
  const dialogClose = document.getElementById('dialog-close');
  const dialogCTA = document.getElementById('dialog-cta');
  if (oppDialog) {
    // Auto-show the opportunity dialog after 5 seconds
    // DISABLED — uncomment to re-enable the popup
    // setTimeout(() => oppDialog.showModal(), 5000);
    // Close button handler
    if (dialogClose) { dialogClose.addEventListener('click', () => oppDialog.close()); }
    // CTA button: scroll to webinar registration section
    if (dialogCTA) {
      dialogCTA.addEventListener('click', () => {
        const webinarSection = document.getElementById('webinar');
        if (webinarSection) {
          webinarSection.scrollIntoView({ behavior: 'smooth' });
        }
        oppDialog.close();
      });
    }
    // Countdown calculation
    function getLastWednesday(year, month) {
      const lastDay = new Date(year, month + 1, 0);
      const day = lastDay.getDay();
      const offset = (day >= 3) ? day - 3 : 7 - (3 - day);
      return new Date(year, month, lastDay.getDate() - offset);
    }
    function getNextWebinarDate(now) {
      const curYear = now.getFullYear();
      const curMonth = now.getMonth();
      let target = getLastWednesday(curYear, curMonth);
      if (now > target) {
        const nextMonth = new Date(curYear, curMonth + 1, 1);
        target = getLastWednesday(nextMonth.getFullYear(), nextMonth.getMonth());
      }
      target.setHours(20, 0, 0, 0);
      return target;
    }
    const elDays    = document.getElementById('countdown-days');
    const elHours   = document.getElementById('countdown-hours');
    const elMinutes = document.getElementById('countdown-minutes');
    const elSeconds = document.getElementById('countdown-seconds');
    function updateCountdown() {
      const now = new Date();
      const target = getNextWebinarDate(now);
      const diffMs = Math.max(0, target - now);
      const totalSeconds = Math.floor(diffMs / 1000);
      const days = Math.floor(totalSeconds / (60 * 60 * 24));
      const hours = Math.floor((totalSeconds % (60 * 60 * 24)) / (60 * 60));
      const minutes = Math.floor((totalSeconds % (60 * 60)) / 60);
      const seconds = totalSeconds % 60;
      if (elDays)    elDays.textContent    = days;
      if (elHours)   elHours.textContent   = String(hours).padStart(2, '0');
      if (elMinutes) elMinutes.textContent = String(minutes).padStart(2, '0');
      if (elSeconds) elSeconds.textContent = String(seconds).padStart(2, '0');
    }
    updateCountdown();
    setInterval(updateCountdown, 1000);
  }

  // ==========================================
  // AI CHATBOT POPUP
  // ==========================================
  const chatbotBtn   = document.getElementById('chatbot-btn');
  const chatbotPopup = document.getElementById('chatbot-popup');
  const chatbotClose = document.getElementById('chatbot-close');

  if (chatbotBtn && chatbotPopup) {
    chatbotBtn.addEventListener('click', () => {
      const opening = chatbotPopup.hidden;
      chatbotPopup.hidden = !opening;
      if (opening) {
        const iframe = chatbotPopup.querySelector('iframe[data-src]');
        if (iframe) { iframe.src = iframe.dataset.src; iframe.removeAttribute('data-src'); }
      }
    });
    if (chatbotClose) {
      chatbotClose.addEventListener('click', () => { chatbotPopup.hidden = true; });
    }
  }
});
