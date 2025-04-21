document.addEventListener('DOMContentLoaded', function () {
    // Internal navigation (Behaviour Analysis)
    const behaviourLink = document.querySelector('a[href="#behaviour-analysis"]');
    const behaviourSection = document.querySelector('#behaviour-analysis');

    // External navigation (CreateID, Prescription, Pupil)
    const externalLinks = document.querySelectorAll('a[href^="createID.html"], a[href^="prescription.html"], a[href^="pupil.html"]');

    // Hide Behaviour Analysis section initially
    behaviourSection.style.display = 'none';

    // Internal Navigation: Show Behaviour Analysis section
    behaviourLink.addEventListener('click', function (e) {
        e.preventDefault();  // Prevent default anchor behavior

        // Hide other main sections
        const allSections = document.querySelectorAll('main');
        allSections.forEach(section => section.style.display = 'none');

        // Show Behaviour Analysis section
        behaviourSection.style.display = 'block';
    });

    // External Navigation: No need to add event listener here for default behavior
    externalLinks.forEach(link => {
        link.addEventListener('click', function () {
            window.location.href = this.href;  // Navigate to external page
        });
    });
});