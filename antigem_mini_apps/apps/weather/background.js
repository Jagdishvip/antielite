// Runs with Sky closed (AntiElite background task): every hour, warn when rain is likely in the next 3 hours.
AntiElite.background.on('rain-check', async (task) => {
  await import('/shared.js'); // defines globalThis.Sky (weather codes, forecast URL)
  const cities = AntiElite.storage.get('cities', []);
  if (!cities.length || AntiElite.storage.get('rainAlerts', true) === false) return;
  const city = cities[0];
  const data = await (await fetch(Sky.url(city, AntiElite.storage.get('units', 'metric')))).json();
  localStorage.setItem('cache:' + city.id, JSON.stringify({ at: Date.now(), data }));
  const p = Sky.rainSoon(data, 3);
  AntiElite.storage.set('lastCheck', { at: Date.now(), city: city.name, rain: p, reason: task.reason });
  if (p >= 60) {
    await AntiElite.notify.show({ title: `☔ Rain likely in ${city.name}`, body: `${p}% chance of rain in the next 3 hours. Take an umbrella.`, tag: 'rain' });
  }
});
