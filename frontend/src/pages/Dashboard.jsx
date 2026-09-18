import React, { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { Users, FileText, MessageCircle, Timer } from 'lucide-react'
import { fetchDashboardStats } from '../services/dashboardService'

function StatCard({ icon: Icon, label, value }) {
  return (
    <div className="card p-5 flex items-center gap-4">
      <div className="bg-sage p-3 rounded-lg">
        <Icon size={22} className="text-amber" />
      </div>
      <div>
        <p className="text-2xl font-display font-semibold">{value}</p>
        <p className="text-xs text-ink-soft">{label}</p>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [stats, setStats] = useState(null)

  useEffect(() => { fetchDashboardStats().then(setStats) }, [])

  if (!stats) return <div className="px-8 py-6 text-ink-soft">Chargement du tableau de bord...</div>

  return (
    <div className="px-8 py-6">
      <h1 className="font-display text-2xl font-semibold mb-1">Tableau de bord</h1>
      <p className="text-sm text-ink-soft mb-6">Statistiques d'utilisation de la plateforme</p>

      <div className="grid grid-cols-4 gap-4 mb-8">
        <StatCard icon={Users} label="Utilisateurs" value={stats.num_users} />
        <StatCard icon={FileText} label="Documents indexés" value={stats.num_documents} />
        <StatCard icon={MessageCircle} label="Questions posées" value={stats.num_questions} />
        <StatCard icon={Timer} label="Temps de réponse moyen" value={`${(stats.avg_response_time_ms / 1000).toFixed(1)}s`} />
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="card p-5">
          <h2 className="font-display font-semibold mb-4">Documents les plus consultés</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={stats.most_viewed_documents} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#DCE1CF" />
              <XAxis type="number" fontSize={12} />
              <YAxis dataKey="title" type="category" width={140} fontSize={11} />
              <Tooltip />
              <Bar dataKey="views" fill="#C97A3D" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card p-5">
          <h2 className="font-display font-semibold mb-4">Matières les plus utilisées</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={stats.most_used_subjects} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#DCE1CF" />
              <XAxis type="number" fontSize={12} />
              <YAxis dataKey="name" type="category" width={140} fontSize={11} />
              <Tooltip />
              <Bar dataKey="count" fill="#8FA084" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
