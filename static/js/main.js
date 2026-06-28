// Shared helper used by house.html and award.html to save a visitor's
// name to the MySQL-backed API before moving on to the next beat.
async function postJSON(url, payload) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  let data = null;
  try {
    data = await res.json();
  } catch (e) {
    data = null;
  }
  if (!res.ok || !data || !data.ok) {
    const message = (data && data.error) || "Something went wrong. Please try again.";
    throw new Error(message);
  }
  return data;
}
