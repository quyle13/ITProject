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

	if(typeof Cookies.get('volume') !== 'undefined' && volume !== volumeState.MUTED) {
		song.volume = Cookies.get('volume');
	}

	if( typeof Cookies.get('song_time') !== 'undefined') {
		song.currentTime = Cookies.get('song_time');
	}

	// Get the current element that is binded to the music
	var playerList = document.querySelectorAll("#player");
	for (i = 0; i < playerList.length; i++) {
		if(playerList[i].src = song.src) {
			var player = playerList[i];
		}
	}

	// Start the music if already started and update the button shape
	if(state == songState.PLAY && typeof player !== 'undefined') {
		song.play();
		player.innerHTML = '<i class="fa fa-pause-circle" title="Pause song"></i>';
	}
	else if(typeof player !== 'undefined') {
		player.innerHTML = '<i class="fa fa-play-circle-o" title="Play song"></i>';
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

	$('#player').click( function(ev) {
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
			$(this).html('<i class="fa fa-play-circle-o" title="Play song"></i>');
		}
		else {
			song.play();
			state = songState.PLAY;
			Cookies.set('song_state', state, {expires: 1 });
			$(this).html('<i class="fa fa-pause-circle" title="Pause song"></i>');
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

	// Called when the song's time has changed
	song.addEventListener('timeupdate', function () {
		Cookies.set('song_time', song.currentTime, {expires: 1 });
		$('#timeBar').attr('max',song.duration);
		$("#timeBar").attr('value', parseInt(song.currentTime, 10));
	});

	// Called when the song has ended
	song.addEventListener('ended', function() {
		this.stop();
		// TODO: Get and Play next song
	}, false);

	song.addEventListener('canplay', function() {});
});