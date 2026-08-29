import { useEffect, useState } from "react";
import "./App.css";
import AnalyticsDashboard from './AnalyticsDashboard';

function App() {
  const [junctions, setJunctions] = useState([]);
  const [showDashboard, setShowDashboard] =
  useState(true);
  const [form, setForm] = useState({
    Junction: 1,
    DateTime: "2017-06-30T10:00",
  });

  const [result, setResult] = useState(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  // ============================================================
  // LOAD JUNCTIONS FROM FLASK
  // ============================================================

  useEffect(() => {
    async function loadJunctions() {
      try {
        const response = await fetch(
          "http://127.0.0.1:5000/api/junctions"
        );

        if (!response.ok) {
          throw new Error(
            "Unable to connect to Flask backend."
          );
        }

        const data = await response.json();

        setJunctions(data.junctions);

        if (data.junctions.length > 0) {
          setForm((previous) => ({
            ...previous,
            Junction: data.junctions[0],
          }));
        }
      } catch (err) {
        setError(err.message);
      }
    }

    loadJunctions();
  }, []);

  // ============================================================
  // HANDLE INPUT CHANGE
  // ============================================================

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,

      [name]:
        name === "Junction"
          ? Number(value)
          : value,
    }));
  }

  // ============================================================
  // CALL FLASK PREDICTION API
  // ============================================================

  async function handlePredict(event) {
    event.preventDefault();

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:5000/api/predict",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            Junction: form.Junction,
            DateTime: form.DateTime,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error ||
            "Traffic prediction failed."
        );
      }

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // ============================================================
  // TRAFFIC LEVEL CSS CLASS
  // ============================================================

  function getLevelClass(level) {
    switch (level) {
      case "LOW":
        return "low";

      case "MODERATE":
        return "moderate";

      case "HIGH":
        return "high";

      case "CRITICAL":
        return "critical";

      default:
        return "";
    }
  }

  // ============================================================
  // PAGE
  // ============================================================

  return (
    <div className="app">

      {/* ====================================================== */}
      {/* HEADER                                                 */}
      {/* ====================================================== */}

      <header className="header">

        <div className="header-content">

          <div>

            <div className="badge">
              AI-POWERED TRANSPORT INTELLIGENCE
            </div>

            <h1>
              Urban Traffic Intelligence
            </h1>

            <p>
              Predict future traffic conditions using
              historical junction traffic patterns.
            </p>

          </div>

        </div>

      </header>


      {/* ====================================================== */}
      {/* MAIN                                                   */}
      {/* ====================================================== */}

      <main className="container">


        {/* ==================================================== */}
        {/* PREDICTION CARD                                      */}
        {/* ==================================================== */}

        <section className="card">

          <div className="section-heading">

            <div>

              <h2>
                Traffic Prediction
              </h2>

              <p>
                Select a junction and prediction time.
              </p>

            </div>

          </div>


          <form
            className="prediction-form"
            onSubmit={handlePredict}
          >

            {/* JUNCTION */}

            <div className="form-group">

              <label htmlFor="Junction">
                Junction
              </label>

              <select
                id="Junction"
                name="Junction"
                value={form.Junction}
                onChange={handleChange}
              >

                {junctions.length === 0 ? (

                  <option>
                    Loading junctions...
                  </option>

                ) : (

                  junctions.map(
                    (junction) => (

                      <option
                        key={junction}
                        value={junction}
                      >
                        Junction {junction}
                      </option>

                    )
                  )

                )}

              </select>

            </div>


            {/* DATE AND TIME */}

            <div className="form-group">

              <label htmlFor="DateTime">
                Prediction Date & Time
              </label>

              <input
                id="DateTime"
                name="DateTime"
                type="datetime-local"
                value={form.DateTime}
                onChange={handleChange}
              />

            </div>


            {/* BUTTON */}

            <button
              className="predict-button"
              type="submit"
              disabled={loading}
            >

              {loading
                ? "Analyzing Traffic..."
                : "Predict Traffic"}

            </button>

          </form>

        </section>


        {/* ==================================================== */}
        {/* ERROR                                                 */}
        {/* ==================================================== */}

        {error && (

          <section className="error-box">

            <strong>
              Error
            </strong>

            <p>
              {error}
            </p>

          </section>

        )}


        {/* ==================================================== */}
        {/* RESULT                                                */}
        {/* ==================================================== */}

        {result && (

          <section className="card result-section">

            <div className="section-heading">

              <div>

                <h2>
                  AI Prediction Result
                </h2>

                <p>
                  Junction {result.junction}
                  {" • "}
                  {result.requested_datetime}
                </p>

              </div>

              <div
                className={
                  `status-badge ${getLevelClass(
                    result.congestion_level
                  )}`
                }
              >
                {result.congestion_level}
              </div>

            </div>


            {/* METRICS */}

            <div className="result-grid">

              {/* PREDICTED */}

              <div className="metric-card">

                <span>
                  Predicted Vehicles
                </span>

                <strong>
                  {result.predicted_vehicles}
                </strong>

                <small>
                  expected next hour
                </small>

              </div>


              {/* HISTORICAL */}

              <div className="metric-card">

                <span>
                  Historical Average
                </span>

                <strong>
                  {result.historical_average}
                </strong>

                <small>
                  learned traffic baseline
                </small>

              </div>


              {/* RISK */}

              <div className="metric-card">

                <span>
                  Risk Score
                </span>

                <strong>
                  {result.risk_score}
                </strong>

                <small>
                  out of 100
                </small>

              </div>


              {/* PEAK */}

              <div className="metric-card">

                <span>
                  Peak Period
                </span>

                <strong>
                  {result.is_peak_hour
                    ? "YES"
                    : "NO"}
                </strong>

                <small>
                  based on traffic time patterns
                </small>

              </div>

            </div>


            {/* ================================================= */}
            {/* DETAILS                                           */}
            {/* ================================================= */}

            <div className="details-grid">

              <div className="detail-card">

                <span>
                  Last Historical Observation
                </span>

                <strong>
                  {result.last_observation}
                </strong>

              </div>


              <div className="detail-card">

                <span>
                  Model
                </span>

                <strong>
                  XGBoost
                </strong>

              </div>

            </div>


            {/* ================================================= */}
            {/* RECOMMENDATION                                    */}
            {/* ================================================= */}

            <div className="recommendation">

              <div className="recommendation-title">

                AI Traffic Recommendation

              </div>

              <p>
                {result.recommendation}
              </p>

            </div>

          </section>

        )}


        {/* ==================================================== */}
        {/* HOW IT WORKS                                         */}
        {/* ==================================================== */}

        <section className="card">

          <div className="section-heading">

            <div>

              <h2>
                How the AI Works
              </h2>

              <p>
                The system learns from historical traffic
                behaviour before making a prediction.
              </p>

            </div>

          </div>


          <div className="pipeline">

            <div className="pipeline-step">

              <span>
                01
              </span>

              <strong>
                Traffic Data
              </strong>

              <p>
                Historical junction observations
              </p>

            </div>


            <div className="pipeline-arrow">
              →
            </div>


            <div className="pipeline-step">

              <span>
                02
              </span>

              <strong>
                Feature Engineering
              </strong>

              <p>
                Time and historical traffic features
              </p>

            </div>


            <div className="pipeline-arrow">
              →
            </div>


            <div className="pipeline-step">

              <span>
                03
              </span>

              <strong>
                XGBoost
              </strong>

              <p>
                Next-hour traffic prediction
              </p>

            </div>


            <div className="pipeline-arrow">
              →
            </div>


            <div className="pipeline-step">

              <span>
                04
              </span>

              <strong>
                Intelligence
              </strong>

              <p>
                Risk and traffic recommendation
              </p>

            </div>

          </div>

        </section>


      </main>


      {/* ====================================================== */}
      {/* FOOTER                                                 */}
      {/* ====================================================== */}

      <footer className="footer">

        AI Urban Traffic Intelligence

        <span>
          •
        </span>

        Flask + XGBoost + React

      </footer>

    </div>
  );
}

export default App;