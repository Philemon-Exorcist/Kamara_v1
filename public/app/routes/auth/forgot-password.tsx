import { useState } from "react";
import { ArrowLeft, CheckCircle2, GraduationCap } from "lucide-react";
import { useNavigate } from "react-router";
import authImage from "../../assets/hero2.jpg";
import "./auth.css";
import { validate } from "./auth-api";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [codeSent, setCodeSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSendCode = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setMessage("");

    const emailErr = validate.email(email);
    if (emailErr) {
      setError(emailErr);
      return;
    }

    setLoading(true);
    setTimeout(() => {
      setCodeSent(true);
      setMessage("Verification code sent to your email.");
      setLoading(false);
    }, 700);
  };

  const handleVerifyCode = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!code.trim()) {
      setError("Please enter the verification code.");
      return;
    }

    navigate("/reset-password", { state: { email, code } });
  };

  return (
    <main className="auth-page">
      <section className="auth-shell reveal" aria-labelledby="forgot-password-heading">
        <div className="auth-panel">
          <div className="auth-topbar">
            <a className="auth-brand" href="/">
              <span aria-hidden="true">
                <GraduationCap size={16} />
              </span>
              Kamara AI
            </a>
            <a className="auth-back" href="/login">
              <ArrowLeft size={16} aria-hidden="true" />
              Back to login
            </a>
          </div>

          <div className="auth-form-wrap">
            <h1 id="forgot-password-heading">Reset your password</h1>
            <p>Enter your email, request a code, then verify it to continue.</p>

            {message && (
              <div className="auth-success-banner" role="alert">
                <CheckCircle2 size={18} />
                <span>{message}</span>
              </div>
            )}

            <form className="auth-form" onSubmit={codeSent ? handleVerifyCode : handleSendCode}>
              {error && <div className="auth-error-banner" role="alert"><span>{error}</span></div>}

              <label htmlFor="forgot-email">
                Email
                <input
                  id="forgot-email"
                  name="email"
                  type="email"
                  placeholder="Enter your email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </label>

              {codeSent && (
                <label htmlFor="reset-code">
                  Verification code
                  <input
                    id="reset-code"
                    name="code"
                    type="text"
                    placeholder="Enter the code you received"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                  />
                </label>
              )}

              <button className="auth-submit" type="submit" disabled={loading}>
                {loading ? "Sending code..." : codeSent ? "Verify code" : "Send code"}
              </button>
            </form>
          </div>
        </div>

        <aside className="auth-visual" aria-label="Kamara AI learning preview">
          <img src={authImage} alt="Students learning together with a laptop" />
          <div className="auth-visual-content">
            <h2>Get back into your account fast</h2>
            <p>We’ll help you verify your identity and set a new password in a few steps.</p>
            <div className="auth-pills" aria-label="Password reset steps">
              <span>Email</span>
              <span>Code</span>
              <span>New password</span>
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}
