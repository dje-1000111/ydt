var tag = document.createElement('script');
tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
var player;

function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
        height: '95%',
        width: '95%',
        videoId: vid,
        playerVars: {
            'controls': 0,
            'showinfo': 1,
            'autohide': 1,
            'playsinline': 1,
            'start': ts[lineNb], //Number((ts[lineNb] / 4.321).toFixed(2))
        },
        events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange
        }
    });
}


function onPlayerReady(event) {
    event.target.playVideo();
}

var paused = true
var done = false;

function onPlayerStateChange(event) {
    if (event.data == YT.PlayerState.PLAYING && !done) {
        replay.innerHTML = "Stop"
        timeout = setTimeout(stopVideo, timeouts[lineNb]);
        done = true;
        paused = false
    }
    if (event.data == YT.PlayerState.PAUSED && !done) {
        replay.innerHTML = "Play"
        done = false;
        paused = true
    }
}

function stopVideo() {
    if (player) {
        player.pauseVideo();

        done = false;
    }
}
