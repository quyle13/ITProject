/* Global element */
var songState =
{
  PLAY:  1,
  PAUSE: 2,
  STOP:  3,
};

var volumeState =
{
  MUTE: 1,
  LOUD: 2,
};

song   = new Audio();
state  = songState.STOP;
volume = volumeState.LOUD;
song.preload = "auto";

var player = 'undefined'

/*
* This function update the time, volume and source of the music by accessing to
* the cookies which contain the different value
*/
var updateData = function()
{
	// Get the state of the player save in the cookie
	if(typeof Cookies.get('song_state') !== 'undefined') {
		state = Cookies.get('song_state');
	}

	if(typeof Cookies.get('volume_state') !== 'undefined') {
		volume = Cookies.get('volume_state');
	}

	if(typeof Cookies.get('song_src') !== 'undefined') {
		song.src = Cookies.get('song_src');
	}

	if(typeof Cookies.get('volume') !== 'undefined' && volume != volumeState.MUTE) {
		song.volume = Cookies.get('volume');
	}
	else if(volume == volumeState.MUTE) {
		song.volume = 0;
	}

	if( typeof Cookies.get('song_time') !== 'undefined') {
		song.currentTime = Cookies.get('song_time');
	}

	// Get the current element that is binded to the music
	var playerList = document.querySelectorAll('button[id^="player-"]');
	for (i = 0; i < playerList.length; i++) {
        if(playerList[i].getAttribute('src') == song.src) {
            player = playerList[i];
		}
	}

	// Start the music if already started and update the button shape
	if(state == songState.PLAY && typeof player !== 'undefined') {
		song.play();
		player.innerHTML = '<i class="fa fa-pause-circle" title="Pause song"></i>';
		$('#header-player').html('<i class="fa fa-pause-circle" title="Pause song"></i>');
	}
	else if(typeof player !== 'undefined') {
		player.innerHTML = '<i class="fa fa-play-circle-o" title="Play song"></i>';
		$('#header-player').html('<i class="fa fa-play-circle-o" title="Play song"></i>');
	}

	// Get the current element that indicates if the song is muted
	var muteList = document.querySelectorAll("#mute");
	for (i = 0; i < muteList.length; i++) {
		if(muteList[i].src = song.src) {
			var mute = muteList[i];
		}
	}

	// Change the button to indicate correctly if the song is muted/unmuted
	if(volume == volumeState.MUTE && typeof mute !== 'undefined') {
		mute.innerHTML = '<i class="fa fa-volume-off" title="Mute"></i>';
	}
	else if(typeof mute !== 'undefined') {
		mute.innerHTML = '<i class="fa fa-volume-up" title="Unmute"></i>';
	}
};

/*
*  Called when the page is showed, when back/forwards button clicked as well.
*  Update the different element, current time, song played, state of the button
*  to stay consistant between pages.
*/
$(window).bind("pageshow", function() {updateData();});

