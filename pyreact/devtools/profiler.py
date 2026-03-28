"""
Profiler Module
===============

Performance profiling for PyReact components.
"""

from typing import Any, Dict, List, Optional
import time


class Profiler:
    """
    Profiler for measuring component performance
    
    Tracks render times, commit times, and identifies
    performance bottlenecks.
    
    Example:
        profiler = Profiler()
        profiler.start()
        
        # ... render components ...
        
        profiler.stop()
        report = profiler.get_report()
    """
    
    def __init__(self):
        self._enabled: bool = False
        self._current_phase: Optional[str] = None
        self._measurements: List[Dict] = []
        self._component_times: Dict[str, List[float]] = {}
        self._render_times: List[float] = []
        self._commit_times: List[float] = []
        self._start_time: float = 0
        self._phase_start: float = 0
    
    def start(self) -> None:
        """Start profiling"""
        self._enabled = True
        self._start_time = time.time()
        self.log("Profiler started")
    
    def stop(self) -> None:
        """Stop profiling"""
        self._enabled = False
        self.log("Profiler stopped")
    
    def is_enabled(self) -> bool:
        """Check if profiling is enabled"""
        return self._enabled
    
    def begin_render(self, component_name: str) -> None:
        """
        Begin measuring render phase
        
        Args:
            component_name: Name of component being rendered
        """
        if not self._enabled:
            return
        
        self._current_phase = 'render'
        self._phase_start = time.time()
        
        self._measurements.append({
            'type': 'render_begin',
            'component': component_name,
            'timestamp': self._phase_start
        })
    
    def end_render(self, component_name: str) -> float:
        """
        End measuring render phase
        
        Args:
            component_name: Name of component
        
        Returns:
            float: Render time in milliseconds
        """
        if not self._enabled:
            return 0
        
        end_time = time.time()
        render_time = (end_time - self._phase_start) * 1000  # Convert to ms
        
        self._render_times.append(render_time)
        
        if component_name not in self._component_times:
            self._component_times[component_name] = []
        self._component_times[component_name].append(render_time)
        
        self._measurements.append({
            'type': 'render_end',
            'component': component_name,
            'timestamp': end_time,
            'duration': render_time
        })
        
        self._current_phase = None
        return render_time
    
    def begin_commit(self) -> None:
        """Begin measuring commit phase"""
        if not self._enabled:
            return
        
        self._current_phase = 'commit'
        self._phase_start = time.time()
    
    def end_commit(self) -> float:
        """
        End measuring commit phase
        
        Returns:
            float: Commit time in milliseconds
        """
        if not self._enabled:
            return 0
        
        end_time = time.time()
        commit_time = (end_time - self._phase_start) * 1000
        
        self._commit_times.append(commit_time)
        
        self._measurements.append({
            'type': 'commit',
            'timestamp': end_time,
            'duration': commit_time
        })
        
        self._current_phase = None
        return commit_time
    
    def log(self, message: str, data: Optional[Dict] = None) -> None:
        """
        Log a profiling message
        
        Args:
            message: Log message
            data: Optional data
        """
        if not self._enabled:
            return
        
        self._measurements.append({
            'type': 'log',
            'message': message,
            'data': data or {},
            'timestamp': time.time()
        })
    
    def get_report(self) -> Dict:
        """
        Get profiling report
        
        Returns:
            dict: Profiling report
        """
        total_render_time = sum(self._render_times)
        total_commit_time = sum(self._commit_times)
        
        # Calculate component statistics
        component_stats = {}
        for name, times in self._component_times.items():
            if times:
                component_stats[name] = {
                    'count': len(times),
                    'total': sum(times),
                    'average': sum(times) / len(times),
                    'min': min(times),
                    'max': max(times)
                }
        
        return {
            'total_time': (time.time() - self._start_time) * 1000,
            'render_time': total_render_time,
            'commit_time': total_commit_time,
            'render_count': len(self._render_times),
            'commit_count': len(self._commit_times),
            'average_render_time': total_render_time / len(self._render_times) if self._render_times else 0,
            'average_commit_time': total_commit_time / len(self._commit_times) if self._commit_times else 0,
            'component_stats': component_stats,
            'measurements': self._measurements[-100:]  # Last 100 measurements
        }
    
    def get_slow_components(self, threshold: float = 16.0) -> List[Dict]:
        """
        Get components that exceed threshold
        
        Args:
            threshold: Threshold in milliseconds (default: 16ms for 60fps)
        
        Returns:
            list: Slow components
        """
        slow = []
        for name, times in self._component_times.items():
            avg_time = sum(times) / len(times) if times else 0
            if avg_time > threshold:
                slow.append({
                    'name': name,
                    'average_time': avg_time,
                    'count': len(times),
                    'max_time': max(times)
                })
        
        return sorted(slow, key=lambda x: x['average_time'], reverse=True)
    
    def clear(self) -> None:
        """Clear profiling data"""
        self._measurements.clear()
        self._component_times.clear()
        self._render_times.clear()
        self._commit_times.clear()
    
    def export(self) -> str:
        """
        Export profiling data as JSON
        
        Returns:
            str: JSON string
        """
        import json
        return json.dumps(self.get_report(), indent=2)


# Global profiler instance
_profiler = Profiler()


def get_profiler() -> Profiler:
    """Get the global profiler"""
    return _profiler


def profile_component(component: Any) -> Dict:
    """
    Profile a single component
    
    Args:
        component: Component instance
    
    Returns:
        dict: Component profile data
    """
    name = component.__class__.__name__
    times = _profiler._component_times.get(name, [])
    
    if times:
        return {
            'name': name,
            'count': len(times),
            'total': sum(times),
            'average': sum(times) / len(times),
            'min': min(times),
            'max': max(times)
        }
    
    return {'name': name, 'count': 0}


def get_profile_data() -> Dict:
    """
    Get all profile data
    
    Returns:
        dict: Profile data
    """
    return _profiler.get_report()


def start_profiling() -> None:
    """Start profiling"""
    _profiler.start()


def stop_profiling() -> Dict:
    """
    Stop profiling and get report
    
    Returns:
        dict: Profiling report
    """
    _profiler.stop()
    return _profiler.get_report()
