const BACKEND_URL = "http://localhost:8001";

// ──────────────────────────────────────────
// Auth
// ──────────────────────────────────────────

async function handleLogin(event) {
    event.preventDefault();
    const username = document.getElementById("login-username").value.trim();
    const password = document.getElementById("login-password").value;

    if (!username || !password) {
        alert("아이디와 비밀번호를 입력해주세요.");
        return;
    }

    try {
        const res = await fetch(`${BACKEND_URL}/api/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password }),
        });
        const data = await res.json();

        if (!res.ok) {
            alert(data.detail || "로그인에 실패했습니다.");
            return;
        }

        if (data.user) {
            sessionStorage.setItem("user_id", data.user.id);
            sessionStorage.setItem("username", data.user.username);
        } else {
            sessionStorage.setItem("username", username);
        }
        location.href = "main.html";
    } catch (e) {
        alert("서버에 연결할 수 없습니다. 백엔드가 실행 중인지 확인해주세요.");
    }
}

async function handleSignup() {
    const username = document.getElementById("signup-username").value.trim();
    const email    = document.getElementById("signup-email").value.trim();
    const password = document.getElementById("signup-password").value;
    const confirm  = document.getElementById("signup-password-confirm").value;

    if (!username || !email || !password) {
        alert("모든 필드를 입력해주세요.");
        return;
    }
    if (password !== confirm) {
        alert("비밀번호가 일치하지 않습니다.");
        return;
    }

    try {
        const res = await fetch(`${BACKEND_URL}/api/auth/signup`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, password }),
        });
        const data = await res.json();

        if (!res.ok) {
            alert(data.detail || "회원가입에 실패했습니다.");
            return;
        }

        alert("회원가입이 완료되었습니다!");
        location.href = "login.html";
    } catch (e) {
        alert("서버에 연결할 수 없습니다. 백엔드가 실행 중인지 확인해주세요.");
    }
}

// ──────────────────────────────────────────
// Chat
// ──────────────────────────────────────────

function appendMessage(type, text) {
    const chatMessages = document.getElementById("chatMessages");
    if (!chatMessages) return;
    const div = document.createElement("div");
    div.classList.add("message", type);
    div.textContent = text;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage() {
    const input  = document.getElementById("chatInput");
    const sendBtn = document.getElementById("sendBtn");
    if (!input) return;

    const message = input.value.trim();
    if (!message) return;

    appendMessage("user", message);
    input.value = "";
    sendBtn.disabled = true;

    const userId = sessionStorage.getItem("user_id");

    try {
        const res = await fetch(`${BACKEND_URL}/api/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message,
                user_id: userId ? parseInt(userId) : null,
            }),
        });
        const data = await res.json();

        if (!res.ok) {
            appendMessage("bot", `오류: ${data.detail || "요청 실패"}`);
        } else {
            appendMessage("bot", data.reply);
        }
    } catch (e) {
        appendMessage("bot", "서버에 연결할 수 없습니다. 백엔드가 실행 중인지 확인해주세요.");
    } finally {
        sendBtn.disabled = false;
        input.focus();
    }
}

// Enter 키로 전송
document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("chatInput");
    if (input) {
        input.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) sendMessage();
        });
    }
});

// ──────────────────────────────────────────
// Sidebar
// ──────────────────────────────────────────

function toggleSidebar() {
    const appLayout = document.querySelector(".app-layout");
    const sidebar   = document.querySelector(".sidebar");
    if (!appLayout || !sidebar) return;

    sidebar.classList.toggle("closed");
    appLayout.classList.toggle("sidebar-open", !sidebar.classList.contains("closed"));
}

// ──────────────────────────────────────────
// Signup step navigation (signup.html 인라인 스크립트 대체)
// ──────────────────────────────────────────

function goToStep2() {
    const step1       = document.getElementById("step1");
    const step2       = document.getElementById("step2");
    const progressFill = document.getElementById("progress-fill");
    if (!step1 || !step2 || !progressFill) return;

    step1.classList.remove("active");
    step2.classList.add("active");
    progressFill.style.width = "100%";
}

function goToStep1() {
    const step1       = document.getElementById("step1");
    const step2       = document.getElementById("step2");
    const progressFill = document.getElementById("progress-fill");
    if (!step1 || !step2 || !progressFill) return;

    step2.classList.remove("active");
    step1.classList.add("active");
    progressFill.style.width = "50%";
}

// ──────────────────────────────────────────
// main.html 초기화
// ──────────────────────────────────────────

window.onload = function () {
    const username = sessionStorage.getItem("username");
    const usernameEl = document.querySelector(".username");
    if (usernameEl && username) usernameEl.textContent = username;
};
