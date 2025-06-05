document.getElementById('playlistForm').addEventListener('submit', function(event) {
    event.preventDefault(); // 기본 폼 제출 방지

    const playlistUrl = document.getElementById('playlistUrl').value;
    console.log('입력된 플레이리스트 링크:', playlistUrl);

    function animatePercentage(element, targetPercent) {
    let current = parseInt(element.getAttribute('data-percent')) || 0;
    targetPercent = Math.min(100, targetPercent); // 최대 100%

    function step() {
        if (current < targetPercent) {
            current += 1;
            element.setAttribute('data-percent', current);
            element.textContent = `${current}%`;
            requestAnimationFrame(step);
        } else {
            element.setAttribute('data-percent', targetPercent);
            element.textContent = `${targetPercent}%`;
        }
    }

    if (current < targetPercent) {
        step();
    } else {
        // 감소 상황도 처리
        element.setAttribute('data-percent', targetPercent);
        element.textContent = `${targetPercent}%`;
    }
}



    function showError(message) {
        const errorElement = document.getElementById('result');
        errorElement.innerHTML = `<p id="error" style="color: red;">${message}</p>`;
        errorElement.style.animation = 'fadeIn 0.5s ease-in-out';
    }

    const spotifyUrlRegex = /^https?:\/\/(?:open\.)?spotify\.com\/(playlist|album)\/([a-zA-Z0-9]+)(?:\?.*)?$/;

    if (!spotifyUrlRegex.test(playlistUrl)) {
        showError('올바른 Spotify 플레이리스트 또는 앨범 URL을 입력하세요.');
        return;
    }

    const button = document.querySelector('button[type="submit"]');
    button.disabled = true;
    button.textContent = '처리 중...';
    document.getElementById('result').innerHTML = '<span style="color:#1DB954;">잠시만 기다려주세요...</span>';
    console.log("fetch")
    fetch("/fetch-playlist", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                url: playlistUrl
            }),
        })
        .then(response => response.json())
        .then(data => {
            const task_id = data.task_id;
            console.log("Task ID:", task_id);

            const protocol = window.location.protocol === "https:" ? "wss" : "ws";
            const ws = new WebSocket(`${protocol}://${window.location.host}/ws/progress/${task_id}`);
            console.log(`ws://${window.location.host}/ws/progress/${task_id}`)

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                console.log("WebSocket 메시지 수신:", data);

                if (data.type === "ping") return;

                if (data.type === "status") {
                    document.getElementById('result').innerHTML = `<p>${data.message}</p>`;
                }

                if (data.type === "downloaded" || data.type === "completed") {
                    if (!document.getElementById('downloadBar')) {
                        document.getElementById('result').innerHTML = `
                        <div class="progress-wrapper">
                            <div class="progress-label">다운로드 진행률</div>
                            <div class="progress-bar">
                                <div id="downloadBar"data-percent="0"></div>
                            </div>
                            <div class="progress-label">처리 진행률</div>
                            <div class="progress-bar">
                                <div id="completeBar" data-percent="0"></div>
                            </div>
                        </div>`;
                }}

                if (data.type === "downloaded") {
                    const percent = Math.round((data.count / data.total) * 100);
                    const downloadBar = document.getElementById('downloadBar');
                    downloadBar.style.width = `${percent}%`;
                    animatePercentage(downloadBar, percent);
                }

                if (data.type === "completed") {
                    const percent = Math.round((data.count / data.total) * 100);
                    const completeBar = document.getElementById('completeBar');
                    completeBar.style.width = `${percent}%`;
                    animatePercentage(completeBar, percent);
                }

                if (data.type === "success") {
                    ws.close();
                    button.disabled = false;
                    button.textContent = '완료';
                    document.getElementById('result').innerHTML = `<p style="color: green;">다운로드 완료! <a href="${data.download_url}" download="${data.pl_name}.zip">다운로드</a></p>`;
                }
            }
        })
});