let time = 120;

let timer = document.getElementById("timer");

let form = document.getElementById("quizForm");

let interval = setInterval(() => {

    time--;

    timer.innerHTML = "Time Left: " + time;

    if(time <= 0){

        clearInterval(interval);

        form.submit();
    }

}, 1000);