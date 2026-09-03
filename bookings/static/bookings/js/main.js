document.addEventListener("DOMContentLoaded", () => {
  const siteNavbar = document.querySelector(".sb-navbar");

  const revealTargets = document.querySelectorAll(
    [
      ".hero-banner",
      ".hero-copy",
      ".hero-panel",
      ".section-heading",
      ".field-search",
      ".field-card",
      ".field-detail-card",
      ".field-empty-state",
      ".card",
      ".table",
      ".alert",
    ].join(","),
  );

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (!reduceMotion && "IntersectionObserver" in window) {
    revealTargets.forEach((element) => {
      element.classList.add("reveal");
    });

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

    revealTargets.forEach((element) => {
      observer.observe(element);
    });
  } else {
    revealTargets.forEach((element) => {
      element.classList.add("is-visible");
    });
  }

  if (siteNavbar && !reduceMotion) {
    let lastScrollY = window.scrollY;
    let isHidden = false;
    let ticking = false;

    const collapseThreshold = 72;

    const updateNavbarState = () => {
      const currentScrollY = window.scrollY;
      const scrollingDown = currentScrollY > lastScrollY;

      const shouldHide = currentScrollY > collapseThreshold && scrollingDown;

      if (shouldHide !== isHidden) {
        siteNavbar.classList.toggle("sb-navbar--hidden", shouldHide);

        isHidden = shouldHide;
      }

      lastScrollY = currentScrollY;
      ticking = false;
    };

    window.addEventListener(
      "scroll",
      () => {
        if (!ticking) {
          window.requestAnimationFrame(updateNavbarState);

          ticking = true;
        }
      },
      {
        passive: true,
      },
    );
  }

  const navLinks = document.querySelectorAll(".navbar a[href]");

  const currentPath = window.location.pathname.replace(/\/+$/, "") || "/";

  navLinks.forEach((link) => {
    try {
      const linkPath = new URL(link.href).pathname.replace(/\/+$/, "") || "/";

      if (linkPath === currentPath) {
        link.classList.add("active");
      }
    } catch {
      // Bỏ qua liên kết không phải URL hợp lệ.
    }
  });
});
