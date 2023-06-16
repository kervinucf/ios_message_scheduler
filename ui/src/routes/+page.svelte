<script>
    import Countdown from './Countdown.svelte';  // make sure to import the countdown component

    //const BASE_URL = 'https://94ed-2600-1700-cf0-32b0-753e-6811-6568-5dd7.ngrok-free.app/';
    const BASE_URL = 'http://127.0.0.1:5000';

    let messages = [];

    async function updateMessages() {
        const data = await getPendingMessages();
        messages = data;
    }

    export async function getPendingMessages() {
        const response = await fetch(`${BASE_URL}/get_scheduled_messages`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        const data = await response.json();
        return data;
    }

    export async function sendMessage() {
        const phoneNumber = document.getElementById("phoneNumber").value;
        const messageText = document.getElementById("messageText").value;
        const scheduleTime = document.getElementById("scheduleTime").value;

        await fetch(`${BASE_URL}/send_message`, {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                phoneNumber: phoneNumber,
                message: messageText,
                scheduleTime: scheduleTime
            })
        });

        await updateMessages();
    }

    export async function modifyMessage(job_id, new_time, new_message) {
        await fetch(`${BASE_URL}/modify_scheduled_message`, {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                job_id: job_id,
                new_time: new_time,
                new_message: new_message
            })
        });

        await updateMessages();
    }

    export async function deleteMessage(job_id) {
        await fetch(`${BASE_URL}/remove_scheduled_message`, {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                job_id: job_id
            })
        });

        await updateMessages();
    }

    // Get initial messages when page is loaded
    updateMessages();

    $: messages
</script>


<div id="messageView" class="light">
    <h1>iOS Message Scheduler</h1>

    <section>
        <h2>Schedule a Message</h2>
        <input type="text" id="phoneNumber" placeholder="Enter Phone Number">
        <textarea id="messageText" placeholder="Enter your message"></textarea>
        <input type="datetime-local" id="scheduleTime">
        <button id="sendMessage" on:click={sendMessage}>Schedule Message</button>
    </section>

    <section>
        <h2>Scheduled Messages</h2>
        <div style="overflow: scroll">
            {#each messages as message}
                <div class="messageCard">
                    <p>{message.message}</p>
                    <p>{message.phone_number}</p>
                    <Countdown endDate={message.next_run_time}/>
                    <button on:click={() => modifyMessage(message.job_id, 'new-time', 'new-message')}>Modify</button>
                    <button on:click={() => deleteMessage(message.job_id)}>Delete</button>
                </div>
            {/each}
        </div>
        <button id="getPendingMessages"
                on:click={async () => {messages = await getPendingMessages();console.log(messages)}}>Refresh
        </button>
    </section>
</div>


<style>
    :root {
        --light-bg: #ffffff;
        --dark-bg: #1c1c1e;
        --light-text: #000000;
        --dark-text: #ffffff;
        --light-card: #f1f3f4;
        --dark-card: #2c2c2e;
        --light-border: #cfd8dc;
        --dark-border: #464646;
        --blue: #007aff;
    }

    #messageView.light {
        background-color: var(--light-bg);
        color: var(--light-text);
    }

    #messageView.dark {
        background-color: var(--dark-bg);
        color: var(--dark-text);
    }

    #messageView {
        font-family: -apple-system, BlinkMacSystemFont, "San Francisco", Helvetica, Arial, sans-serif;
        max-width: none;
        margin: 0;
        padding: 1rem;
        height: 100vh;
        transition: background-color 0.3s ease, color 0.3s ease;
    }

    #messageView h1, #messageView h2 {
        font-weight: 500;
        text-align: center;
    }

    #messageView input,
    #messageView textarea {
        padding: 0.5rem;
        border: 1px solid var(--light-border);
        border-radius: 5px;
        width: 100%;
        box-sizing: border-box;
        background-color: var(--light-card);
        transition: background-color 0.3s ease, border-color 0.3s ease;
    }

    #messageView.dark input,
    #messageView.dark textarea {
        background-color: var(--dark-card);
        border-color: var(--dark-border);
    }

    #messageView button {
        cursor: pointer;
        padding: 0.5rem 1rem;
        background-color: var(--blue);
        color: var(--light-bg);
        border: none;
        border-radius: 12px;
        font-weight: bold;
        transition: background-color 0.3s ease;
        margin-top: 1rem;
    }

    .messageCard {
        background-color: var(--light-card);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        transition: background-color 0.3s ease;
    }

    #messageView.dark .messageCard {
        background-color: var(--dark-card);
    }

    .messageCard p {
        margin-bottom: 0.5rem;
    }

    .messageCard button {
        padding: 0.25rem 0.5rem;
        margin-right: 0.5rem;
        font-size: 0.9rem;
        border-radius: 10px;
    }
</style>
