import {
  useEffect,
  useState
} from "react";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from "recharts";


function AnalyticsDashboard() {

  const [summary, setSummary] =
    useState(null);

  const [junctions, setJunctions] =
    useState([]);

  const [hourly, setHourly] =
    useState([]);

  const [peak, setPeak] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  // ==========================================================
  // LOAD ANALYTICS
  // ==========================================================

  useEffect(() => {

    async function loadDashboard() {

      try {

        const [
          summaryResponse,
          junctionResponse,
          hourlyResponse,
          peakResponse
        ] = await Promise.all([

          fetch(
            "http://127.0.0.1:5000/api/analytics/summary"
          ),

          fetch(
            "http://127.0.0.1:5000/api/analytics/junctions"
          ),

          fetch(
            "http://127.0.0.1:5000/api/analytics/hourly"
          ),

          fetch(
            "http://127.0.0.1:5000/api/analytics/peak"
          )

        ]);


        if (
          !summaryResponse.ok ||
          !junctionResponse.ok ||
          !hourlyResponse.ok ||
          !peakResponse.ok
        ) {

          throw new Error(
            "Unable to load dashboard data."
          );

        }


        const summaryData =
          await summaryResponse.json();

        const junctionData =
          await junctionResponse.json();

        const hourlyData =
          await hourlyResponse.json();

        const peakData =
          await peakResponse.json();


        setSummary(summaryData);

        setJunctions(
          junctionData.junctions || []
        );

        setHourly(
          hourlyData.hourly || []
        );

        setPeak(peakData);


      } catch (err) {

        setError(
          err.message
        );

      } finally {

        setLoading(false);

      }

    }


    loadDashboard();

  }, []);


  // ==========================================================
  // LOADING
  // ==========================================================

  if (loading) {

    return (

      <section className="dashboard-loading">

        <div className="loading-spinner"></div>

        <p>
          Loading traffic analytics...
        </p>

      </section>

    );

  }


  // ==========================================================
  // ERROR
  // ==========================================================

  if (error) {

    return (

      <section className="dashboard-error">

        <h3>
          Dashboard Error
        </h3>

        <p>
          {error}
        </p>

        <p>
          Make sure Flask is running on
          port 5000.
        </p>

      </section>

    );

  }


  // ==========================================================
  // DASHBOARD
  // ==========================================================

  return (

    <section className="analytics-dashboard">


      {/* ==================================================== */}
      {/* DASHBOARD HEADER                                    */}
      {/* ==================================================== */}

      <div className="dashboard-header">

        <div>

          <span className="dashboard-label">
            TRAFFIC ANALYTICS
          </span>

          <h2>
            Urban Traffic Overview
          </h2>

          <p>
            Historical traffic intelligence
            derived from the provided traffic dataset.
          </p>

        </div>

      </div>


      {/* ==================================================== */}
      {/* KPI CARDS                                           */}
      {/* ==================================================== */}

      <div className="kpi-grid">


        {/* TOTAL OBSERVATIONS */}

        <div className="kpi-card">

          <span>
            Total Observations
          </span>

          <strong>
            {summary?.total_observations?.toLocaleString()}
          </strong>

          <small>
            traffic records
          </small>

        </div>


        {/* AVERAGE */}

        <div className="kpi-card">

          <span>
            Average Vehicles
          </span>

          <strong>
            {summary?.average_vehicles}
          </strong>

          <small>
            per observation
          </small>

        </div>


        {/* MAXIMUM */}

        <div className="kpi-card">

          <span>
            Maximum Vehicles
          </span>

          <strong>
            {summary?.maximum_vehicles}
          </strong>

          <small>
            highest observed volume
          </small>

        </div>


        {/* JUNCTIONS */}

        <div className="kpi-card">

          <span>
            Monitored Junctions
          </span>

          <strong>
            {summary?.junction_count}
          </strong>

          <small>
            traffic locations
          </small>

        </div>

      </div>


      {/* ==================================================== */}
      {/* PEAK INFORMATION                                    */}
      {/* ==================================================== */}

      <div className="peak-panel">


        <div className="peak-item">

          <span>
            Peak Traffic Hour
          </span>

          <strong>
            {peak?.peak_hour}:00
          </strong>

          <small>
            {peak?.peak_average_vehicles}
            {" "}
            vehicles average
          </small>

        </div>


        <div className="peak-item">

          <span>
            Lowest Traffic Hour
          </span>

          <strong>
            {peak?.lowest_hour}:00
          </strong>

          <small>
            {peak?.lowest_average_vehicles}
            {" "}
            vehicles average
          </small>

        </div>


        <div className="peak-item">

          <span>
            Traffic Range
          </span>

          <strong>
            {summary?.minimum_vehicles}
            {" – "}
            {summary?.maximum_vehicles}
          </strong>

          <small>
            observed vehicle range
          </small>

        </div>

      </div>


      {/* ==================================================== */}
      {/* CHART GRID                                          */}
      {/* ==================================================== */}

      <div className="chart-grid">


        {/* HOURLY TRAFFIC */}

        <div className="chart-card">

          <div className="chart-header">

            <div>

              <h3>
                Hourly Traffic Pattern
              </h3>

              <p>
                Average traffic volume by hour of day.
              </p>

            </div>

          </div>


          <div className="chart">

            <ResponsiveContainer
              width="100%"
              height={360}
            >

              <LineChart
                data={hourly}
                margin={{
                  top: 15,
                  right: 20,
                  left: 0,
                  bottom: 10
                }}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                />

                <XAxis
                  dataKey="hour"
                  tickFormatter={(hour) =>
                    `${hour}:00`
                  }
                />

                <YAxis />

                <Tooltip
                  labelFormatter={(hour) =>
                    `${hour}:00`
                  }
                />

                <Line
                  type="monotone"
                  dataKey="average_vehicles"
                  name="Average Vehicles"
                  stroke="#2563eb"
                  strokeWidth={3}
                  dot={false}
                />

              </LineChart>

            </ResponsiveContainer>

          </div>

        </div>


        {/* JUNCTION COMPARISON */}

        <div className="chart-card">

          <div className="chart-header">

            <div>

              <h3>
                Junction Comparison
              </h3>

              <p>
                Average traffic volume by junction.
              </p>

            </div>

          </div>


          <div className="chart">

            <ResponsiveContainer
              width="100%"
              height={360}
            >

              <BarChart
                data={junctions}
                margin={{
                  top: 15,
                  right: 20,
                  left: 0,
                  bottom: 10
                }}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                />

                <XAxis
                  dataKey="junction"
                  tickFormatter={(value) =>
                    `J${value}`
                  }
                />

                <YAxis />

                <Tooltip />

                <Bar
                  dataKey="average_vehicles"
                  name="Average Vehicles"
                  fill="#2563eb"
                  radius={[
                    5,
                    5,
                    0,
                    0
                  ]}
                />

              </BarChart>

            </ResponsiveContainer>

          </div>

        </div>

      </div>


      {/* ==================================================== */}
      {/* JUNCTION TABLE                                      */}
      {/* ==================================================== */}

      <div className="table-card">

        <div className="chart-header">

          <div>

            <h3>
              Junction Intelligence
            </h3>

            <p>
              Traffic statistics for each monitored junction.
            </p>

          </div>

        </div>


        <div className="table-wrapper">

          <table>

            <thead>

              <tr>

                <th>
                  Rank
                </th>

                <th>
                  Junction
                </th>

                <th>
                  Average Vehicles
                </th>

                <th>
                  Maximum Vehicles
                </th>

                <th>
                  Total Vehicles
                </th>

                <th>
                  Observations
                </th>

              </tr>

            </thead>


            <tbody>

              {junctions.map(
                (item, index) => (

                  <tr
                    key={
                      item.junction
                    }
                  >

                    <td>
                      {index + 1}
                    </td>

                    <td>
                      <strong>
                        Junction {
                          item.junction
                        }
                      </strong>
                    </td>

                    <td>
                      {
                        item.average_vehicles
                      }
                    </td>

                    <td>
                      {
                        item.maximum_vehicles
                      }
                    </td>

                    <td>
                      {
                        item.total_vehicles
                          ?.toLocaleString()
                      }
                    </td>

                    <td>
                      {
                        item.observations
                          ?.toLocaleString()
                      }
                    </td>

                  </tr>

                )
              )}

            </tbody>

          </table>

        </div>

      </div>


      {/* ==================================================== */}
      {/* DATA SOURCE                                         */}
      {/* ==================================================== */}

      <div className="data-source">

        <strong>
          Data Source
        </strong>

        <span>
          Historical traffic observations
          processed from the provided dataset.
        </span>

      </div>


    </section>

  );

}


export default AnalyticsDashboard;