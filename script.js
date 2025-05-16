// JavaScript for TurnClicksToClients.com

document.addEventListener('DOMContentLoaded', () => {
    console.log('TurnClicksToClients.com website loaded.');

    // Initialize FAQ accordion for enhanced offer page
    initFaqAccordion();

    // Smooth scroll for navigation links
    const navLinks = document.querySelectorAll('header nav ul li a[href^="#"], .cta-button[href^="#"]');
    const header = document.querySelector('header');
    const headerHeight = header ? header.offsetHeight : 70;

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            let targetId = this.getAttribute('href');
            // Ensure targetId is not just "#"
            if (targetId.length > 1) {
                let targetElement = document.querySelector(targetId);
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - headerHeight,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Sticky header functionality
    const siteHeader = document.querySelector('header');
    if (siteHeader) {
        let sticky = siteHeader.offsetTop;
        function handleScroll() {
            if (window.pageYOffset > sticky + 50) { // Add a small buffer
                siteHeader.classList.add('sticky-header');
            } else {
                siteHeader.classList.remove('sticky-header');
            }
        }
        window.addEventListener('scroll', handleScroll);
        handleScroll(); // Initial check in case the page is already scrolled
    }

    // Hamburger menu and mobile nav toggle (from index.html)
    const hamburger = document.querySelector('.hamburger');
    const navUl = document.getElementById('main-nav');
    if (hamburger && navUl) {
      function closeAllDropdowns() {
        document.querySelectorAll('.dropdown-parent').forEach(li => li.classList.remove('open'));
      }
      hamburger.addEventListener('click', function() {
        const open = navUl.classList.toggle('open');
        hamburger.setAttribute('aria-expanded', open);
        if (!open) closeAllDropdowns();
      });
      // Dropdowns for mobile
      navUl.querySelectorAll('.dropdown-parent > a').forEach(link => {
        link.addEventListener('click', function(e) {
          if (window.innerWidth <= 900) {
            e.preventDefault();
            const parent = this.parentElement;
            const isOpen = parent.classList.toggle('open');
            // Close others
            navUl.querySelectorAll('.dropdown-parent').forEach(li => {
              if (li !== parent) li.classList.remove('open');
            });
          }
        });
      });
      // Close nav on link click (conversion best practice)
      navUl.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', function() {
          if (window.innerWidth <= 900) {
            navUl.classList.remove('open');
            closeAllDropdowns();
          }
        });
      });
    }

    // Fade-in elements on scroll
    const observerOptions = {
        root: null, // relative to document viewport
        rootMargin: '0px',
        threshold: 0.1 // 10% of the item is visible
    };

    const observerCallback = (entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target); // Stop observing once visible
            }
        });
    };

    const intersectionObserver = new IntersectionObserver(observerCallback, observerOptions);

    const fadeElements = document.querySelectorAll('.niche-item, .team-card, .pricing-card, .testimonial-card, .special-promotion-box, .guarantee-box, .unique-mechanism-explanation, .deeper-benefit-explanation, .commitment-box, .transition-to-solution, #core-offer .container > h2, #core-offer .container > p, #ideal-clients .container > h2, #ideal-clients .container > p, #pricing .container > h2, #pricing .container > p, #guarantee .container > h2');

    fadeElements.forEach(el => {
        el.classList.add('fade-in-element'); // Add base class for initial state
        intersectionObserver.observe(el);
    });

    // ROI Calculator Logic
    const avgClientValueSlider = document.getElementById('avgClientValue');
    const currentClientsSlider = document.getElementById('currentClients');
    const conversionRateSlider = document.getElementById('conversionRate');

    const avgClientValueOutput = document.querySelector('output[for="avgClientValue"]');
    const currentClientsOutput = document.querySelector('output[for="currentClients"]');
    const conversionRateOutput = document.querySelector('output[for="conversionRate"]');

    const additionalClientsDisplay = document.getElementById('additionalClients');
    const monthlyRevenueDisplay = document.getElementById('monthlyRevenue');
    const annualRevenueDisplay = document.getElementById('annualRevenue');
    const roiValueDisplay = document.getElementById('roiValue');

    const ACCELERATE_PLAN_COST = 1500; // Monthly cost

    function formatCurrency(value) {
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(value);
    }

    function calculateROI() {
        if (!avgClientValueSlider || !currentClientsSlider || !conversionRateSlider ||
            !avgClientValueOutput || !currentClientsOutput || !conversionRateOutput ||
            !additionalClientsDisplay || !monthlyRevenueDisplay || !annualRevenueDisplay || !roiValueDisplay) {
            // console.error("One or more ROI calculator elements are missing.");
            return; // Exit if any element is not found
        }

        const avgClientValue = parseFloat(avgClientValueSlider.value);
        const currentClients = parseInt(currentClientsSlider.value);
        const conversionRate = parseInt(conversionRateSlider.value); // Currently not used in core projection, but available

        // Update slider output displays
        avgClientValueOutput.textContent = formatCurrency(avgClientValue);
        currentClientsOutput.textContent = currentClients;
        // Ensure conversion rate output always matches slider value
        conversionRateOutput.textContent = conversionRateSlider.value + '%';

        // --- Calculation Logic (Revised to include Conversion Rate impact) ---
        // Scale leads added by system based on current size
        const BASE_NEW_LEADS = 50; // Base new leads for established businesses
        // Scale new leads more appropriately based on current client load
        const NEW_LEADS_FROM_SYSTEM = Math.min(BASE_NEW_LEADS, Math.max(10, currentClients * 7));

        const SYSTEM_CONVERSION_UPLIFT_FACTOR = 1.5; // Our system improves current conversion rate by 50%
        const SYSTEM_MIN_CONVERSION_RATE = 20;   // Our system achieves at least 20% conversion
        const SYSTEM_MAX_CONVERSION_RATE = 45;   // Our system's conversion rate is realistically capped at 45%

        // Adjust the minimum clients based on current client input
        // This creates a more realistic projection for small businesses
        const MIN_ADDITIONAL_CLIENTS_FLOOR = Math.max(1, Math.floor(currentClients * 0.6));
        const MAX_ADDITIONAL_CLIENTS_CAP = 50;  // Maximum additional clients we project

        // 1. Estimate current leads
        let currentUserLeads = 0;
        if (conversionRate > 0) {
            currentUserLeads = currentClients / (conversionRate / 100);
        } else { // Avoid division by zero if conversionRate is somehow 0 (slider min is 1)
            currentUserLeads = currentClients * 20; // Assume a 5% conversion rate if 0 is given
        }

        // 2. Add system-generated leads
        const totalLeadsWithSystem = currentUserLeads + NEW_LEADS_FROM_SYSTEM;

        // 3. Determine effective system conversion rate
        let effectiveSystemConversionRate = Math.max(SYSTEM_MIN_CONVERSION_RATE, conversionRate * SYSTEM_CONVERSION_UPLIFT_FACTOR);
        effectiveSystemConversionRate = Math.min(effectiveSystemConversionRate, SYSTEM_MAX_CONVERSION_RATE);

        // 4. Calculate total projected clients with our system
        const totalProjectedClientsWithSystem = totalLeadsWithSystem * (effectiveSystemConversionRate / 100);

        // 5. Determine additional clients (raw)
        const additionalClientsRaw = totalProjectedClientsWithSystem - currentClients;

        // 6. Apply realistic boundaries and ensure it's an integer
        let projectedAdditionalClients = Math.floor(additionalClientsRaw);
        projectedAdditionalClients = Math.max(MIN_ADDITIONAL_CLIENTS_FLOOR, projectedAdditionalClients);
        // Cap additional clients to a multiple of current clients (2x) or 10, whichever is higher
        const MAX_REASONABLE_ADDITIONAL = Math.max(10, Math.floor(currentClients * 2));
        projectedAdditionalClients = Math.min(projectedAdditionalClients, MAX_REASONABLE_ADDITIONAL);

        // Special case for very small businesses (1-5 clients)
        // Makes results more realistic and proportional
        if (currentClients <= 5) {
            // Cap additional clients to not exceed currentClients
            projectedAdditionalClients = Math.min(projectedAdditionalClients, currentClients);
        }

        // Ensure it doesn't show negative additional clients if somehow current setup is better than projection inputs
        projectedAdditionalClients = Math.max(0, projectedAdditionalClients);

        const monthlyRevenueIncrease = projectedAdditionalClients * avgClientValue;
        const annualRevenueGrowth = monthlyRevenueIncrease * 12;

        const investment3Months = ACCELERATE_PLAN_COST * 3;
        const gain3Months = monthlyRevenueIncrease * 3;
        let roi3Months = 0;
        if (investment3Months > 0) {
            roi3Months = (gain3Months - investment3Months) / investment3Months;
             // If gain is less than investment, it's a loss, but ROI can still be calculated this way.
            // We want to show it as a multiplier like 2.5x, so if it's 150% return, it's 1.5x on top of investment, total 2.5x
            // Or more simply: (Total Gain / Total Investment) = Growth Factor
            roi3Months = gain3Months / investment3Months;
        }


        // Update result displays
        additionalClientsDisplay.textContent = projectedAdditionalClients;
        monthlyRevenueDisplay.textContent = formatCurrency(monthlyRevenueIncrease);
        annualRevenueDisplay.textContent = formatCurrency(annualRevenueGrowth);
        roiValueDisplay.textContent = roi3Months.toFixed(1) + 'x';
    }

    // Add event listeners to sliders
    if (avgClientValueSlider) avgClientValueSlider.addEventListener('input', calculateROI);
    if (currentClientsSlider) currentClientsSlider.addEventListener('input', calculateROI);
    if (conversionRateSlider) conversionRateSlider.addEventListener('input', calculateROI);

    // Initial calculation on page load
    calculateROI();

    // Dynamic Booking Counter Logic
    const bookingBanner = document.getElementById('dynamic-booking-banner');
    const appointmentsCountSpan = document.getElementById('booked-appointments-count');

    if (bookingBanner && appointmentsCountSpan) {
        const MIN_WEEKLY_APPOINTMENTS = 100; // Min target for a full week. Adjusted slightly to ensure threshold can be met.
        const MAX_WEEKLY_APPOINTMENTS = 191; // Max target for a full week
        const MIN_DISPLAY_THRESHOLD = 93;   // Never display below this
        const MIN_DAILY_INCREMENT = 1; // Ensure at least a small jump each day

        function getWeekStartDate(date) {
            const d = new Date(date);
            const day = d.getDay();
            const diff = d.getDate() - day + (day === 0 ? -6 : 1); // Adjust so Monday is 1st day
            return new Date(d.setDate(diff)).setHours(0, 0, 0, 0);
        }

        function initializeOrUpdateCounter() {
            const now = new Date();
            const currentWeekStartMs = getWeekStartDate(now);

            let weeklyTarget = parseInt(localStorage.getItem('tctc_weeklyTarget') || '0', 10);
            let lastStoredWeekStartMs = parseInt(localStorage.getItem('tctc_weekStartMs') || '0', 10);
            let currentDisplayCount = parseInt(localStorage.getItem('tctc_lastDisplayedCount') || '0', 10);

            if (currentWeekStartMs !== lastStoredWeekStartMs) { // New week or first time
                weeklyTarget = Math.floor(Math.random() * (MAX_WEEKLY_APPOINTMENTS - MIN_WEEKLY_APPOINTMENTS + 1)) + MIN_WEEKLY_APPOINTMENTS;
                // Ensure weekly target is sensible with the display threshold
                weeklyTarget = Math.max(weeklyTarget, MIN_DISPLAY_THRESHOLD + (7 * MIN_DAILY_INCREMENT)); // e.g. ensure it can grow from threshold over a week
                localStorage.setItem('tctc_weeklyTarget', weeklyTarget);
                localStorage.setItem('tctc_weekStartMs', currentWeekStartMs);
                currentDisplayCount = MIN_DISPLAY_THRESHOLD; // Start new week at the new minimum threshold
                localStorage.setItem('tctc_lastDisplayedCount', currentDisplayCount);
            } else {
                // If same week, ensure currentDisplayCount isn't below new threshold due to code changes
                currentDisplayCount = Math.max(currentDisplayCount, MIN_DISPLAY_THRESHOLD);
            }

            const dayOfWeek = now.getDay(); // 0 (Sun) to 6 (Sat)
            const adjustedDay = (dayOfWeek === 0) ? 7 : dayOfWeek; // Mon=1, Tue=2, ..., Sun=7

            const dailyProgressFactors = [0, 0.15, 0.30, 0.50, 0.70, 0.90, 1, 1]; // Base factors
            let proportionalTodayCount = Math.floor(weeklyTarget * dailyProgressFactors[adjustedDay]);

            // Ensure idealTodayCount is always >= currentDisplayCount from previous session (if same week) + min increment,
            // OR the proportional count, whichever makes sense, but not less than threshold.
            // This logic ensures the number generally goes up each day or meets the day's target.
            let idealTodayCount = Math.max(proportionalTodayCount, currentDisplayCount + MIN_DAILY_INCREMENT, MIN_DISPLAY_THRESHOLD);
            idealTodayCount = Math.min(idealTodayCount, weeklyTarget); // Don't exceed overall weekly target

            // On Mondays (or the first day of the week for the script), idealTodayCount should be based on its proportion or threshold.
            // For other days, it should aim to be higher than the last displayed count.
            if (currentWeekStartMs === lastStoredWeekStartMs && currentDisplayCount >= MIN_DISPLAY_THRESHOLD) { // If it's not the first day of a new week cycle for storage
                 // Ensure that idealTodayCount is at least the last shown count (or a bit more)
                 idealTodayCount = Math.max(idealTodayCount, currentDisplayCount);
            }

            // Final check: if it's still below the base min display threshold, set it to that.
            idealTodayCount = Math.max(idealTodayCount, MIN_DISPLAY_THRESHOLD);

            // Ensure current display count starts at or above threshold
            currentDisplayCount = Math.max(currentDisplayCount, MIN_DISPLAY_THRESHOLD);
            appointmentsCountSpan.textContent = currentDisplayCount;

            // Animate towards idealTodayCount
            if (window.tctcBookingInterval) clearInterval(window.tctcBookingInterval);

            window.tctcBookingInterval = setInterval(() => {
                if (currentDisplayCount < idealTodayCount) {
                    currentDisplayCount++;
                    appointmentsCountSpan.textContent = currentDisplayCount;
                    localStorage.setItem('tctc_lastDisplayedCount', currentDisplayCount);
                } else if (currentDisplayCount > idealTodayCount) { // Should only happen if idealTodayCount logic allows decrease (e.g. error or drastic change)
                     currentDisplayCount--; // Or snap: currentDisplayCount = idealTodayCount;
                     appointmentsCountSpan.textContent = currentDisplayCount;
                     localStorage.setItem('tctc_lastDisplayedCount', currentDisplayCount);
                } else {
                     // Target reached, maybe a slight random tick later for activity illusion
                    if (Math.random() < 0.1 && currentDisplayCount < weeklyTarget) { // 10% chance to increment if not at max weekly
                        // This creates a small chance of ticking up even after reaching daily ideal, towards weekly max
                        currentDisplayCount++;
                        appointmentsCountSpan.textContent = currentDisplayCount;
                        localStorage.setItem('tctc_lastDisplayedCount', currentDisplayCount);
                    } else if (currentDisplayCount >= weeklyTarget) {
                        clearInterval(window.tctcBookingInterval); // Stop if weekly target met
                    }
                }
            }, 90000); // Update approx every 1.5 mins to simulate activity, adjust as desired
        }

        initializeOrUpdateCounter(); // Initialize and start counter animation
        // Optionally re-check/re-animate on visibility change if tab was backgrounded for a long time
        document.addEventListener("visibilitychange", () => {
            if (document.visibilityState === "visible") {
                initializeOrUpdateCounter();
            } else {
                if (window.tctcBookingInterval) clearInterval(window.tctcBookingInterval);
            }
        });
    }

    // Smooth scroll for anchor links (ensure this is not duplicated)
    // Note: A similar smooth scroll for navLinks is already present at the top.
    // This one targets any a[href^="#"] which might be more general.
    // Consolidating or ensuring they don't conflict is good.
    // For now, assuming the top one handles navigation, and this could be for in-page links.
    // If all links are covered by the first, this second one can be removed.
    // Based on current structure, the first one (navLinks) is more specific for header/CTA.
    // This broader one might be useful for other # links on pages.
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        // Check if this link is already handled by the navLinks smooth scroll
        let alreadyHandled = false;
        navLinks.forEach(navLink => {
            if (navLink === anchor) {
                alreadyHandled = true;
            }
        });

        if (!alreadyHandled) {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const targetId = this.getAttribute('href');
                // Ensure targetId is not just "#"
                if (targetId.length > 1) {
                    const targetElement = document.querySelector(targetId);
                    if (targetElement) {
                        // Use a consistent offset, perhaps headerHeight if it's a general link
                        // For now, direct scroll for non-nav links
                        targetElement.scrollIntoView({
                            behavior: 'smooth'
                        });
                    }
                }
            });
        }
    });

    // Chat Widget Logic
    const chatButton = document.getElementById('chat-widget-button');
    const chatModal = document.getElementById('chat-modal');
    const chatModalCloseButton = document.getElementById('chat-modal-close');
    const chatContactForm = document.getElementById('chat-contact-form');
    const chatIndustrySelect = document.getElementById('chat-industry'); // Get the select element

    if (chatButton && chatModal && chatModalCloseButton && chatContactForm && chatIndustrySelect) {
        // Define the list of niches
        const idealClientNiches = [
            "Child Care Centers",
            "Cosmetic Dentists",
            "PMU Artists",
            "Non-Surgical Body Contouring",
            "Weight Loss Clinics",
            "High-End Chiropractors",
            "Sleep Apnea & Snoring Clinics",
            "Hearing Aid & Audiology Clinics",
            "DME Clinics",
            "Other" // Add an 'Other' option
        ];

        // Populate industry dropdown
        chatIndustrySelect.innerHTML = ''; // Clear existing options
        const defaultOption = document.createElement('option');
        defaultOption.value = "";
        defaultOption.textContent = "Select your industry...";
        defaultOption.disabled = true;
        defaultOption.selected = true;
        chatIndustrySelect.appendChild(defaultOption);

        idealClientNiches.forEach(niche => {
            const option = document.createElement('option');
            option.value = niche.toLowerCase().replace(/ & /g, '-').replace(/\s+/g, '-').replace(/[\/()]/g, '');
            option.textContent = niche;
            chatIndustrySelect.appendChild(option);
        });

        function openChatModal() {
            chatModal.classList.remove('modal-hidden');
            chatModal.classList.add('modal-visible');
            document.body.style.overflow = 'hidden'; // Prevent background scroll
        }

        function closeChatModal() {
            chatModal.classList.remove('modal-visible');
            chatModal.classList.add('modal-hidden');
            document.body.style.overflow = ''; // Restore background scroll
        }

        chatButton.addEventListener('click', openChatModal);
        chatModalCloseButton.addEventListener('click', closeChatModal);

        // Close modal if user clicks on the overlay background
        chatModal.addEventListener('click', (event) => {
            if (event.target === chatModal) {
                closeChatModal();
            }
        });

        // Close modal with Escape key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape' && !chatModal.classList.contains('modal-hidden')) {
                closeChatModal();
            }
        });

        // Handle form submission
        chatContactForm.addEventListener('submit', (event) => {
            event.preventDefault();
            const formData = new FormData(chatContactForm);
            const data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });

            // Map form field names to Supabase column names/expected JSON keys
            if (data.name) {
                data.fullName = data.name; // Create fullName from data.name
            }

            // businessName is sent as is (camelCase) from HTML name="businessName"

            // Add other mappings here if needed, e.g.:

            const supabaseUrl = 'https://eumhqssfvkyuepyrtlqj.supabase.co/functions/v1/send-chat-to-slack';

            // Show a generic "sending" message or disable the button
            const submitButton = chatContactForm.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.textContent;
            submitButton.disabled = true;
            submitButton.textContent = 'Sending...';

            // Hide any previous success/error messages from the modal
            const successMessageDiv = document.getElementById('chat-success-message');
            const errorMessageDiv = document.getElementById('chat-error-message'); // Assuming you might add one
            if (successMessageDiv) successMessageDiv.style.display = 'none';
            if (errorMessageDiv) errorMessageDiv.style.display = 'none';


            fetch(supabaseUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            })
            .then(response => {
                if (!response.ok) {
                    // Try to get error message from response, or use a default
                    return response.json().then(errData => {
                        throw new Error(errData.error || `Network response was not ok: ${response.statusText}`);
                    }).catch(() => { // If response.json() fails or no errData.error
                        throw new Error(`Network response was not ok: ${response.statusText}`);
                    });
                }
                return response.json();
            })
            .then(responseData => {
                console.log('Success:', responseData);
                chatContactForm.style.setProperty('display', 'none', 'important'); // Hide the form using !important
                if (successMessageDiv) {
                    successMessageDiv.style.display = 'block'; // Show the success message
                } else {
                    alert("Thank You! Our team has been alerted and will get back to you as soon as possible.");
                }
                // chatContactForm.reset(); // Reset is less critical if form is hidden
                // Keep modal open to show success message
            })
            .catch((error) => {
                console.error('Error:', error);
                // Display an error message to the user in the modal
                if (errorMessageDiv) {
                    errorMessageDiv.textContent = 'Error: ' + error.message + '. Please try again or contact support.';
                    errorMessageDiv.style.display = 'block';
                } else {
                    // Fallback alert for errors
                    alert('There was an error sending your message: ' + error.message + '. Please try again.');
                }
            })
            .finally(() => {
                // Re-enable the submit button and restore its text
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.textContent = originalButtonText;
                }
                // We don't close the modal immediately here to allow the user to see the success/error message.
                // The success message itself in the HTML contains instructions to close.
                // If an error occurs, the user might want to try submitting again.
            });
        });
    }

    // Qualification Checklist Logic
    const checklistForm = document.getElementById('qualifying-checklist-form');
    const checklistCheckboxes = checklistForm ? checklistForm.querySelectorAll('input[type="checkbox"]') : [];
    const checklistResultsDiv = document.getElementById('checklist-results');

    function updateChecklistResults() {
        if (!checklistForm || !checklistResultsDiv || checklistCheckboxes.length === 0) return;

        const checkedCount = Array.from(checklistCheckboxes).filter(checkbox => checkbox.checked).length;
        let resultHTML = '';

        if (checkedCount === 0 && !Array.from(checklistCheckboxes).some(checkbox => checkbox.matches(':hover'))) {
             // Optional: only show results if at least one box is checked, or don't show if none checked unless maybe hovering
             checklistResultsDiv.style.display = 'none';
             return;
        }

        if (checkedCount >= 5) {
            resultHTML = `
                <h4>You're Likely an Ideal Candidate!</h4>
                <p>Checking ${checkedCount} boxes strongly suggests you're ready for the kind of predictable growth our system provides. We encourage you to apply today while spots in your city are still available.</p>
                <p><a href="#pricing">See Plans & Apply Now</a> or <a href="#quiz-start">Take the 30-Sec Quiz</a></p>
            `;
        } else if (checkedCount >= 3) { // 3 or 4 boxes
            resultHTML = `
                <h4>You Show Strong Potential!</h4>
                <p><a href="#cta-contact" style="font-weight:bold; color:#007bff; text-decoration:underline;">Submit Your Application to Partner With Us</a>—or, if you want to see for yourself just how quickly your growth can ignite, <a href="#quiz-start" style="font-weight:bold; color:#28a745; text-decoration:underline;">complete our 30-Second Discovery Quiz</a>. This is your moment to move from 'maybe' to momentum—before your competitors even realize what they've missed.</p>
            `;
        } else { // Fewer than 3 boxes
            resultHTML = `
                <h4>IM READY TO GET STARTED</h4>
                <p><strong>There are two kinds of people reading this right now:</strong> Those who will keep searching, hoping for a breakthrough, and those who seize the moment and take decisive action. If you see the value in a proven system, but want to understand exactly how it works—or if you already know you want to partner with us and claim your edge—your next step is clear.</p>
                <p><a href="#core-offer" style="font-weight:bold; color:#007bff; text-decoration:underline;">Learn About Our System</a> or <a href="#cta-contact" style="font-weight:bold; color:#28a745; text-decoration:underline;">Send Us a Message If You'd Like To Partner With Us</a>. The window of opportunity is open—but it never stays open for long. Decide. Act. The future belongs to those who move first.</p>
            `;
        }

        checklistResultsDiv.innerHTML = resultHTML;
        checklistResultsDiv.style.display = 'block'; // Show the results box
    }

    if (checklistForm) {
        checklistForm.addEventListener('change', updateChecklistResults);
        // Initial check in case of browser back/forward preserving state
        // updateChecklistResults();
        // --> Decided against initial check to avoid showing results before interaction
    }

    // Open chat modal when 'Send Us a Message If You\'d Like To Partner With Us' is clicked
    document.body.addEventListener('click', function(e) {
        const target = e.target;
        if (target.tagName === 'A' && target.textContent.trim().replace(/\s+/g, ' ') === "Send Us a Message If You'd Like To Partner With Us") {
            e.preventDefault();
            const chatButton = document.getElementById('chat-widget-button');
            if (chatButton) chatButton.click();
        }
    });

    /**
     * Initialize the FAQ accordion functionality
     */
    function initFaqAccordion() {
        const faqItems = document.querySelectorAll('.faq-item');

        faqItems.forEach(item => {
            const question = item.querySelector('.faq-question');

            if (question) {
                question.addEventListener('click', () => {
                    // Toggle active class on the clicked item
                    item.classList.toggle('active');

                    // Close other items
                    faqItems.forEach(otherItem => {
                        if (otherItem !== item && otherItem.classList.contains('active')) {
                            otherItem.classList.remove('active');
                        }
                    });
                });
            }
        });
    }
});