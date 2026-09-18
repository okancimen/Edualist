document.addEventListener("DOMContentLoaded", () => {

  // ── CRITICAL (runs immediately): lang init + mobile menu ────────────

  const langSwitcher = document.getElementById("lang-switcher");
  const langBtns = langSwitcher ? langSwitcher.querySelectorAll(".lang-btn") : [];
  const html = document.documentElement;
  const path = window.location.pathname;
  let currentLang = "tr";
  currentLang = path.includes("/en/") || path.endsWith("/en") ? "en"
    : path.includes("/tr/") || path.endsWith("/tr") ? "tr"
    : localStorage.getItem("edualist_lang") || html.getAttribute("lang") || "tr";

  const placeholders = {
    tr: { name: "Örn: Ahmet Yılmaz", phone: "+90 555 123 4567", details: "Çocuğunuzun yaşını, sınıfını ve eğitim geçmişini belirtiniz..." },
    en: { name: "e.g. John Doe", phone: "e.g. +971 50 123 4567", details: "Please share child's age, grade, language background, etc..." }
  };

  function setLang(lang) {
    if (html.getAttribute("lang") !== lang) html.setAttribute("lang", lang);
    langBtns.forEach(btn => btn.getAttribute("data-lang") === lang
      ? btn.classList.add("active") : btn.classList.remove("active"));
    const p = placeholders[lang];
    if (!p) return;
    const fields = ["form-name","form-phone","form-details","webinar-name","webinar-phone"];
    const vals   = [p.name,    p.phone,    p.details,    p.name,        p.phone       ];
    fields.forEach((id, i) => { const el = document.getElementById(id); if (el) el.placeholder = vals[i]; });
  }

  langBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const lang = btn.getAttribute("data-lang");
      localStorage.setItem("edualist_lang", lang);
      if ((/^\/(tr|en)(\/|$)/.test(path) || path === "/") && lang !== currentLang) {
        const hash = window.location.hash || "";
        window.location.href = lang === "en" ? "../en/" + hash : "../tr/" + hash;
      } else {
        setLang(lang);
      }
    });
  });
  setLang(currentLang);

  const menuToggle = document.getElementById("menu-toggle");
  const navMenu = document.getElementById("nav-menu");
  const navLinks = navMenu ? navMenu.querySelectorAll("a") : [];
  if (menuToggle && navMenu) {
    menuToggle.addEventListener("click", e => {
      e.stopPropagation();
      navMenu.classList.toggle("open");
      menuToggle.classList.toggle("active");
    });
    document.addEventListener("click", e => {
      if (!navMenu.contains(e.target) && !menuToggle.contains(e.target)) {
        navMenu.classList.remove("open");
        menuToggle.classList.remove("active");
      }
    });
    navLinks.forEach(link => {
      link.addEventListener("click", () => {
        navMenu.classList.remove("open");
        menuToggle.classList.remove("active");
      });
    });
  }

  // ── DEFERRED: split into multiple small tasks so no single task blocks INP ──

  // Task A: visual UI (navbar scroll + scroll-reveal) — first deferred task
  setTimeout(() => {

    // Navbar scroll effect
    const navbar = document.getElementById("navbar");
    if (navbar && !CSS.supports("(animation-timeline: scroll()) and (animation-range: 0% 100%)")) {
      let ticking = false;
      window.addEventListener("scroll", () => {
        if (!ticking) {
          requestAnimationFrame(() => {
            navbar.classList.toggle("header-scrolled", window.scrollY > 50);
            ticking = false;
          });
          ticking = true;
        }
      }, { passive: true });
    }

    // Scroll-reveal
    const revealEls = document.querySelectorAll(".scroll-reveal");
    if (revealEls.length && !CSS.supports("(animation-timeline: view()) and (animation-range: entry)")) {
      const revealObs = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add("reveal-active");
            revealObs.unobserve(entry.target);
          }
        });
      }, { root: null, threshold: 0.15, rootMargin: "0px 0px -50px 0px" });
      requestAnimationFrame(() => {
        revealEls.forEach(el => el.classList.add("reveal-init"));
        requestAnimationFrame(() => { revealEls.forEach(el => revealObs.observe(el)); });
      });
    }

  }, 0); // end Task A

  // Task B: forms + countdown + blog tracking + chatbot — separate task
  setTimeout(() => {

    // Consultation form
    const consultForm = document.getElementById("consultation-form");
    const consultAlert = document.getElementById("form-alert");
    if (consultForm) {
      consultForm.addEventListener("submit", e => {
        e.preventDefault();
        if (!consultForm.checkValidity()) { consultForm.reportValidity(); return; }
        const submitBtn = consultForm.querySelector('[type="submit"]');
        if (submitBtn) submitBtn.disabled = true;
        const data = {
          type: "consultation",
          name: document.getElementById("form-name").value,
          email: document.getElementById("form-email").value,
          phone: document.getElementById("form-phone").value,
          relocation: document.getElementById("form-relocation").value,
          details: document.getElementById("form-details").value
        };
        const url = window.location.pathname === "/" ? "/mail.php" : "../mail.php";
        fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) })
          .then(r => r.json())
          .then(r => {
            if (r.ok && consultAlert) {
              consultAlert.style.display = "flex";
              consultForm.reset();
              consultForm.classList.remove("was-validated");
              consultAlert.scrollIntoView({ behavior: "smooth", block: "nearest" });
              setTimeout(() => { consultAlert.style.display = "none"; }, 5000);
              if (typeof gtag === "function") {
                gtag("event", "consultation_form_submit", { event_category: "lead", event_label: "Consultation Form" });
                gtag("event", "conversion", { send_to: "AW-18221941570/A9mqCOy81MQcEMKG8_BD" });
              }
            } else {
              if (submitBtn) submitBtn.disabled = false;
              alert("Mesaj gönderilemedi. Lütfen WhatsApp veya e-posta ile ulaşın.");
            }
          })
          .catch(() => {
            if (submitBtn) submitBtn.disabled = false;
            alert("Bağlantı hatası. Lütfen WhatsApp veya e-posta ile ulaşın.");
          });
      });
    }

    // Webinar form
    const webinarForm = document.getElementById("webinar-form");
    const webinarAlert = document.getElementById("webinar-alert");
    if (webinarForm) {
      webinarForm.addEventListener("submit", e => {
        e.preventDefault();
        if (!webinarForm.checkValidity()) { webinarForm.reportValidity(); return; }
        const submitBtn = webinarForm.querySelector('[type="submit"]');
        if (submitBtn) submitBtn.disabled = true;
        const data = {
          type: "webinar",
          name: document.getElementById("webinar-name").value,
          email: document.getElementById("webinar-email").value,
          phone: document.getElementById("webinar-phone").value
        };
        const url = window.location.pathname === "/" ? "/mail.php" : "../mail.php";
        fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) })
          .then(r => r.json())
          .then(r => {
            if (r.ok && webinarAlert) {
              webinarAlert.style.display = "flex";
              webinarForm.reset();
              webinarAlert.scrollIntoView({ behavior: "smooth", block: "nearest" });
              setTimeout(() => { webinarAlert.style.display = "none"; }, 5000);
              if (typeof gtag === "function") {
                gtag("event", "webinar_form_submit", { event_category: "lead", event_label: "Webinar Registration" });
                gtag("event", "conversion", { send_to: "AW-18221941570/nVpmCL_R1MQcEMKG8_BD" });
              }
            } else {
              if (submitBtn) submitBtn.disabled = false;
              alert("Mesaj gönderilemedi. Lütfen WhatsApp veya e-posta ile ulaşın.");
            }
          })
          .catch(() => {
            if (submitBtn) submitBtn.disabled = false;
            alert("Bağlantı hatası. Lütfen WhatsApp veya e-posta ile ulaşın.");
          });
      });
    }

    // Countdown + dialog
    const dialog = document.getElementById("opp-dialog");
    if (dialog) {
      function lastWednesdayOfMonth(y, m) {
        const last = new Date(y, m + 1, 0);
        const dow = last.getDay();
        const diff = dow >= 3 ? dow - 3 : 7 - (3 - dow);
        return new Date(y, m, last.getDate() - diff);
      }
      const dialogClose = document.getElementById("dialog-close");
      const dialogCta   = document.getElementById("dialog-cta");
      if (dialogClose) dialogClose.addEventListener("click", () => dialog.close());
      if (dialogCta) dialogCta.addEventListener("click", () => {
        const webinar = document.getElementById("webinar");
        if (webinar) webinar.scrollIntoView({ behavior: "smooth" });
        dialog.close();
      });
      const cdDays = document.getElementById("countdown-days");
      const cdHrs  = document.getElementById("countdown-hours");
      const cdMins = document.getElementById("countdown-minutes");
      const cdSecs = document.getElementById("countdown-seconds");
      function tickCountdown() {
        const now = new Date();
        const y = now.getFullYear(), m = now.getMonth();
        let target = lastWednesdayOfMonth(y, m);
        if (now > target) {
          const next = new Date(y, m + 1, 1);
          target = lastWednesdayOfMonth(next.getFullYear(), next.getMonth());
        }
        target.setHours(20, 0, 0, 0);
        const diff = Math.max(0, target - now);
        const totalSec = Math.floor(diff / 1000);
        const d = Math.floor(totalSec / 86400);
        const h = Math.floor(totalSec % 86400 / 3600);
        const min = Math.floor(totalSec % 3600 / 60);
        const s = totalSec % 60;
        if (cdDays) cdDays.textContent = d;
        if (cdHrs)  cdHrs.textContent  = String(h).padStart(2, "0");
        if (cdMins) cdMins.textContent  = String(min).padStart(2, "0");
        if (cdSecs) cdSecs.textContent  = String(s).padStart(2, "0");
      }
      tickCountdown();
      setInterval(tickCountdown, 1000);
    }

    // Blog CTA tracking
    const blogMatch = window.location.pathname.match(/\/blog\/([^/]+)\//);
    if (blogMatch) {
      const slug = blogMatch[1];
      document.addEventListener("click", e => {
        const link = e.target.closest("a[href]");
        if (!link || !link.classList.contains("btn") || typeof gtag !== "function") return;
        const href = link.getAttribute("href") || "";
        if (href.includes("#contact") || href.includes("/uluslararasi-okul-danismanligi/")) {
          gtag("event", "blog_cta_click", { event_category: "lead", event_label: slug });
          gtag("event", "conversion", { send_to: "AW-18221941570/YZxyCOLI6cQcEMKG8_BD" });
        } else if (href.includes("/dubai/")) {
          gtag("event", "blog_dubai_cta_click", { event_category: "engagement", event_label: slug });
        } else if (href.includes("eduentry.com")) {
          gtag("event", "blog_eduentry_click", { event_category: "engagement", event_label: slug });
        }
      });
    }

    // Chatbot
    const chatBtn   = document.getElementById("chatbot-btn");
    const chatPopup = document.getElementById("chatbot-popup");
    const chatClose = document.getElementById("chatbot-close");
    if (chatBtn && chatPopup) {
      chatBtn.addEventListener("click", () => {
        const wasHidden = chatPopup.hidden;
        chatPopup.hidden = !wasHidden;
        if (wasHidden) {
          const iframe = chatPopup.querySelector("iframe[data-src]");
          if (iframe) { iframe.src = iframe.dataset.src; iframe.removeAttribute("data-src"); }
          if (typeof gtag === "function") gtag("event", "chatbot_open", { event_category: "engagement", event_label: "EduBot" });
        }
      });
      if (chatClose) chatClose.addEventListener("click", () => { chatPopup.hidden = true; });
    }

    // Section active-nav observer — lowest priority, use idle callback
    const idle = window.requestIdleCallback || (cb => setTimeout(cb, 100));
    idle(() => {
      const sections = document.querySelectorAll("section[id]");
      if (!sections.length || !navLinks.length) return;
      const sectionObs = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const id = entry.target.getAttribute("id");
            navLinks.forEach(link => {
              link.getAttribute("href") === `#${id}`
                ? link.classList.add("active")
                : link.classList.remove("active");
            });
          }
        });
      }, { root: null, rootMargin: "-30% 0px -60% 0px", threshold: 0 });
      sections.forEach(s => sectionObs.observe(s));
    });

  }, 0); // end Task B

});
