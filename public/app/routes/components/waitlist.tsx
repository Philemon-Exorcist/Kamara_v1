import { useState, type FormEvent } from "react";
import { authApi } from "../auth/auth-api";

/**
 * WaitlistForm Component
 * Handles the logic for joining the waitlist by connecting to the backend API.
 */
export function WaitlistForm() {
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [status, setStatus] = useState<{
    type: "idle" | "loading" | "success" | "error";
    message: string;
  }>({
    type: "idle",
    message: "",
  });

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    setStatus({ type: "loading", message: "Processing..." });

    try {
      const data = await authApi.joinWaitlist({
        email: email.trim(),
        name: fullName.trim(),
      });

      setStatus({
        type: data.status === "already_joined" ? "idle" : "success",
        message: data.message || "Success! You've been added to the waitlist.",
      });

      if (data.status === "success") {
        setEmail("");
        setFullName("");
      }
    } catch (error) {
      setStatus({
        type: "error",
        message:
          error instanceof Error
            ? error.message
            : "Could not reach the server. Please try again.",
      });
    }
  };

  return (
    <form className="waitlist-form" onSubmit={handleSubmit}>
      <label htmlFor="waitlist-name">Join the waitlist</label>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <input
          id="waitlist-name"
          type="text"
          placeholder="Full Name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          required
          disabled={status.type === "loading"}
        />
        <input
          id="waitlist-email"
          type="email"
          placeholder="Enter your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          disabled={status.type === "loading"}
        />
        <button type="submit" disabled={status.type === "loading"}>
          {status.type === "loading" ? "Joining..." : "Join"}
        </button>
      </div>
      
      {status.message && (
        <p style={{ 
          marginTop: '10px', 
          fontSize: '0.85rem', 
          color: status.type === 'error' ? '#ef4444' : '#22c55e' 
        }}>
          {status.message}
        </p>
      )}
    </form>
  );
}
