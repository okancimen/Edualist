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
  const langBtns = langSwitcher.querySelectorAll('.lang-btn');
  const htmlRoot = document.documentElement;

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
    
    // 2. Persist in storage
    localStorage.setItem('edualist_lang', lang);
    
    // 3. Update switcher buttons
    langBtns.forEach(btn => {
      if (btn.getAttribute('data-lang') === lang) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    // 4. Update Form Placeholders dynamically
    const nameInput = document.getElementById('form-name');
    const phoneInput = document.getElementById('form-phone');
    const detailsInput = document.getElementById('form-details');
    const webNameInput = document.getElementById('webinar-name');
    const webPhoneInput = document.getElementById('webinar-phone');

    if (nameInput) nameInput.placeholder = placeholders[lang].name;
    if (phoneInput) phoneInput.placeholder = placeholders[lang].phone;
    if (detailsInput) detailsInput.placeholder = placeholders[lang].details;
    if (webNameInput) webNameInput.placeholder = placeholders[lang].name;
    if (webPhoneInput) webPhoneInput.placeholder = placeholders[lang].phone;
  }

  // Event listener for lang switcher buttons
  langBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const selectedLang = btn.getAttribute('data-lang');
      setLanguage(selectedLang);
    });
  });

  // Init language from storage or default to Turkish
  const savedLang = localStorage.getItem('edualist_lang') || 'tr';
  setLanguage(savedLang);

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
    // Add initialization class to all reveal candidates
    revealElements.forEach(el => el.classList.add('reveal-init'));

    const revealObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('reveal-active');
          // Once animated, no need to track again
          revealObserver.unobserve(entry.target);
        }
      });
    }, {
      root: null,
      threshold: 0.15,
      rootMargin: '0px 0px -50px 0px' // Trigger slightly before element fits in viewport
    });

    revealElements.forEach(el => revealObserver.observe(el));
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

      // Basic HTML5 validation trigger
      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }

      // Collect data (for presentation or simulation)
      const data = {
        name: document.getElementById('form-name').value,
        email: document.getElementById('form-email').value,
        phone: document.getElementById('form-phone').value,
        relocation: document.getElementById('form-relocation').value,
        details: document.getElementById('form-details').value
      };

      console.log('Form submission received:', data);

      // Show beautiful feedback box
      if (alertBox) {
        alertBox.style.display = 'flex';
        
        // Clear all inputs
        form.reset();
        
        // Scroll smoothly to alert box
        alertBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        // Remove validation classes if any
        form.classList.remove('was-validated');

        // Hide success message after 5 seconds
        setTimeout(() => {
          alertBox.style.display = 'none';
        }, 5000);
      }
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

      const data = {
        name: document.getElementById('webinar-name').value,
        email: document.getElementById('webinar-email').value,
        phone: document.getElementById('webinar-phone').value
      };

      console.log('Webinar registration received:', data);

      if (webinarAlert) {
        webinarAlert.style.display = 'flex';
        webinarForm.reset();
        webinarAlert.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        setTimeout(() => {
          webinarAlert.style.display = 'none';
        }, 5000);
      }
    });
  }

});
