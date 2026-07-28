import { useState } from "react";
import { ArrowLeft, Eye, EyeOff, GraduationCap, CheckCircle2, AlertCircle } from "lucide-react";
import { useNavigate } from "react-router";
import authImage from "../../assets/hero2.jpg";
import "./auth.css";
import { authApi, validate } from "./auth-api";

export default function SignupPage() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<{ firstName?: string; lastName?: string; email?: string; password?: string; general?: string }>({});
  const [agreed, setAgreed] = useState(false);
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    
    // Client-side validation
    const firstNameErr = validate.name(firstName);
    const lastNameErr = validate.name(lastName);
    const emailErr = validate.email(email);
    const passErr = validate.password(password, true);

    if (firstNameErr || lastNameErr || emailErr || passErr) {
      setErrors({
        firstName: firstNameErr || "",
        lastName: lastNameErr || "",
        email: emailErr || "",
        password: passErr || "",
      });
      return;
    }

    if (!agreed) {
      setErrors({ general: "Please agree to the terms and conditions to continue." });
      return;
    }

    setLoading(true);
    try {
      await authApi.signup({ firstName, lastName, email, password });
      setSuccess("Registration successful! Redirecting to login...");
      setTimeout(() => navigate("/login"), 2000);
    } catch (err: any) {
      setErrors({ general: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-page">
      <section className="auth-shell reveal" aria-labelledby="signup-heading">
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
            <h1 id="signup-heading">Create your account</h1>
            <p>Start learning with AI-powered support built around your goals.</p>

            {success && (
              <div className="auth-success-banner" role="alert">
                <CheckCircle2 size={18} />
                <span>{success}</span>
              </div>
            )}

            {/* <button className="google-button" type="button">
              <span aria-hidden="true">G</span>
              Sign up with Google
            </button>

            <div className="auth-divider">
              <span>or</span>
            </div> */}

            <form className="auth-form" onSubmit={handleSubmit}>
              {errors.general && (
                <div className="auth-error-banner" role="alert">
                  <AlertCircle size={18} />
                  <span>{errors.general}</span>
                </div>
              )}

              <div className="auth-form-row auth-name-row">
                <label htmlFor="signup-first-name">
                  First name
                  <input
                    id="signup-first-name"
                    name="firstName"
                    type="text"
                    placeholder="First name"
                    autoComplete="given-name"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                  />
                  {errors.firstName && <span className="auth-field-error">{errors.firstName}</span>}
                </label>

                <label htmlFor="signup-last-name">
                  Last name
                  <input
                    id="signup-last-name"
                    name="lastName"
                    type="text"
                    placeholder="Last name"
                    autoComplete="family-name"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                  />
                  {errors.lastName && <span className="auth-field-error">{errors.lastName}</span>}
                </label>
              </div>

              <label htmlFor="signup-email">
                Email
                <input
                  id="signup-email"
                  name="email"
                  type="email"
                  placeholder="Enter your email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
                {errors.email && <span className="auth-field-error">{errors.email}</span>}
              </label>

              <label htmlFor="signup-password">
                Password
                <div className="auth-password-wrap">
                  <input
                    id="signup-password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
                    autoComplete="new-password"
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

              <label className="auth-check" htmlFor="terms">
                <input 
                  id="terms" 
                  name="terms" 
                  type="checkbox" 
                  checked={agreed}
                  onChange={(e) => setAgreed(e.target.checked)}
                  required
                />
                I agree to Kamara AI Terms, Privacy Policy and learning updates
              </label>

              <button className="auth-submit" type="submit" disabled={loading}>
                {loading ? "Creating Account..." : "Sign Up"}
              </button>
            </form>

            <p className="auth-switch">
              Already have an account? <a href="/login">Log in</a>
            </p>
          </div>
        </div>

        <aside className="auth-visual" aria-label="Kamara AI learning preview">
          <img src={authImage} alt="Students learning together with a laptop" />
          <div className="auth-visual-content">
            <h2>Build skills that last</h2>
            <p>
              Learn at your pace with focused courses, smart feedback, and
              support that keeps you moving.
            </p>
            <div className="auth-pills" aria-label="Kamara AI benefits">
              <span>Personalized Learning</span>
              <span>Progress Tracking</span>
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}
