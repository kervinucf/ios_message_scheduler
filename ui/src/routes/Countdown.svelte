<script>
  export let endDate;

  let diff, days, hours, minutes, seconds;

  const updateTimer = () => {
    diff = new Date(endDate) - new Date();

    if (diff <= 0) {
      clearInterval(interval);
      diff = days = hours = minutes = seconds = 0;
    } else {
      seconds = Math.floor((diff / 1000) % 60);
      minutes = Math.floor((diff / 1000 / 60) % 60);
      hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
      days = Math.floor(diff / (1000 * 60 * 60 * 24));
    }
  };

  const interval = setInterval(() => {
    updateTimer();
    $: diff, days, hours, minutes, seconds
  }, 1000);

  updateTimer();
</script>

<p>{days} days, {hours} hours, {minutes} minutes, {seconds} seconds remaining</p>
