document.addEventListener("DOMContentLoaded", () => {
  const siteNavbar = document.querySelector(".sb-navbar");

  const revealTargets = document.querySelectorAll(
    [
      ".reveal",
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

  const bookingForm = document.querySelector("[data-booking-form]");

  if (bookingForm) {
    const startInput = bookingForm.querySelector("#id_start_time");
    const endInput = bookingForm.querySelector("#id_end_time");
    const durationOutput = bookingForm.querySelector("[data-booking-duration]");
    const totalOutput = bookingForm.querySelector("[data-booking-total]");
    const preview = bookingForm.querySelector("[data-booking-price-preview]");
    const messageOutput = bookingForm.querySelector("[data-booking-price-message]");
    const slotButtons = document.querySelectorAll("[data-booking-slot]");
    const pricePerHour = Number.parseFloat(bookingForm.dataset.pricePerHour || "0");
    const currencyFormatter = new Intl.NumberFormat("vi-VN", {
      maximumFractionDigits: 0,
    });

    const isSameLocalDate = (firstDate, secondDate) =>
      firstDate.getFullYear() === secondDate.getFullYear() &&
      firstDate.getMonth() === secondDate.getMonth() &&
      firstDate.getDate() === secondDate.getDate();

    const resetPreview = (message, isError = false) => {
      durationOutput.textContent = "—";
      totalOutput.textContent = "—";
      messageOutput.textContent = message;
      preview.classList.toggle("has-error", isError);
    };

    const updatePricePreview = () => {
      if (!startInput.value || !endInput.value) {
        resetPreview("Chọn thời gian để xem tổng tiền.");
        return;
      }

      const startTime = new Date(startInput.value);
      const endTime = new Date(endInput.value);

      if (Number.isNaN(startTime.getTime()) || Number.isNaN(endTime.getTime())) {
        resetPreview("Thời gian chưa hợp lệ.", true);
        return;
      }

      if (!isSameLocalDate(startTime, endTime)) {
        resetPreview("Giờ bắt đầu và kết thúc phải trong cùng ngày.", true);
        return;
      }

      const durationHours = (endTime - startTime) / 3600000;

      if (durationHours <= 0) {
        resetPreview("Giờ kết thúc phải sau giờ bắt đầu.", true);
        return;
      }

      const totalPrice = durationHours * pricePerHour;
      const formattedDuration = durationHours.toLocaleString("vi-VN", {
        maximumFractionDigits: 2,
      });

      durationOutput.textContent = `${formattedDuration} giờ`;
      totalOutput.textContent = `${currencyFormatter.format(totalPrice)} VNĐ`;
      messageOutput.textContent = "Tổng tiền chính thức sẽ được hệ thống tính lại khi xác nhận.";
      preview.classList.remove("has-error");
    };

    slotButtons.forEach((button) => {
      button.addEventListener("click", () => {
        slotButtons.forEach((slot) => slot.classList.remove("is-selected"));
        button.classList.add("is-selected");
        startInput.value = button.dataset.start;
        endInput.value = button.dataset.end;
        updatePricePreview();

        if (window.innerWidth < 992 && !reduceMotion) {
          bookingForm.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      });
    });

    startInput.addEventListener("input", updatePricePreview);
    endInput.addEventListener("input", updatePricePreview);
    updatePricePreview();
  }
});
