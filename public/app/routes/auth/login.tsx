import { useState } from "react";
import { ArrowLeft, Eye, EyeOff, GraduationCap, CheckCircle2, AlertCircle } from "lucide-react";
import { useNavigate } from "react-router";
import authImage from "../../assets/hero2.jpg";
import "./auth.css";
import { authApi, validate } from "./auth-api";
import { getAccessToken, loadCurrentUser, saveLoginSession } from "./session";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<{ email?: string; password?: string; general?: string }>({});
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    // Client-side validation
    const emailErr = validate.email(email);
    const passErr = validate.password(password);

    if (emailErr || passErr) {
      setErrors({ email: emailErr || "", password: passErr || "" });
      return;
    }

    setLoading(true);
    try {
      const data = await authApi.login({ email, password });
      saveLoginSession({ ...data, email });

      const accessToken = getAccessToken();
      if (accessToken) {
        await loadCurrentUser(() => authApi.me(accessToken)).catch(() => null);
      }

      setSuccess("Login successful! Redirecting to dashboard...");
      setTimeout(() => navigate("/dashboard"), 1500);
    } catch (err: any) {
      setErrors({ general: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-page">
      <section className="auth-shell reveal" aria-labelledby="login-heading">
        <div className="auth-panel">
          <div className="auth-topbar">
            <a className="auth-brand" href="/">
              <span aria-hidden="true">
                <GraduationCap size={16} />
              </span>
              Kamara AI
            </a>
            <a className="auth-back" href="/">
              <ArrowLeft size={16} aria-hidden="true" />
              Back
            </a>
          </div>

          <div className="auth-form-wrap">
            <h1 id="login-heading">Welcome back</h1>
            <p>Continue your learning journey with guided courses and AI support.</p>

            {success && (
              <div className="auth-success-banner" role="alert">
                <CheckCircle2 size={18} />
                <span>{success}</span>
              </div>
            )}

            {/* <button className="google-button" type="button">
              <span aria-hidden="true">G</span>
              Login with Google
            </button>

            <div className="auth-divider">
              <span>or</span>
            </div> */}

            <form className="auth-form" onSubmit={handleSubmit}>
              {errors.general && <p className="auth-error-msg" style={{ color: "red", marginBottom: "1rem" }}>{errors.general}</p>}
              <label htmlFor="login-email">
                Email
                <input
                  id="login-email"
                  name="email"
                  type="email"
                  placeholder="Enter your email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
                {errors.email && <span className="auth-field-error">{errors.email}</span>}
              </label>

              <label htmlFor="login-password">
                Password
                <div className="auth-password-wrap">
                  <input
                    id="login-password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
                    autoComplete="current-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                  <button
                    className="auth-password-toggle"
                    type="button"
                    onClick={() => setShowPassword((current) => !current)}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                    aria-pressed={showPassword}
                  >
                    {showPassword ? <EyeOff size={18} aria-hidden="true" /> : <Eye size={18} aria-hidden="true" />}
                  </button>
                </div>
                {errors.password && <span className="auth-field-error">{errors.password}</span>}
              </label>

              <div className="auth-form-row">
                <label className="auth-check" htmlFor="remember-me">
                  <input id="remember-me" name="remember" type="checkbox" />
                  Remember me
                </label>
                <a href="/forgot-password">Forgot password?</a>
              </div>

              <button className="auth-submit" type="submit" disabled={loading}>
                {loading ? "Logging in..." : "Log In"}
              </button>
            </form>

            <p className="auth-switch">
              New to Kamara AI? <a href="/signup">Create an account</a>
            </p>
          </div>
        </div>

        <aside className="auth-visual" aria-label="Kamara AI learning preview">
          <img src={authImage} alt="Students learning together with a laptop" />
          <div className="auth-visual-content">
            <h2>Study smarter with Kamara AI</h2>
            <p>
              Personalized lessons, practical goals, and AI guidance for every
              learner.
            </p>
            <div className="auth-pills" aria-label="Kamara AI benefits">
              <span>AI Study Plans</span>
              <span>Course Guidance</span>
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}
