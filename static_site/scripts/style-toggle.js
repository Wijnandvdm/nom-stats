// Set the default theme when the document has loaded
document.addEventListener("DOMContentLoaded", function(event){
    document.body.classList.add('dark-mode');
});


function toggleTheme() {
    const body = document.body;
    const toggleButton = document.querySelector('.theme-toggle');

    body.classList.toggle('light-mode');
    body.classList.toggle('dark-mode');

    // Update button icon
    if (body.classList.contains('light-mode')) {
        toggleButton.textContent = '☀️'; // Sun for light mode
        toggleButton.setAttribute('data-tooltip', 'Welcome back to civilization!');
    } else {
        toggleButton.textContent = '🌙'; // Moon for dark mode
        toggleButton.setAttribute('data-tooltip', 'Light mode, really?');
    }
}
