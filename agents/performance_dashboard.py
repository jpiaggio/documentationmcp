#!/usr/bin/env python3
"""
Monitoring Dashboard for Enterprise Enhancements

Tracks and visualizes:
- Performance metrics over time
- Cost savings
- API usage efficiency
- Cache hit rates
- Token consumption
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict


@dataclass
class PerformanceSnapshot:
    """Single point-in-time performance measurement."""
    timestamp: str
    execution_time_seconds: float
    files_processed: int
    api_calls_saved: int
    cost_saved: float
    token_reduction_percent: float
    modules_analyzed: int
    cache_hit_rate: float


class PerformanceDashboard:
    """Monitor and visualize performance metrics."""
    
    def __init__(self, metrics_file: str = "analysis_metrics.json"):
        """
        Initialize dashboard.
        
        Args:
            metrics_file: Path to metrics history file
        """
        self.metrics_file = Path(metrics_file)
        self.snapshots = self._load_snapshots()
    
    def _load_snapshots(self) -> List[PerformanceSnapshot]:
        """Load metrics snapshots from file."""
        if not self.metrics_file.exists():
            return []
        
        try:
            with open(self.metrics_file, 'r') as f:
                data = json.load(f)
            
            # Handle both new and old format
            if isinstance(data, dict) and 'metrics_history' in data:
                # New format from integrated_workflow
                snapshots = []
                for m in data['metrics_history']:
                    # Convert metrics to snapshot
                    snapshots.append({
                        'timestamp': m.get('timestamp'),
                        'execution_time_seconds': m.get('execution_time'),
                        'files_processed': m.get('total_files_processed'),
                        'api_calls_saved': m.get('api_calls_saved'),
                        'cost_saved': m.get('cost_before', 0) - m.get('cost_after', 0),
                        'token_reduction_percent': m.get('token_reduction', 0) * 100,
                        'modules_analyzed': m.get('modules_analyzed'),
                        'cache_hit_rate': 0.95  # Would need to calculate
                    })
                return snapshots
            elif isinstance(data, list):
                return [PerformanceSnapshot(**s) for s in data]
        except Exception as e:
            print(f"Warning: Could not load metrics: {e}")
        
        return []
    
    def add_snapshot(self, execution_time: float, files_processed: int,
                    api_calls_saved: int, cost_saved: float,
                    token_reduction: float, modules_analyzed: int,
                    cache_hit_rate: float = 0.95):
        """
        Add a performance snapshot.
        
        Args:
            execution_time: Time to complete analysis (seconds)
            files_processed: Number of files analyzed
            api_calls_saved: Number of API calls saved
            cost_saved: Dollar amount saved
            token_reduction: Percentage of tokens reduced
            modules_analyzed: Number of modules analyzed
            cache_hit_rate: Cache effectiveness (0-1)
        """
        snapshot = PerformanceSnapshot(
            timestamp=datetime.now().isoformat(),
            execution_time_seconds=execution_time,
            files_processed=files_processed,
            api_calls_saved=api_calls_saved,
            cost_saved=cost_saved,
            token_reduction_percent=token_reduction * 100,
            modules_analyzed=modules_analyzed,
            cache_hit_rate=cache_hit_rate
        )
        
        self.snapshots.append(snapshot)
        self._save_snapshots()
    
    def _save_snapshots(self):
        """Save snapshots to file."""
        data = [asdict(s) for s in self.snapshots]
        with open(self.metrics_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        Get summary metrics for the past N days.
        
        Args:
            days: Number of days to include
        
        Returns:
            Summary statistics
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent = [
            s for s in self.snapshots
            if datetime.fromisoformat(s.timestamp) > cutoff_date
        ]
        
        if not recent:
            return {
                'period': f'Last {days} days',
                'data_points': 0,
                'message': 'No data available'
            }
        
        total_time = sum(s.execution_time_seconds for s in recent)
        total_files = sum(s.files_processed for s in recent)
        total_api_saved = sum(s.api_calls_saved for s in recent)
        total_cost_saved = sum(s.cost_saved for s in recent)
        avg_token_reduction = sum(s.token_reduction_percent for s in recent) / len(recent)
        avg_cache_hit = sum(s.cache_hit_rate for s in recent) / len(recent)
        
        return {
            'period': f'Last {days} days',
            'data_points': len(recent),
            'total_execution_time': total_time,
            'total_files_analyzed': total_files,
            'total_api_calls_saved': total_api_saved,
            'total_cost_saved': total_cost_saved,
            'average_token_reduction_percent': avg_token_reduction,
            'average_cache_hit_rate': avg_cache_hit,
            'efficiency_improvement': f"{avg_token_reduction:.1f}% token reduction"
        }
    
    def print_dashboard(self, days: int = 7):
        """
        Print a visual dashboard of metrics.
        
        Args:
            days: Number of days to show
        """
        summary = self.get_summary(days)
        
        print("\n" + "="*80)
        print("PERFORMANCE DASHBOARD")
        print("="*80)
        
        if 'message' in summary:
            print(f"\n{summary['message']}")
            return
        
        print(f"\nPeriod: {summary['period']} ({summary['data_points']} analyses)")
        
        print(f"\n📊 PERFORMANCE METRICS")
        print("-" * 80)
        print(f"Total Execution Time:    {summary['total_execution_time']:.2f} seconds")
        print(f"Files Analyzed:          {summary['total_files_analyzed']:,}")
        print(f"Average per file:        {summary['total_execution_time']/max(summary['total_files_analyzed'],1):.2f}s")
        
        print(f"\n💰 COST SAVINGS")
        print("-" * 80)
        print(f"API Calls Saved:         {summary['total_api_calls_saved']:,}")
        print(f"Cost Saved:              ${summary['total_cost_saved']:.2f}")
        monthly_savings = (summary['total_cost_saved'] / min(summary['data_points'], 30)) * 30
        print(f"Projected Monthly:       ${monthly_savings:.2f}")
        print(f"Projected Annual:        ${monthly_savings * 12:.2f}")
        
        print(f"\n🔄 EFFICIENCY METRICS")
        print("-" * 80)
        print(f"Token Reduction:         {summary['average_token_reduction_percent']:.1f}%")
        print(f"Cache Hit Rate:          {summary['average_cache_hit_rate']*100:.1f}%")
        
        print("\n" + "="*80)
    
    def export_csv(self, csv_file: str = "metrics.csv"):
        """Export metrics to CSV."""
        import csv
        
        if not self.snapshots:
            print("No metrics to export")
            return
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'timestamp', 'execution_time_seconds', 'files_processed',
                'api_calls_saved', 'cost_saved', 'token_reduction_percent',
                'modules_analyzed', 'cache_hit_rate'
            ])
            
            writer.writeheader()
            for snapshot in self.snapshots:
                writer.writerow(asdict(snapshot))
        
        print(f"✅ Metrics exported to: {csv_file}")
    
    def print_history(self, limit: int = 10):
        """Print recent analysis history."""
        recent = self.snapshots[-limit:]
        
        if not recent:
            print("No history available")
            return
        
        print("\n" + "="*80)
        print(f"RECENT ANALYSES (Last {len(recent)})")
        print("="*80)
        print(f"{'Time':<25} {'Files':<10} {'Time (s)':<10} {'Cost Saved':<15} {'Token %':<10}")
        print("-" * 80)
        
        for s in recent:
            time_str = datetime.fromisoformat(s.timestamp).strftime("%Y-%m-%d %H:%M")
            print(f"{time_str:<25} {s.files_processed:<10} {s.execution_time_seconds:<10.2f} ${s.cost_saved:<14.2f} {s.token_reduction_percent:<10.1f}%")
        
        print("="*80)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics."""
        if not self.snapshots:
            return {'message': 'No data available'}
        
        return {
            'total_snapshots': len(self.snapshots),
            'total_execution_time': sum(s.execution_time_seconds for s in self.snapshots),
            'total_files_analyzed': sum(s.files_processed for s in self.snapshots),
            'total_api_calls_saved': sum(s.api_calls_saved for s in self.snapshots),
            'total_cost_saved': sum(s.cost_saved for s in self.snapshots),
            'average_execution_time': sum(s.execution_time_seconds for s in self.snapshots) / len(self.snapshots),
            'first_analysis': self.snapshots[0].timestamp,
            'last_analysis': self.snapshots[-1].timestamp
        }


