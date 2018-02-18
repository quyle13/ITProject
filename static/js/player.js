$(document).ready(function() {

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

	// Get classes
	container = $('.container');
	cover 	  = $('.cover');
	player 	  = $('.player');

	song   = new Audio();
	state  = songState.STOP;
	volume = volumeState.LOUD;

	song.preload = "auto"

	// Get the state of the player save in the cookie --------------------------
	if(typeof Cookies.get('song_state') !== 'undefined') {
		state = Cookies.get('song_state');
	}

	if(typeof Cookies.get('volume_state') !== 'undefined') {
		volume = Cookies.get('volume_state');
	}

	if(typeof Cookies.get('song_src') !== 'undefined') {
		song.src = Cookies.get('song_src');
	}

	if(typeof Cookies.get('volume') !== 'undefined' && volume != volumeState.MUTED) {
		song.volume = Cookies.get('volume');
	}

	if( typeof Cookies.get('song_time') !== 'undefined') {
		song.currentTime = Cookies.get('song_time');
	}
	// -------------------------------------------------------------------------

	// TODO: Set correctly the right song displayed

	if(state == songState.PLAY) {
		song.play();
	}

	$('.btn').click( function(ev) {
		ev.preventDefault();

		// Control if another song need to be played
		if(song.src != $(this).attr("src") || state == songState.STOP) {
			song.type = 'audio/mpeg';
			song.src  = $(this).attr("src");

			state = songState.STOP;
			Cookies.set('song_state', state);
			Cookies.set('song_src', song.src, {expires: 1 });
		}

		// Play/Pause the song and modify the state
		if(state == songState.PLAY) {
			song.pause();
			state = songState.PAUSE;
			Cookies.set('song_state', state, {expires: 1 });
		}
		else {
			song.play();
			state = songState.PLAY;
			Cookies.set('song_state', state, {expires: 1 });
		}
	});

	// $('#stop').click( function(ev) {
	// 	ev.preventDefault();
	//
	// 	song.pause();
	// 	song.currentTime = 0;
	// 	state = songState.STOP;
	// 	Cookies.set('song_state', state, {expires: 1 });
	// });

	//  $('#mute').click( function(ev) {
	// 	ev.preventDefault();
	//
	// 	// Mute/Unmute the song and modify the state
	// 	if(volume == volumeState.MUTED) {
	// 		song.volume = Cookies.get('volume');
	// 		volume = volumeState.LOUD;
	// 		Cookies.set('volume_state', volume, {expires: 1 });
	// 	}
	// 	else {
	// 		Cookies.set('volume', song.volume, {expires: 1 });
	// 		song.volume = 0;
	// 		volume = volumeState.MUTED;
	// 		Cookies.set('volume_state', volume, {expires: 1 });
	// 	}
	// });

	// $("#timeBar").bind("change", function() {
	// 	song.currentTime = $(this).val();
	// 	$(this).attr("max", song.duration);
	// });

	// $("#volumeBar").bind("change", function() {
	// });

	song.addEventListener('timeupdate', function () {
		Cookies.set('song_time', song.currentTime, {expires: 1 });
		$('#timeBar').attr('max',song.duration);
		$("#timeBar").attr('value', parseInt(song.currentTime, 10));
	});

	song.addEventListener('ended', function() {
		this.stop();
		// TODO: Get and Play next song
	}, false);

	song.addEventListener('canplay', function() {});
});
