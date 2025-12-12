/**
 * Attaches a scroll listener to hide/show an element.
 * @param {HTMLElement} element The element to hide/show.
 * @returns {function} A cleanup function to remove the event listener.
 */
export function setupAutoHide(element) {
  let lastScrollY = window.scrollY;
  let ticking = false;

  const handleScroll = () => {
    const currentScrollY = window.scrollY;

    if (currentScrollY > lastScrollY && currentScrollY > 100) {
      // Scrolling down
      element.classList.add('hide-widget');
    } else {
      // Scrolling up
      element.classList.remove('hide-widget');
    }
    lastScrollY = currentScrollY;
    ticking = false;
  };

  const onScroll = () => {
    if (!ticking) {
      window.requestAnimationFrame(handleScroll);
      ticking = true;
    }
  };

  window.addEventListener('scroll', onScroll);

  // Return a cleanup function
  return () => {
    window.removeEventListener('scroll', onScroll);
  };
}