document.addEventListener("DOMContentLoaded", () => {
  const siteNavbar = document.querySelector(".sb-navbar");
  const revealTargets = document.querySelectorAll(".hero-banner, .hero-copy, .hero-panel, .section-heading, .field-card, .card, .table, .alert, .navbar, .btn, .field-card__top, .field-meta");

  revealTargets.forEach((element) => element.classList.add("reveal"));

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    {
      threshold: 0.15,
    },
  );

  revealTargets.forEach((element) => observer.observe(element));

  if (siteNavbar) {
    let lastScrollY = window.scrollY;
    let isHidden = false;
    const collapseThreshold = 72;

    siteNavbar.classList.remove("sb-navbar--hidden");

    const updateNavbarState = () => {
      const currentScrollY = window.scrollY;
      const scrollingDown = currentScrollY > lastScrollY;
      const shouldHide = currentScrollY > collapseThreshold && scrollingDown;

      if (shouldHide !== isHidden) {
        siteNavbar.classList.toggle("sb-navbar--hidden", shouldHide);
        isHidden = shouldHide;
      }

      lastScrollY = currentScrollY;
    };

    window.addEventListener(
      "scroll",
      () => {
        window.requestAnimationFrame(updateNavbarState);
      },
      { passive: true },
    );

    updateNavbarState();
  }

  const buttons = document.querySelectorAll(".btn");
  buttons.forEach((button) => {
    button.addEventListener("click", (event) => {
      const rect = button.getBoundingClientRect();
      const ripple = document.createElement("span");
      const size = Math.max(rect.width, rect.height);

      ripple.className = "ripple";
      ripple.style.width = `${size}px`;
      ripple.style.height = `${size}px`;
      ripple.style.left = `${event.clientX - rect.left - size / 2}px`;
      ripple.style.top = `${event.clientY - rect.top - size / 2}px`;

      button.style.position = "relative";
      button.style.overflow = "hidden";
      button.appendChild(ripple);

      window.setTimeout(() => ripple.remove(), 650);
    });
  });

  const inputs = document.querySelectorAll("input, select, textarea");
  inputs.forEach((input) => {
    input.classList.add("form-control");
    input.addEventListener("focus", () => input.parentElement?.classList.add("is-focused"));
    input.addEventListener("blur", () => input.parentElement?.classList.remove("is-focused"));
  });

  const navLinks = document.querySelectorAll(".navbar a[href]");
  const currentPath = window.location.pathname.replace(/\/+$/, "") || "/";

  navLinks.forEach((link) => {
    try {
      const linkPath = new URL(link.href).pathname.replace(/\/+$/, "") || "/";
      if (linkPath === currentPath) {
        link.classList.add("active");
      }
    } catch (error) {
      return;
    }
  });
});
