// Auto logout after 10 minutes of inactivity
let inactivityTime = function () {
    let time;
    window.onload = resetTimer;
    document.onmousemove = resetTimer;
    document.onkeypress = resetTimer;

    function logout() {
        // Only logout if user is logged in
        if (document.querySelector('.navbar-text')) {
            alert('Session expired due to inactivity. Please login again.');
            window.location.href = '/logout';
        }
    }

    function resetTimer() {
        clearTimeout(time);
        time = setTimeout(logout, 600000); // 10 minutes
    }
};

inactivityTime();

// Display current date and time
function updateDateTime() {
    const now = new Date();
    const dateTimeString = now.toLocaleString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    const datetimeElement = document.getElementById('current-datetime');
    if (datetimeElement) {
        datetimeElement.textContent = dateTimeString;
    }
}

// Update datetime every second
setInterval(updateDateTime, 1000);
updateDateTime();
