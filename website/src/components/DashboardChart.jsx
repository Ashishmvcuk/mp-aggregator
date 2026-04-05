import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Title,
  Tooltip,
} from 'chart.js'
import { Bar } from 'react-chartjs-2'
import './DashboardChart.css'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

/**
 * @param {{ items: Array<{ university: string; title: string; result_url: string; date: string }> }} props
 */
export function DashboardChart({ items }) {
  const counts = items.reduce((acc, r) => {
    acc[r.university] = (acc[r.university] || 0) + 1
    return acc
  }, /** @type {Record<string, number>} */ ({}))

  const labels = Object.keys(counts).sort((a, b) => counts[b] - counts[a])
  const dataValues = labels.map((l) => counts[l])

  const data = {
    labels,
    datasets: [
      {
        label: 'Results',
        data: dataValues,
        backgroundColor: 'rgba(183, 28, 28, 0.85)',
        borderColor: 'rgba(92, 6, 6, 1)',
        borderWidth: 1,
        borderRadius: 2,
        maxBarThickness: 44,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      title: { display: false },
      tooltip: {
        callbacks: {
          label: (ctx) => `${ctx.parsed.y} result${ctx.parsed.y === 1 ? '' : 's'}`,
        },
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: {
          color: '#333',
          maxRotation: 50,
          minRotation: 0,
          autoSkip: true,
          font: { size: 11, weight: '600' },
        },
      },
      y: {
        beginAtZero: true,
        ticks: { stepSize: 1, color: '#333' },
        grid: { color: 'rgba(0, 0, 0, 0.08)' },
      },
    },
  }

  if (labels.length === 0) {
    return (
      <section className="sr-chart" aria-label="Results chart" id="dashboard">
        <h2 className="sr-chart__title">University wise result count</h2>
        <p className="sr-chart__empty">No data to chart yet.</p>
      </section>
    )
  }

  return (
    <section className="sr-chart" aria-label="Results chart" id="dashboard">
      <h2 className="sr-chart__title">University wise result count</h2>
      <div className="sr-chart__canvas-wrap">
        <Bar data={data} options={options} />
      </div>
    </section>
  )
}
