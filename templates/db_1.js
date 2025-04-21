// Function to show the selected section and hide others
function showSection(sectionId) {
    // Hide all sections
    const sections = document.querySelectorAll("main");
    sections.forEach(section => {
        section.style.display = "none";
    });

    // Show the selected section
    const selectedSection = document.getElementById(sectionId);
    if (selectedSection) {
        selectedSection.style.display = "block";
    }
}

// Function to handle Create Patient's ID flow
function goToPrescriptionScanner() {
    showSection('prescription-scanner');
}

// Function to handle Existing Patient Login flow
function goToBehaviourAnalysis() {
    showSection('behaviour-analysis');
}

// Function to handle navigation from Behaviour Analysis to Pupil Analysis
function goToPupilAnalysis() {
    showSection('pupil-analysis');
}

// Event listeners for sidebar navigation
document.querySelector("a[href='#create-patient-id']").addEventListener("click", function(event) {
    event.preventDefault();
    showSection('create-patient-id');
});

document.querySelector("a[href='#Existing-ID']").addEventListener("click", function(event) {
    event.preventDefault();
    showSection('Existing-ID');
});

// Event listener for Create Patient's ID form submission
document.querySelector(".next-btn").addEventListener("click", function(event) {
    event.preventDefault();
    goToPrescriptionScanner();
});

// Event listener for Existing Patient Login form submission
document.querySelector("#Existing-ID form").addEventListener("submit", function(event) {
    event.preventDefault();
    goToBehaviourAnalysis();
});

// Event listener for Behaviour Analysis form submission
document.querySelector("#behaviour-analysis .next-btn").addEventListener("click", function(event) {
    event.preventDefault();
    goToPupilAnalysis();
});


function previewFiles() {
    const fileInput = document.getElementById('file-input');
    const previewContainer = document.getElementById('preview-container');
    previewContainer.innerHTML = '';

    Array.from(fileInput.files).forEach(file => {
        const fileReader = new FileReader();
        fileReader.onload = function(e) {
            const fileUrl = e.target.result;
            let element;

            if (file.type.startsWith('image/')) {
                element = document.createElement('img');
                element.src = fileUrl;
            } else if (file.type === 'application/pdf') {
                element = document.createElement('iframe');
                element.src = fileUrl;
            }

            element.onclick = function() {
                openFullscreen(fileUrl, file.type);
            };

            previewContainer.appendChild(element);
        };
        fileReader.readAsDataURL(file);
    });
}

function openFullscreen(url, type) {
    const fullscreenPreview = document.getElementById('fullscreen-preview');
    const fullscreenContent = document.getElementById('fullscreen-content');
    fullscreenContent.innerHTML = '';

    if (type.startsWith('image/')) {
        const img = document.createElement('img');
        img.src = url;
        fullscreenContent.appendChild(img);
    } else if (type === 'application/pdf') {
        const iframe = document.createElement('iframe');
        iframe.src = url;
        fullscreenContent.appendChild(iframe);
    }

    fullscreenPreview.style.display = 'block';
}

function closeFullscreen() {
    const fullscreenPreview = document.getElementById('fullscreen-preview');
    fullscreenPreview.style.display = 'none';
}
// Initial navigation to show the dashboard
navigateToSection('dashboard');
