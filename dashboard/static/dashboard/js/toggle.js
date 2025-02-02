document.addEventListener("DOMContentLoaded", function() {
    // Select all toggle buttons
    const toggleButtons = document.querySelectorAll(".toggle-btn");

    toggleButtons.forEach(button => {
        button.addEventListener("click", function() {
            // Get the target element ID from data-target
            const targetId = this.getAttribute("data-target");
            const targetElement = document.getElementById(targetId);

            // Toggle visibility
            if (targetElement) {
                if (targetElement.style.display === "none") {
                    targetElement.style.display = "block"; // Show the block
                } else {
                    targetElement.style.display = "none"; // Hide the block
                }
            }
        });
    });
});