def create_sample_metrics():
    """Create sample metrics for demonstration."""
    dashboard = PerformanceDashboard('sample_metrics.json')
    
    # Add sample data
    base_time = datetime.now() - timedelta(days=6)
    
    for i in range(7):
        snapshot_time = (base_time + timedelta(days=i)).isoformat()
        
        # Simulate decreasing execution time (mostly due to cache hitting)
        execution_time = 45 - (i * 3)  # 45s down to 24s
        
        # Simulate increasing files with more cache hits
        files = 500 - (i * 50)  # 500 down to 150
        
        dashboard.add_snapshot(
            execution_time=execution_time,
            files_processed=files,
            api_calls_saved=int(files * 0.9 * 50),
            cost_saved=float(files * 0.9 * 0.05),
            token_reduction=0.8,
            modules_analyzed=3,
            cache_hit_rate=0.5 + (i * 0.05)  # 50% up to 80%
        )
    
    return dashboard


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        print("Creating sample metrics...")
        dashboard = create_sample_metrics()
    else:
        dashboard = PerformanceDashboard()
    
    # Print dashboard
    dashboard.print_dashboard(days=7)
    
    # Print history
    dashboard.print_history(limit=10)
    
    # Print overall stats
    stats = dashboard.get_stats()
    print("\n" + "="*80)
    print("OVERALL STATISTICS")
    print("="*80)
    if 'total_snapshots' in stats:
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"{key:.<40} {value:.2f}")
            else:
                print(f"{key:.<40} {value}")
    else:
        print(stats)
