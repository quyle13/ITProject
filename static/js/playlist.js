$(document).ready(function () {
    $('.add-to-playlist').click(function () {
        var ids = $(this).attr('aria-label');
        $.ajax({
            url: "/ajax/add-to-playlist/" + ids,
        }).error(function (error) {
            alert(error);
        }).done(function (data) {
            alert(data + " - song added to playlist");
        });
    });
});