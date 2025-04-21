document.addEventListener('DOMContentLoaded', function () {

    // Get references to all sections
    const reportUploadSection = document.getElementById('Report-Upload');
    const selfAnalysisSection = document.getElementById('Self-Analysis');

    // Initially hide both sections
    hideSection(reportUploadSection);
    hideSection(selfAnalysisSection);

    // Get the sidebar menu items
    const reportUploadLink = document.querySelector('a[href="#Report-Upload-id"]');
    const selfAnalysisLink = document.querySelector('a[href="#Self-Analysis-id"]');

    // References for blood and urine forms
    const bloodTestForm = document.getElementById('blood-test-form');
    const urineTestForm = document.getElementById('urine-test-form');
    const nextBloodButton = document.getElementById('next-blood');

    // Initially hide the urine test form
    urineTestForm.style.display = 'none';

    // Function to hide sections
    function hideSection(section) {
        section.classList.remove('show');
        setTimeout(() => {
            section.style.display = 'none';
        }, 500);
    }

    // Function to show sections
    function showSection(section) {
        section.style.display = 'block';
        setTimeout(() => {
            section.classList.add('show');
        }, 10);
    }

    // Function to show the blood report form first, then urine test form after clicking "Next"
    function showReportUpload() {
        hideSection(selfAnalysisSection); // Hide self analysis section
        showSection(reportUploadSection); // Show the report upload section
        
        // Initially show the blood test form and hide the urine test form
        bloodTestForm.style.display = 'block';
        urineTestForm.style.display = 'none';

        // Handle the "Next" button click for the blood test form
        nextBloodButton.addEventListener('click', function () {
            // Hide blood test form and show urine test form
            bloodTestForm.style.display = 'none';
            urineTestForm.style.display = 'block';
        });
    }

    // Function to show the self analysis form
    function showSelfAnalysis() {
        hideSection(reportUploadSection); // Hide report upload section
        showSection(selfAnalysisSection); // Show self analysis section
    }

    // Add event listeners to sidebar links
    reportUploadLink.addEventListener('click', function (e) {
        e.preventDefault(); // Prevent the default anchor action
        showReportUpload();
    });

    selfAnalysisLink.addEventListener('click', function (e) {
        e.preventDefault(); // Prevent the default anchor action
        showSelfAnalysis();
    });

});
