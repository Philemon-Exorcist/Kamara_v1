import { useEffect, useState } from "react";
import { ArrowLeft, CheckCircle2, Eye, EyeOff, GraduationCap } from "lucide-react";
import { useLocation, useNavigate } from "react-router";
import authImage from "../../assets/hero2.jpg";
import "./auth.css";
import { authApi, validate } from "./auth-api";
import { AuthGate } from "./auth-gate";

type RecoveryCredentials = {
  accessToken?: string;
  refreshToken?: string;
  code?: string;
};

function readRecoveryCredentials(search: string, hash: string): RecoveryCredentials {
  const queryParams = new URLSearchParams(search);
  const hashParams = new URLSearchParams(hash.startsWith("#") ? hash.slice(1) : hash);

  return {
    accessToken: queryParams.get("access_token") || hashParams.get("access_token") || undefined,
    refreshToken: queryParams.get("refresh_token") || hashParams.get("refresh_token") || undefined,
    code: queryParams.get("code") || hashParams.get("code") || undefined,
  };
}

export default function ResetPasswordPage() {
  return (
    <AuthGate>
      <ResetPasswordContent />
    </AuthGate>
  );
}

function ResetPasswordContent() {
  const location = useLocation();
  const navigate = useNavigate();

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const [recoveryCredentials, setRecoveryCredentials] = useState<RecoveryCredentials>({});

  useEffect(() => {
    setRecoveryCredentials(readRecoveryCredentials(location.search, location.hash));
  }, [location.hash, location.search]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    const passErr = validate.password(password, true);
    if (passErr) {
      setError(passErr);
      return;
    }

    if (!confirmPassword) {
      setError("Please confirm your new password.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (
      !recoveryCredentials.code &&
      (!recoveryCredentials.accessToken || !recoveryCredentials.refreshToken)
    ) {
      setError("This password reset link is missing recovery data. Please request a new link.");
      return;
    }

    setLoading(true);
    try {
      await authApi.updatePassword({
        ...recoveryCredentials,
        newPassword: password,
      });
      setSuccess("Password updated successfully. Redirecting to login...");
      setTimeout(() => navigate("/login"), 1600);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-page">
      <section className="auth-shell reveal" aria-labelledby="reset-password-heading">
        <div className="auth-panel">
          <div className="auth-topbar">
            <a className="auth-brand" href="/">
              <span aria-hidden="true">
                <GraduationCap size={16} />
              </span>
              Kamara AI
            </a>
            <a className="auth-back" href="/forgot-password">
              <ArrowLeft size={16} aria-hidden="true" />
              Back
            </a>
          </div>

          <div className="auth-form-wrap">
            <h1 id="reset-password-heading">Create a new password</h1>
            <p>Enter and confirm your new password to finish updating your account.</p>

            {success && (
              <div className="auth-success-banner" role="alert">
                <CheckCircle2 size={18} />
                <span>{success}</span>
              </div>
            )}

            <form className="auth-form" onSubmit={handleSubmit}>
              {error && (
                <div className="auth-error-banner" role="alert">
                  <span>{error}</span>
                </div>
              )}

              <label htmlFor="new-password">
                New password
                <div className="auth-password-wrap">
                  <input
                    id="new-password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter new password"
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
              </label>

              <label htmlFor="confirm-password">
                Confirm password
                <div className="auth-password-wrap">
                  <input
                    id="confirm-password"
                    name="confirmPassword"
                    type={showConfirmPassword ? "text" : "password"}
                    placeholder="Confirm new password"
                    autoComplete="new-password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                  />
                  <button
                    className="auth-password-toggle"
                    type="button"
                    onClick={() => setShowConfirmPassword((current) => !current)}
                    aria-label={
                      showConfirmPassword ? "Hide password confirmation" : "Show password confirmation"
                    }
                    aria-pressed={showConfirmPassword}
                  >
                    {showConfirmPassword ? <EyeOff size={18} aria-hidden="true" /> : <Eye size={18} aria-hidden="true" />}
                  </button>
                </div>
              </label>

              <button className="auth-submit" type="submit" disabled={loading}>
                {loading ? "Updating password..." : "Update password"}
              </button>
            </form>
          </div>
        </div>

        <aside className="auth-visual" aria-label="Kamara AI learning preview">
          <img src={authImage} alt="Students learning together with a laptop" />
          <div className="auth-visual-content">
            <h2>Finish the reset and sign in again</h2>
            <p>Once your new password is saved, you will be sent back to the login page automatically.</p>
            <div className="auth-pills" aria-label="Password reset benefits">
              <span>Secure reset</span>
              <span>Quick login</span>
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}
