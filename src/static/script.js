document.getElementById('playlistForm').addEventListener('submit', async function(event) {
    event.preventDefault(); // 기본 폼 제출 방지

    const playlistUrl = document.getElementById('playlistUrl').value;
    console.log('입력된 플레이리스트 링크:', playlistUrl);

    // Spotify 플레이리스트 URL 검증 로직 추가

    // 공통 함수: 에러 메시지 표시
    function showError(message) {
        const errorElement = document.getElementById('result');
        errorElement.innerHTML = `<p id="error" style="color: red;">${message}</p>`;
        errorElement.style.animation = 'fadeIn 0.5s ease-in-out';
    }

    // 기존 이벤트 리스너 내부에 URL 검증 추가
    const spotifyUrlRegex = /^https?:\/\/(?:open\.)?spotify\.com\/(playlist|album)\/([a-zA-Z0-9]+)(?:\?.*)?$/;

    if (!spotifyUrlRegex.test(playlistUrl)) {
        showError('올바른 Spotify 플레이리스트 또는 앨범 URL을 입력하세요.');
        return;
    }


    // 백엔드로 POST 요청 보내기
    try {
        // 버튼 비활성화 및 로딩 메시지 표시
        const button = document.querySelector('button[type="submit"]');
        button.disabled = true;
        button.textContent = '처리 중...';
        document.getElementById('result').innerHTML = '<span style="color:#1DB954;">잠시만 기다려주세요...</span>';

        const response = await fetch('/fetch-playlist', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: playlistUrl }),
        });

        // 백엔드 요청 실패 시 에러 처리
        if (!response.ok) {
            showError('다운로드 실패!');
            return;
        }

        const data = await response.json();

        // 백엔드 응답 처리 로직 업데이트
        if (data.success) {
            // 파일 크기를 MB 단위로 변환
            const fileSizeInMB = (data.file_size / (1024 * 1024)).toFixed(2);
            document.getElementById('result').innerHTML = `<a href="${data.download_url}" download>플레이리스트 다운로드</a> (${fileSizeInMB} MB)`;
            document.getElementById('result').style.animation = 'fadeIn 0.5s ease-in-out';
        } else {
            showError(`${data.message}`);
        }
    } catch (error) {
        // 네트워크 오류 시 에러 처리
        console.error('Network Error:', error);
        showError('네트워크 오류가 발생했습니다. 인터넷 연결을 확인하세요.');
    } finally {
        // 백엔드 응답 처리 후 버튼 복구
        const button = document.querySelector('button[type="submit"]');
        button.disabled = false;
        button.textContent = '다운로드';
    }
});
