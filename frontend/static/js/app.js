/* =========================================================
   DR. URCW AI - FRONTEND CONTROLLER
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       SIDEBAR COLLAPSE
    ====================================================== */

    const sidebarToggle = document.querySelector(".sidebar-toggle");
    const sidebar = document.querySelector(".sidebar");

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener("click", () => {
            sidebar.classList.toggle("collapsed");
        });
    }


    /* =====================================================
       PROFILE DROPDOWN
    ====================================================== */

    const profileTrigger = document.querySelector(".profile-trigger");
    const profileDropdown = document.querySelector(".profile-dropdown");

    if (profileTrigger && profileDropdown) {
        profileTrigger.addEventListener("click", (e) => {
            e.stopPropagation();
            profileDropdown.classList.toggle("show");
        });

        document.addEventListener("click", () => {
            profileDropdown.classList.remove("show");
        });
    }


    /* =====================================================
       CHAT SEND MESSAGE (AJAX)
    ====================================================== */

    const chatForm = document.querySelector("#chat-form");
    const chatInput = document.querySelector("#chat-input");
    const chatMessages = document.querySelector(".chat-messages");

    if (chatForm) {

        chatForm.addEventListener("submit", async function (e) {
            e.preventDefault();

            const message = chatInput.value.trim();
            if (!message) return;

            appendMessage("user", message);
            chatInput.value = "";
            scrollChatBottom();

            try {
                const response = await fetch("/chat", {
                    method: "POST",
                    body: new URLSearchParams({ message })
                });

                const data = await response.json();

                appendMessage("bot", data.reply);
                scrollChatBottom();

            } catch (error) {
                appendMessage("bot", "Something went wrong. Please try again.");
            }
        });
    }


    /* =====================================================
       APPEND CHAT MESSAGE
    ====================================================== */

    function appendMessage(sender, content) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", sender);
        messageDiv.innerHTML = content;
        chatMessages.appendChild(messageDiv);
    }

    function scrollChatBottom() {
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }


    /* =====================================================
       RENAME CHAT SESSION
    ====================================================== */

    document.querySelectorAll(".rename-session").forEach(button => {
        button.addEventListener("click", function () {
            const sessionId = this.dataset.id;
            const newTitle = prompt("Enter new chat name:");

            if (!newTitle) return;

            fetch("/rename-session", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: `session_id=${sessionId}&new_title=${encodeURIComponent(newTitle)}`
            }).then(() => location.reload());
        });
    });


    /* =====================================================
       DELETE CHAT SESSION
    ====================================================== */

    document.querySelectorAll(".delete-session").forEach(button => {
        button.addEventListener("click", function () {
            const sessionId = this.dataset.id;

            if (!confirm("Are you sure you want to delete this chat?")) return;

            fetch("/delete-session", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: `session_id=${sessionId}`
            }).then(() => location.reload());
        });
    });


    /* =====================================================
       MODAL CONTROL
    ====================================================== */

    document.querySelectorAll("[data-open-modal]").forEach(button => {
        button.addEventListener("click", function () {
            const target = document.querySelector(this.dataset.openModal);
            if (target) target.classList.add("show");
        });
    });

    document.querySelectorAll("[data-close-modal]").forEach(button => {
        button.addEventListener("click", function () {
            this.closest(".modal").classList.remove("show");
        });
    });


    /* =====================================================
       ADMIN STUDENT DETAIL PANEL
    ====================================================== */

    document.querySelectorAll(".student-item").forEach(item => {
        item.addEventListener("click", function () {
            const detailPanel = document.querySelector(".student-detail-panel");
            if (!detailPanel) return;

            document.querySelectorAll(".student-item").forEach(i => i.classList.remove("active"));
            this.classList.add("active");

            detailPanel.classList.add("show");
            detailPanel.innerHTML = this.dataset.details;
        });
    });


    /* =====================================================
       NOTIFICATION MARK READ (READY)
    ====================================================== */

    document.querySelectorAll(".mark-read").forEach(btn => {
        btn.addEventListener("click", function () {
            const notificationId = this.dataset.id;

            fetch(`/notification/read/${notificationId}`, {
                method: "POST"
            }).then(() => location.reload());
        });
    });


    /* =====================================================
       AUTO ACTIVE SIDEBAR LINK
    ====================================================== */

    const currentPath = window.location.pathname;
    document.querySelectorAll(".sidebar a").forEach(link => {
        if (link.getAttribute("href") === currentPath) {
            link.classList.add("active");
        }
    });

});