/*
*  Manage the different actions regarding the play button and save the diffrent
*  State of the song.
*/
$(document).ready(function() {

	// updateData();

	$('#header-player').click( function(ev) {
		ev.preventDefault();

		// Play/Pause the song and modify the state
		if(state == songState.PLAY) {
			song.pause();
			state = songState.PAUSE;
			Cookies.set('song_state', state, {expires: 1 });

			$(this).html('<i class="fa fa-play-circle-o" title="Play song"></i>');
			player.innerHTML = '<i class="fa fa-play-circle-o" title="Play song"></i>';

            console.log("Stop Playing song: " + player.getAttribute('src'));
		}
		else {
			song.play();
			state = songState.PLAY;
			Cookies.set('song_state', state, {expires: 1 });

			$(this).html('<i class="fa fa-pause-circle" title="Pause song"></i>');
			player.innerHTML = '<i class="fa fa-pause-circle" title="Pause song"></i>';

            console.log("Start Playing song: " + player.getAttribute('src'));
		}
	});

	$('button[id^="player-"]').click( function(ev) {
		ev.preventDefault();

		// Control if another song need to be played
		if(song.src != $(this).attr("src") || state == songState.STOP) {
			song.type = 'audio/mpeg';
			song.src  = $(this).attr("src");

			state = songState.STOP;
			Cookies.set('song_state', state);
			Cookies.set('song_src', song.src, {expires: 1 });

            $('button[id^="player-"]').html('<i class="fa fa-play-circle-o" title="Play song"></i>');

            player = $(this)[0];

            console.log("New song selected: " + song.src);
		}

		// Play/Pause the song and modify the state
		if(state == songState.PLAY) {
			song.pause();
			state = songState.PAUSE;
			Cookies.set('song_state', state, {expires: 1 });

			$(this).html('<i class="fa fa-play-circle-o" title="Play song"></i>');
			$('#header-player').html('<i class="fa fa-play-circle-o" title="Play song"></i>');

            console.log("Stop Playing song: " + song.src);
		}
		else {
			song.play();
			state = songState.PLAY;
			Cookies.set('song_state', state, {expires: 1 });

			$(this).html('<i class="fa fa-pause-circle" title="Pause song"></i>');
			$('#header-player').html('<i class="fa fa-pause-circle" title="Pause song"></i>');

            console.log("Start Playing song: " + song.src);
		}
	});

	 $('button[id^="mute-"]').click( function(ev) {
		ev.preventDefault();

		// Mute/Unmute the song and modify the state
		if(volume == volumeState.MUTE) {
			song.volume = Cookies.get('volume');
			volume = volumeState.LOUD;
			Cookies.set('volume_state', volume, {expires: 1 });
			$('button[id^="mute-"]').html('<i class="fa fa-volume-up" title="Unmute"></i>');
		}
		else {
			Cookies.set('volume', song.volume, {expires: 1 });
			song.volume = 0;
			volume = volumeState.MUTE;
			Cookies.set('volume_state', volume, {expires: 1 });
			$('button[id^="mute-"]').html('<i class="fa fa-volume-off" title="Mute"></i>');
		}
	});

	// $("#timeBar").bind("change", function() {
	// 	song.currentTime = $(this).val();
	// 	$(this).attr("max", song.duration);
	// });

	// $("#volumeBar").bind("change", function() {
	// });

	// Called when the song's time has changed
	song.addEventListener('timeupdate', function () {
		Cookies.set('song_time', song.currentTime, {expires: 1 });
		// $('#timeBar').attr('max',song.duration);
		// $("#timeBar").attr('value', parseInt(song.currentTime, 10));
	});

	// Called when the song has ended
	song.addEventListener('ended', function() {
		$('#header-player').html('<i class="fa fa-play-circle-o" title="Play song"></i>');
		player.innerHTML = '<i class="fa fa-play-circle-o" title="Play song"></i>';

		state = songState.STOP;
		Cookies.set('song_state', state, {expires: 1 });

        console.log("End of the song: " + player.getAttribute('src'));

		// TODO: Get and Play next song and change player object

        src = player.getAttribute('src');
        console.log(src);

        url = document.URL.substring(document.URL.search("view"));
        url = url.split("/");
        if(url[1] == "artist") {
            page = "artist";
        }
        else if(url[1] == "album") {
            page = "album";
        }
        else if(url[1] == "song") {
            page = "song";
        }
        else {
            page = "other";
        }

        $.get('/next-song/', {currentSrc: src, currentPage: page}, function(data){
            slug =  data.split(" ")[1];
            newSrc = data.split(" ")[0];

            song.src = newSrc;
            Cookies.set('song_src', song.src, {expires: 1 });
            song.play();

            player = $('#player-' + slug)[0];

            state = songState.PLAY;
            Cookies.set('song_state', state, {expires: 1 });

            $('#header-player').html('<i class="fa fa-pause-circle" title="Pause song"></i>');
            player.innerHTML = '<i class="fa fa-pause-circle" title="Pause song"></i>';

            console.log("Start Playing song: " + player.getAttribute('src'));
        });

	}, false);

	song.addEventListener('canplay', function() {});
});
