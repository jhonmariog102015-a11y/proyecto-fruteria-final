// CAMBIO GUÍA 4: reubicado en la estructura modular de JavaScript.
/*!
* Start Bootstrap - Agency v7.0.12 (https://startbootstrap.com/theme/agency)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-agency/blob/master/LICENSE)
*/
//
// Scripts
// 

window.addEventListener('DOMContentLoaded', event => {

    const navbar = document.getElementById('mainNav');
    let lastScrollTop = 0;

    const controlarNavbar = function () {
        if (!navbar) {
            return;
        }

        const scrollTop = window.scrollY;

        if (scrollTop <= 20) {
            navbar.classList.add('nav-transparent');
            navbar.classList.remove('nav-scrolled');
        } else if (scrollTop > lastScrollTop) {
            navbar.classList.remove('nav-transparent');
            navbar.classList.add('nav-scrolled');
        } else {
            navbar.classList.add('nav-transparent');
            navbar.classList.remove('nav-scrolled');
        }

        lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
    };

    // Navbar shrink function
    var navbarShrink = function () {
        const navbarCollapsible = document.body.querySelector('#mainNav');
        if (!navbarCollapsible) {
            return;
        }
        if (window.scrollY === 0) {
            navbarCollapsible.classList.remove('navbar-shrink')
        } else {
            navbarCollapsible.classList.add('navbar-shrink')
        }

    };

    // Shrink the navbar 
    navbarShrink();
    controlarNavbar();

    // Shrink the navbar when page is scrolled
    document.addEventListener('scroll', navbarShrink);
    window.addEventListener('scroll', controlarNavbar);

    //  Activate Bootstrap scrollspy on the main nav element
    const mainNav = document.body.querySelector('#mainNav');
    if (mainNav) {
        new bootstrap.ScrollSpy(document.body, {
            target: '#mainNav',
            rootMargin: '0px 0px -40%',
        });
    };

    // Collapse responsive navbar when toggler is visible
    const navbarToggler = document.body.querySelector('.navbar-toggler');
    const responsiveNavItems = [].slice.call(
        document.querySelectorAll('#navbarResponsive .nav-link')
    );
    responsiveNavItems.map(function (responsiveNavItem) {
        responsiveNavItem.addEventListener('click', () => {
            if (window.getComputedStyle(navbarToggler).display !== 'none') {
                navbarToggler.click();
            }
        });
    });

});
