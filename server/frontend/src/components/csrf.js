export default function csrfToken() {
  const cookie = document.cookie.split("; ").find(value => value.startsWith("csrftoken="));
  return cookie ? decodeURIComponent(cookie.slice("csrftoken=".length)) : "";
}
