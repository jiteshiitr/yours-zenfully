$(document).ready(function() {
    var mediaRecorder;
    var audioChunks = [];
    var isRecording = false;

    function toggleRecording() {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    }

    function startRecording() {
        audioChunks = [];
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(function(stream) {
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start();
                $('#record-button').addClass('recording').html('<i class="fas fa-stop"></i> Stop');
                $('.progress-container').addClass('active');

                mediaRecorder.ondataavailable = function(e) {
                    audioChunks.push(e.data);
                };

                mediaRecorder.onstop = function() {
                    var audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    transcribeAudio(audioBlob);
                };

                isRecording = true;
            });
    }

    function stopRecording() {
        mediaRecorder.stop();
        $('#record-button').removeClass('recording').html('<i class="fas fa-microphone"></i> Speak');
        $('.progress-container').removeClass('active');
        isRecording = false;
    }

    function transcribeAudio(audioBlob) {
        var formData = new FormData();
        formData.append('audio', audioBlob, 'audio.wav');
        $.ajax({
            url: '/transcribe',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.status === 'success') {
                    sendMessage(response.transcript);
                } else {
                    displayMessage(response.message, 'bot');
                    speak(response.message);
                }
            }
        });
    }

    function sendMessage(message) {
        displayMessage(message, 'user');
        $.ajax({
            url: '/chat',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'message': message }),
            success: function(response) {
                displayMessage(response.message, 'bot');
                speak(response.message);
            }
        });
    }

    function displayMessage(message, sender) {
        var chatBody = $('.chat-body');
        var messageElement = $('<div>').addClass('message ' + sender);
        var messageContent = $('<div>').addClass('message-content').text(message);
        messageElement.append(messageContent);
        chatBody.append(messageElement);

        chatBody.scrollTop(chatBody[0].scrollHeight);
    }

    function speak(text) {
        var msg = new SpeechSynthesisUtterance();
        msg.text = text;
        msg.lang = 'en-US';
        msg.rate = 0.9; // Slightly slower rate for more natural speech
        msg.pitch = 1.1; // Slightly higher pitch for a more engaging tone
        msg.volume = 1; // Full volume

        // Selecting a more human-like voice, if available
        var voices = window.speechSynthesis.getVoices();
        for(var i = 0; i < voices.length; i++) {
            if(voices[i].name === 'Google UK English Female' || voices[i].name === 'Google US English') {
                msg.voice = voices[i];
                break;
            }
        }

        window.speechSynthesis.speak(msg);
    }

    $('#record-button').on('click', toggleRecording);
});
