const input_message = document.querySelector('.chat-message-input');
const message_body = document.querySelector('.left-middle-cont');
const send_message_form = document.querySelector('#chat-message-submit');
// const USER_ID = document.querySelector('#logged-in-user').value;

let loc = window.location;
let wsStart = 'ws://';

if (loc.protocol === 'https') {
    wsStart = 'wss://'
}
let endpoint = wsStart + loc.host + loc.pathname

var socket = new WebSocket(endpoint)

socket.onopen = async function (e) {
    console.log('open', e)
    send_message_form.onclick =  function (e) {
        e.preventDefault()
        console.log('click')
        let message = input_message.value;
        let data = {
            'message': message
        }
        data = JSON.stringify(data)
        socket.send(data)
        console.log($(this)[0])
        $(this)[0].reset()
    }
    
}
socket.onerror = async function (e) {
    console.log('error', e)

}
socket.onmessage = async function (e) {
    console.log('message', e)

}
socket.onclose = async function (e) {
    console.log('close', e)

}


function newMessage(message){
    if ($.trim(message) === '' ){
        return false;
    }
    let message_element = `
    <div class="right-main-messege">
        <span>${message}</span>
    </div>
    `
    message_body.append($(message_element))
    message_body.animate({
        scrollTop: $(document).height()
    }, 100);
    input_message.val(null);
    
}
