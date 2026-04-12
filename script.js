const chats = [
    [
        { type: "bot", text: "안녕하세요. 무엇을 도와드릴까요?" },
        { type: "user", text: "안녕하세요." },
        { type: "bot", text: "반갑습니다." }
    ],
    [
        { type: "bot", text: "두 번째 대화입니다." },
        { type: "user", text: "사이드바 테스트 중입니다." }
    ],
    [
        { type: "bot", text: "세 번째 대화입니다." }
    ]
];

function loadChat(index) {
    const chatMessages = document.getElementById("chatMessages");
    const chatItems = document.querySelectorAll(".chat-item");

    if (!chatMessages || !chatItems.length) return;

    chatMessages.innerHTML = "";

    chats[index].forEach(msg => {
        const div = document.createElement("div");
        div.classList.add("message", msg.type);
        div.textContent = msg.text;
        chatMessages.appendChild(div);
    });

    chatItems.forEach(item => item.classList.remove("active"));
    if (chatItems[index]) {
        chatItems[index].classList.add("active");
    }
}

window.onload = function () {
    loadChat(0);
};

function toggleSidebar() {
    const appLayout = document.querySelector(".app-layout");
    const sidebar = document.querySelector(".sidebar");

    if (!appLayout || !sidebar) return;

    sidebar.classList.toggle("closed");

    if (sidebar.classList.contains("closed")) {
        appLayout.classList.remove("sidebar-open");
    } else {
        appLayout.classList.add("sidebar-open");
    }
}

function goToStep2() {
    const step1 = document.getElementById("step1");
    const step2 = document.getElementById("step2");
    const progressFill = document.getElementById("progress-fill");

    if (!step1 || !step2 || !progressFill) return;

    step1.classList.remove("active");
    step2.classList.add("active");
    progressFill.style.width = "100%";
}

function goToStep1() {
    const step1 = document.getElementById("step1");
    const step2 = document.getElementById("step2");
    const progressFill = document.getElementById("progress-fill");

    if (!step1 || !step2 || !progressFill) return;

    step2.classList.remove("active");
    step1.classList.add("active");
    progressFill.style.width = "50%";
}