function startQuizTimer(minutesLimit) {
    let duration = minutesLimit * 60;
    let display = document.getElementById('time');

    let timer = setInterval(function () {
        let minutes = parseInt(duration / 60, 10);
        let seconds = parseInt(duration % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.textContent = minutes + ":" + seconds;

        if (--duration < 0) {
            clearInterval(timer);
            alert(gettext("Hết thời gian! Bài sẽ được nộp."));
            document.querySelector("form").submit();
        }
    }, 1000);
}
