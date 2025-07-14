document.addEventListener('DOMContentLoaded', function () {
    // Desktop Sidebar Toggle
    const sidebar = document.getElementById('sidebar')
    const sidebarToggle = document.getElementById('sidebarToggle')
    const sidebarToggleIcon = document.getElementById('sidebarToggleIcon')

    const toggleSidebar = () => {
        sidebar.classList.toggle('collapsed')
        const isCollapsed = sidebar.classList.contains('collapsed')
        sidebarToggleIcon.classList.toggle('fa-angle-double-right', isCollapsed)
        sidebarToggleIcon.classList.toggle('fa-angle-double-left', !isCollapsed)
        localStorage.setItem('sidebarCollapsed', isCollapsed)
    }

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar)
    }

    if (localStorage.getItem('sidebarCollapsed') === 'true') {
        // To avoid flash of un-collapsed sidebar, apply class directly
        sidebar.classList.add('collapsed')
        if (sidebarToggleIcon) {
            sidebarToggleIcon.classList.add('fa-angle-double-right')
            sidebarToggleIcon.classList.remove('fa-angle-double-left')
        }
    }

    // Mobile Sidebar Toggle
    const mobileToggleBtn = document.createElement('button')
    mobileToggleBtn.className = 'btn btn-primary d-md-none position-fixed'
    mobileToggleBtn.style.cssText = 'top: 10px; left: 10px; z-index: 1001;'
    mobileToggleBtn.innerHTML = '<i class="fas fa-bars"></i>'
    document.body.appendChild(mobileToggleBtn)

    mobileToggleBtn.addEventListener('click', function () {
        sidebar.classList.toggle('active')
    })
})

const Toast = Swal.mixin({
    toast: true,
    position: "top-end",
    showConfirmButton: false,
    timer: 5000,
    timerProgressBar: true,
    didOpen: (toast) => {
        toast.addEventListener("mouseenter", Swal.stopTimer);
        toast.addEventListener("mouseleave", Swal.resumeTimer);
    },
});

// calls the function to display messages
function CalledToast(type, message) {
    Toast.fire({
        icon: type,
        title: message,
    });
}