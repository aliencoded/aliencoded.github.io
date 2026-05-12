function updateNYTime() {
  const now = new Date();

  const dateOptions = {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
    timeZone: "America/New_York"
  };

  const timeOptions = {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
    timeZone: "America/New_York"
  };

  const dateString = now.toLocaleDateString("en-US", dateOptions);
  const timeString = now.toLocaleTimeString("en-US", timeOptions);

  const dateEl = document.getElementById("today-date");
  const timeEl = document.getElementById("ny-time");

  if (dateEl) dateEl.textContent = dateString;
  if (timeEl) timeEl.textContent = " · " + timeString + " ET";
}

updateNYTime();
// minute-precision display — no need to tick every second
setInterval(updateNYTime, 30000);
