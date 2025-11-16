import { XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import type { ServerMetrics } from '../../utils/types';
import { format } from 'date-fns';

interface MetricsChartProps {
  metrics: ServerMetrics;
  metricsHistory: ServerMetrics[];
}

export const MetricsChart = ({ metrics, metricsHistory }: MetricsChartProps) => {
  // Prepare chart data from history
  const chartData = metricsHistory.length > 0
    ? metricsHistory.map((m) => {
        const timestamp = m.timestamp ? new Date(m.timestamp) : new Date();
        return {
          name: format(timestamp, 'HH:mm:ss'),
          time: timestamp.getTime(),
          cpu: m.cpu?.usage_percent || 0,
          memory: m.memory?.usage_percent || 0,
          disk: m.disk?.usage_percent || 0,
        };
      })
    : [
        // Fallback to current metrics if no history yet
        {
          name: format(new Date(), 'HH:mm:ss'),
          time: Date.now(),
          cpu: metrics.cpu.usage_percent,
          memory: metrics.memory.usage_percent,
          disk: metrics.disk.usage_percent,
        },
      ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">CPU Usage</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{metrics.cpu.usage_percent.toFixed(1)}%</div>
          <p className="text-xs text-muted-foreground">
            {metrics.cpu.cores} cores @ {metrics.cpu.frequency_mhz} MHz
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Memory Usage</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{metrics.memory.usage_percent.toFixed(1)}%</div>
          <p className="text-xs text-muted-foreground">
            {metrics.memory.used_gb.toFixed(2)} GB / {metrics.memory.total_gb.toFixed(2)} GB
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Disk Usage</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{metrics.disk.usage_percent.toFixed(1)}%</div>
          <p className="text-xs text-muted-foreground">
            {metrics.disk.used_gb.toFixed(2)} GB / {metrics.disk.total_gb.toFixed(2)} GB
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Network</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {(metrics.network.bytes_sent / 1024 / 1024).toFixed(2)} MB
          </div>
          <p className="text-xs text-muted-foreground">
            Sent: {(metrics.network.bytes_sent / 1024 / 1024).toFixed(2)} MB | Recv:{' '}
            {(metrics.network.bytes_recv / 1024 / 1024).toFixed(2)} MB
          </p>
        </CardContent>
      </Card>

      <Card className="md:col-span-2 lg:col-span-4">
        <CardHeader>
          <CardTitle>Usage Over Time</CardTitle>
          <CardDescription>Real-time resource usage metrics</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <defs>
                {/* CPU - Blue/Cyan for processing/tech */}
                <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.6} />
                  <stop offset="50%" stopColor="#60a5fa" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
                {/* Memory - Green matching healthy status */}
                <linearGradient id="colorMemory" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.6} />
                  <stop offset="50%" stopColor="#34d399" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
                {/* Disk - Amber/Orange for warning/caution */}
                <linearGradient id="colorDisk" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.6} />
                  <stop offset="50%" stopColor="#fbbf24" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
              <XAxis 
                dataKey="name" 
                stroke="hsl(var(--muted-foreground))"
                style={{ fontSize: '12px' }}
                interval="preserveStartEnd"
                tick={{ fill: 'hsl(var(--muted-foreground))' }}
              />
              <YAxis 
                stroke="hsl(var(--muted-foreground))"
                style={{ fontSize: '12px' }}
                domain={[0, 100]}
                tick={{ fill: 'hsl(var(--muted-foreground))' }}
                label={{ 
                  value: 'Usage %', 
                  angle: -90, 
                  position: 'insideLeft', 
                  style: { 
                    textAnchor: 'middle', 
                    fill: 'hsl(var(--muted-foreground))' 
                  } 
                }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'hsl(var(--card))', 
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '8px',
                  color: 'hsl(var(--card-foreground))',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
                }}
                labelStyle={{ 
                  color: 'hsl(var(--card-foreground))',
                  fontWeight: 600,
                  marginBottom: '4px'
                }}
                itemStyle={{ 
                  color: 'hsl(var(--card-foreground))'
                }}
              />
              <Legend 
                wrapperStyle={{ color: 'hsl(var(--foreground))' }}
                iconType="circle"
              />
              <Area 
                type="monotone" 
                dataKey="cpu" 
                stroke="#60a5fa" 
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorCpu)" 
                name="CPU %" 
                dot={false}
                activeDot={{ r: 5, fill: '#3b82f6', stroke: '#1e40af', strokeWidth: 2 }}
              />
              <Area 
                type="monotone" 
                dataKey="memory" 
                stroke="#34d399" 
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorMemory)" 
                name="Memory %" 
                dot={false}
                activeDot={{ r: 5, fill: '#10b981', stroke: '#059669', strokeWidth: 2 }}
              />
              <Area 
                type="monotone" 
                dataKey="disk" 
                stroke="#fbbf24" 
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorDisk)" 
                name="Disk %" 
                dot={false}
                activeDot={{ r: 5, fill: '#f59e0b', stroke: '#d97706', strokeWidth: 2 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
};

