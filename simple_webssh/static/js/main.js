jQuery(function ($) {
    $('form#connect').submit(function (event) {
        event.preventDefault();

        var form = $(this),
            url = form.attr('action'),
            type = form.attr('method'),
            data = new FormData(this);

        $.ajax({
            url: url,
            type: type,
            data: data,
            success: callback,
            cache: false,
            contentType: false,
            processData: false
        });

    });

    function callback(msg) {
        // console.log(msg);
        if (msg.code !== 0) {
            $('#status').text(msg.msg);
            return;
        }

        var ws_url = window.location.href.replace('http', 'ws').replace("webssh/connection", ""),
            join = (ws_url[ws_url.length - 1] === '/' ? '' : '/'),
            url = ws_url + join + 'webssh/session?token=' + msg.data.token,
            socket = new WebSocket(url),
            terminal = document.getElementById('#terminal'),
            term = new Terminal({cursorBlink: true});

        console.log(url);
        term.on('data', function (data) {
            console.log(data);
            socket.send(data);
        });

        socket.onopen = function (e) {
            $('.container').hide();
            term.open(terminal, true);
        };

        socket.onmessage = function (msg) {
            // console.log(msg);
            term.write(msg.data);
        };

        socket.onerror = function (e) {
            console.log(e);
        };

        socket.onclose = function (e) {
            console.log(e);
            term.destroy();
            $('.container').show();
            $('#status').text(e.reason);
        };
    }
});
