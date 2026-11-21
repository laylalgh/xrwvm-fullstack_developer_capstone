import React, { useState } from "react";
import Header from "../Header/Header";
import csrfToken from "../csrf";
import "./Register.css";

const fields = [
  ["userName", "Username", "text", "username"],
  ["firstName", "First Name", "text", "given-name"],
  ["lastName", "Last Name", "text", "family-name"],
  ["email", "Email", "email", "email"],
  ["password", "Password", "password", "new-password"],
];

export default function Register() {
  const [message, setMessage] = useState("");
  const [pending, setPending] = useState(false);

  async function register(event) {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.currentTarget));
    setPending(true);
    setMessage("");
    try {
      const response = await fetch("/djangoapp/registration", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
        body: JSON.stringify(data),
      });
      const result = await response.json();
      if (!response.ok) {
        setMessage(result.message || "Registration failed.");
        return;
      }
      sessionStorage.setItem("username", result.userName);
      window.location.assign("/dealers");
    } catch {
      setMessage("Registration is temporarily unavailable.");
    } finally {
      setPending(false);
    }
  }

  return <>
    <Header />
    <main className="container py-4" style={{ maxWidth: 480 }}>
      <h1>Create an account</h1>
      <form onSubmit={register}>
        {fields.map(([name, label, type, autocomplete]) => (
          <div className="mb-3" key={name}>
            <label htmlFor={name} className="form-label">{label}</label>
            <input className="form-control" id={name} name={name} type={type}
              autoComplete={autocomplete} required />
          </div>
        ))}
        {message && <p role="alert">{message}</p>}
        <button className="btn btn-primary" disabled={pending}>Register</button>
      </form>
    </main>
  </>;
}
