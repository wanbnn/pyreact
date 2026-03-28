"""
Scheduler Module
================

This module implements the scheduler for managing updates
with different priorities.
"""

from typing import Any, Callable, Dict, List, Optional
from enum import IntEnum
import time


class Priority(IntEnum):
    """Priority levels for scheduled updates"""
    IMMEDIATE = 99      # Execute immediately
    USER_BLOCKING = 98  # User interactions
    NORMAL = 97         # Normal updates
    LOW = 96            # Preloading, etc.
    IDLE = 95           # Background tasks


def get_timeout_for_priority(priority: Priority) -> float:
    """Get timeout for a priority level"""
    timeouts = {
        Priority.IMMEDIATE: 0,
        Priority.USER_BLOCKING: 250,
        Priority.NORMAL: 5000,
        Priority.LOW: 10000,
        Priority.IDLE: float('inf')
    }
    return timeouts.get(priority, 5000)


class Task:
    """Scheduled task"""
    
    def __init__(
        self,
        callback: Callable,
        priority: Priority,
        expiration_time: float
    ):
        self.callback = callback
        self.priority = priority
        self.expiration_time = expiration_time
        self.completed = False
    
    def __lt__(self, other: 'Task') -> bool:
        """Compare tasks by priority (higher priority first)"""
        return self.priority > other.priority
    
    def __repr__(self) -> str:
        return f"Task(priority={self.priority.name}, completed={self.completed})"


class Scheduler:
    """
    Scheduler for managing updates with priorities
    
    Implements a priority queue for scheduling callbacks.
    Higher priority tasks are executed first.
    
    Example:
        scheduler = Scheduler()
        
        # Schedule high priority task
        scheduler.schedule_callback(
            lambda: print('User interaction'),
            Priority.USER_BLOCKING
        )
        
        # Schedule low priority task
        scheduler.schedule_callback(
            lambda: print('Background task'),
            Priority.IDLE
        )
    """
    
    IMMEDIATE_PRIORITY = Priority.IMMEDIATE
    USER_BLOCKING_PRIORITY = Priority.USER_BLOCKING
    NORMAL_PRIORITY = Priority.NORMAL
    LOW_PRIORITY = Priority.LOW
    IDLE_PRIORITY = Priority.IDLE
    
    def __init__(self):
        self._queue: List[Task] = []
        self._scheduled: bool = False
        self._is_flushing: bool = False
        self._current_task: Optional[Task] = None
    
    def schedule_callback(
        self,
        callback: Callable,
        priority: Priority = Priority.NORMAL
    ) -> Task:
        """
        Schedule a callback with a priority
        
        Args:
            callback: Function to execute
            priority: Priority level
        
        Returns:
            Task: The scheduled task
        """
        timeout = get_timeout_for_priority(priority)
        expiration_time = time.time() + timeout
        
        task = Task(callback, priority, expiration_time)
        
        # Insert sorted by priority
        self._insert_sorted(task)
        
        # Ensure work loop is scheduled
        self._ensure_scheduled()
        
        return task
    
    def _insert_sorted(self, task: Task) -> None:
        """Insert task in sorted order"""
        for i, existing in enumerate(self._queue):
            if task < existing:
                self._queue.insert(i, task)
                return
        self._queue.append(task)
    
    def _ensure_scheduled(self) -> None:
        """Ensure the work loop is scheduled"""
        if not self._scheduled:
            self._scheduled = True
            self._schedule_work_loop()
    
    def _schedule_work_loop(self) -> None:
        """Schedule the work loop (override for different platforms)"""
        # In a real implementation, this would use requestIdleCallback or similar
        # For now, we'll execute immediately
        self._work_loop()
    
    def _work_loop(self) -> None:
        """Process tasks until deadline or queue is empty"""
        self._is_flushing = True
        
        try:
            while self._queue:
                task = self._queue[0]
                
                # Check if task has expired
                if task.expiration_time < time.time():
                    # Task expired, execute it
                    self._queue.pop(0)
                    self._execute_task(task)
                else:
                    # Check if we should yield
                    # In a real implementation, we'd check deadline
                    self._queue.pop(0)
                    self._execute_task(task)
        finally:
            self._is_flushing = False
            self._scheduled = False
            
            # Re-schedule if there are more tasks
            if self._queue:
                self._ensure_scheduled()
    
    def _execute_task(self, task: Task) -> None:
        """Execute a single task"""
        self._current_task = task
        try:
            task.callback()
            task.completed = True
        except Exception as e:
            print(f"Error executing scheduled task: {e}")
        finally:
            self._current_task = None
    
    def cancel_task(self, task: Task) -> bool:
        """
        Cancel a scheduled task
        
        Args:
            task: Task to cancel
        
        Returns:
            bool: True if task was cancelled
        """
        if task in self._queue:
            self._queue.remove(task)
            return True
        return False
    
    def flush_all(self) -> None:
        """Execute all pending tasks"""
        while self._queue:
            task = self._queue.pop(0)
            self._execute_task(task)
    
    def get_first_task(self) -> Optional[Task]:
        """Get the highest priority task without removing it"""
        return self._queue[0] if self._queue else None
    
    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return len(self._queue) == 0
    
    def get_pending_count(self) -> int:
        """Get number of pending tasks"""
        return len(self._queue)


class UpdateScheduler:
    """
    Scheduler specifically for component updates
    
    Manages batch updates and priorities for component re-renders.
    """
    
    def __init__(self):
        self._pending_updates: Dict[int, Any] = {}
        self._batch_depth: int = 0
        self._is_batching: bool = False
        self._scheduler = Scheduler()
    
    def schedule_update(
        self,
        component: Any,
        priority: Priority = Priority.NORMAL
    ) -> None:
        """
        Schedule a component update
        
        Args:
            component: Component to update
            priority: Update priority
        """
        component_id = id(component)
        self._pending_updates[component_id] = component
        
        if not self._is_batching:
            self._flush_updates()
    
    def batch_updates(self, callback: Callable) -> None:
        """
        Execute callback with batched updates
        
        Updates are not flushed until callback completes.
        
        Args:
            callback: Function to execute
        """
        self._is_batching = True
        self._batch_depth += 1
        
        try:
            callback()
        finally:
            self._batch_depth -= 1
            if self._batch_depth == 0:
                self._is_batching = False
                self._flush_updates()
    
    def _flush_updates(self) -> None:
        """Flush all pending updates"""
        updates = self._pending_updates.copy()
        self._pending_updates.clear()
        
        for component in updates.values():
            if hasattr(component, '_apply_state'):
                component._apply_state()
            if hasattr(component, 'render'):
                component.render()
    
    def defer_update(self, component: Any) -> None:
        """Defer an update to low priority"""
        self.schedule_update(component, Priority.LOW)
    
    def immediate_update(self, component: Any) -> None:
        """Execute an immediate update"""
        self.schedule_update(component, Priority.IMMEDIATE)


# Global scheduler instance
_scheduler = Scheduler()
_update_scheduler = UpdateScheduler()


def get_scheduler() -> Scheduler:
    """Get the global scheduler"""
    return _scheduler


def get_update_scheduler() -> UpdateScheduler:
    """Get the global update scheduler"""
    return _update_scheduler


def schedule_callback(callback: Callable, priority: Priority = Priority.NORMAL) -> Task:
    """Schedule a callback with the global scheduler"""
    return _scheduler.schedule_callback(callback, priority)


def batch_updates(callback: Callable) -> None:
    """Batch multiple updates together"""
    _update_scheduler.batch_updates(callback)
