// Main JavaScript functionality for StudentStay
document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize all components
    initializeNavbar();
    initializeLoadingStates();
    initializeFavorites();
    initializeSearchEnhancements();
    initializeScrollAnimations();
    initializeTooltips();
    initializeImageLazyLoading();
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

// Navbar functionality
function initializeNavbar() {
    const navbar = document.querySelector('.custom-navbar');
    
    // Navbar scroll effect
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    // Mobile menu enhancements
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            // Add animation class
            navbarCollapse.classList.toggle('show-mobile');
        });
    }
}

// Loading states
function initializeLoadingStates() {
    const loadingOverlay = document.getElementById('loading-overlay');
    
    // Show loading overlay for form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            // Don't show loading for search forms
            if (!form.classList.contains('hero-search-form') && 
                !form.classList.contains('filter-form')) {
                showLoading();
            }
        });
    });
    
    // Show loading for navigation
    const navLinks = document.querySelectorAll('a[href]:not([href^="#"]):not([href^="mailto"]):not([href^="tel"])');
    navLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            // Only show loading for internal links
            if (link.hostname === window.location.hostname) {
                showLoading();
                // Hide loading after timeout as fallback
                setTimeout(hideLoading, 3000);
            }
        });
    });
    
    // Hide loading when page loads
    window.addEventListener('load', hideLoading);
}

function showLoading() {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'flex';
    }
}

function hideLoading() {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
    }
}

// Favorites functionality
function initializeFavorites() {
    // Get favorites from localStorage
    let favorites = JSON.parse(localStorage.getItem('favoriteHostels') || '[]');
    
    // Update UI for existing favorites
    updateFavoriteButtons(favorites);
    
    // Handle favorite button clicks
    const favoriteButtons = document.querySelectorAll('.favorite-btn');
    favoriteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const hostelId = this.getAttribute('data-hostel-id');
            toggleFavorite(hostelId, this);
        });
    });
}

function toggleFavorite(hostelId, button) {
    let favorites = JSON.parse(localStorage.getItem('favoriteHostels') || '[]');
    const icon = button.querySelector('i');
    const text = button.querySelector('span');
    
    if (favorites.includes(hostelId)) {
        // Remove from favorites
        favorites = favorites.filter(id => id !== hostelId);
        icon.classList.replace('fas', 'far');
        icon.classList.remove('text-danger');
        if (text) text.textContent = 'Save';
        
        // Show notification
        showNotification('Removed from favorites', 'info');
    } else {
        // Add to favorites
        favorites.push(hostelId);
        icon.classList.replace('far', 'fas');
        icon.classList.add('text-danger');
        if (text) text.textContent = 'Saved';
        
        // Show notification
        showNotification('Added to favorites', 'success');
    }
    
    localStorage.setItem('favoriteHostels', JSON.stringify(favorites));
}

function updateFavoriteButtons(favorites) {
    const favoriteButtons = document.querySelectorAll('.favorite-btn');
    favoriteButtons.forEach(function(button) {
        const hostelId = button.getAttribute('data-hostel-id');
        if (favorites.includes(hostelId)) {
            const icon = button.querySelector('i');
            const text = button.querySelector('span');
            icon.classList.replace('far', 'fas');
            icon.classList.add('text-danger');
            if (text) text.textContent = 'Saved';
        }
    });
}

// Enhanced search functionality
function initializeSearchEnhancements() {
    const searchForm = document.querySelector('.hero-search-form');
    if (!searchForm) return;
    
    // Add search suggestions (if you implement an API endpoint)
    const searchInput = searchForm.querySelector('input[type="text"]');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                // Implement search suggestions here
                // fetchSearchSuggestions(this.value);
            }, 300);
        });
    }
    
    // Enhanced form validation
    searchForm.addEventListener('submit', function(e) {
        const formData = new FormData(this);
        let hasValidInput = false;
        
        for (let value of formData.values()) {
            if (value.trim() !== '') {
                hasValidInput = true;
                break;
            }
        }
        
        if (!hasValidInput) {
            e.preventDefault();
            showNotification('Please select at least one search criteria', 'warning');
        }
    });
}

// Scroll animations
function initializeScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                
                // Counter animation for stats
                if (entry.target.classList.contains('stat-number')) {
                    animateCounter(entry.target);
                }
            }
        });
    }, observerOptions);
    
    // Observe elements
    const animatedElements = document.querySelectorAll([
        '.hostel-card',
        '.step-card',
        '.stat-item',
        '.content-section'
    ].join(', '));
    
    animatedElements.forEach(function(el) {
        observer.observe(el);
    });
}

// Counter animation for statistics
function animateCounter(element) {
    const target = parseInt(element.textContent.replace(/[^0-9]/g, ''));
    const duration = 2000;
    const step = target / (duration / 16);
    let current = 0;
    
    const timer = setInterval(function() {
        current += step;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        
        element.textContent = Math.floor(current).toLocaleString() + 
                             (element.textContent.includes('+') ? '+' : '');
    }, 16);
}

// Initialize tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Image lazy loading
function initializeImageLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    }, {
        rootMargin: '0px 0px 200px 0px'
    });
    
    images.forEach(function(img) {
        imageObserver.observe(img);
    });
}

// Show notification
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.role = 'alert';
    notification.innerHTML = `
        <strong>${message}</strong>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(notification);
        bsAlert.close();
    }, 5000);
}