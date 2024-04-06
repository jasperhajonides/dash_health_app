
// Animation for changing tabs
if (!window.dash_clientside) {
    window.dash_clientside = {};
}

window.dash_clientside.clientside = {
    trigger_animation: function(trigger) {
        const content = document.getElementById('tabs-content');
        if (content) {
            content.classList.remove('fade-in-content');
            void content.offsetWidth; // Trigger reflow to reset animation
            content.classList.add('fade-in-content');
        }
        return trigger;
    }
}

