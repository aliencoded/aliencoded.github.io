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
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: true,
    timeZone: "America/New_York"
  };

  const dateString = now.toLocaleDateString("en-US", dateOptions);
  const timeString = now.toLocaleTimeString("en-US", timeOptions);

  const dateEl = document.getElementById("today-date");
  const timeEl = document.getElementById("ny-time");

  if (dateEl && timeEl) {
    dateEl.textContent = dateString;
    timeEl.textContent = " | Time: " + timeString + " (New York)";
  }
}

updateNYTime();
setInterval(updateNYTime, 1000);