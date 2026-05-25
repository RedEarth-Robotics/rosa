# Advanced Agent Customization Tutorial

Learn to create production-ready custom agents with advanced features.

## Learning Objectives

- Extend the ROSA class for specialized robots
- Implement custom prompts and safety systems
- Configure streaming and non-streaming modes
- Deploy agents in production environments

**Time**: 90 minutes  
**Prerequisites**: Custom Tool Development Tutorial, Python proficiency

## Part 1: Custom Agent Class (25 minutes)

### Exercise 1.1: Basic Custom Agent

Create `warehouse_agent.py`:

```python
from rosa import ROSA
from rosa.prompts import RobotSystemPrompts
from langchain.agents import tool
from langchain_openai import ChatOpenAI

class WarehouseRobotAgent(ROSA):
    """Specialized agent for warehouse automation robots.
    
    Features:
    - Zone-based navigation
    - Pallet handling
    - Safety compliance
    - Inventory tracking
    """
    
    def __init__(self, streaming: bool = False, verbose: bool = True):
        # Robot-specific configuration
        self.__blacklist = [
            "emergency_stop",
            "motor_override",
            "delete_param",
            "shutdown"
        ]
        
        # Custom prompts
        self.__prompts = RobotSystemPrompts(
            embodiment_and_persona=(
                "You are a warehouse AGV (Automated Guided Vehicle) "
                "with lifting capabilities. You operate in a "
                "structured warehouse environment."
            ),
            about_your_operators=(
                "You work alongside warehouse staff and supervisors. "
                "Follow their instructions precisely and report status clearly."
            ),
            critical_instructions=(
                "1. Always check for obstacles before moving\n"
                "2. Never exceed maximum speed of 1.5 m/s\n"
                "3. Require confirmation for destructive operations\n"
                "4. Report any anomalies immediately"
            ),
            constraints_and_guardrails=(
                "- Maximum payload: 500kg\n"
                "- Operating hours: 6 AM - 10 PM\n"
                "- No entry into restricted zones without authorization\n"
                "- Always maintain safe distance from humans (2m minimum)"
            ),
            about_your_environment=(
                "Indoor warehouse with 5 zones (A-E), each with "
                "shelves, loading docks, and charging stations. "
                "Floor is marked with QR codes for navigation."
            ),
            about_your_capabilities=(
                "- Navigate between warehouse zones\n"
                "- Lift and transport pallets up to 500kg\n"
                "- Scan QR codes for position verification\n"
                "- Communicate with warehouse management system\n"
                "- Autonomous charging when battery < 20%"
            ),
            mission_and_objectives=(
                "Transport materials between zones efficiently "
                "while maintaining safety standards. Optimize "
                "routes to minimize travel time and energy consumption."
            )
        )
        
        # Initialize LLM
        self.__llm = ChatOpenAI(
            model="gpt-4",
            temperature=0
        )
        
        # Initialize ROSA with custom configuration
        super().__init__(
            ros_version=1,
            llm=self.__llm,
            tools=self._get_warehouse_tools(),
            prompts=self.__prompts,
            blacklist=self.__blacklist,
            verbose=verbose,
            streaming=streaming,
            accumulate_chat_history=True,
            max_iterations=50
        )
    
    def _get_warehouse_tools(self):
        """Create warehouse-specific tools."""
        return [
            self._create_navigate_to_zone_tool(),
            self._create_lift_pallet_tool(),
            self._create_drop_pallet_tool(),
            self._create_check_inventory_tool(),
            self._create_scan_qr_tool()
        ]
    
    def _create_navigate_to_zone_tool(self):
        @tool
        def navigate_to_zone(zone: str) -> str:
            """Navigate to a warehouse zone.
            
            Args:
                zone: Target zone (A, B, C, D, or E)
            
            Returns:
                Navigation status
            """
            valid_zones = ["A", "B", "C", "D", "E"]
            if zone not in valid_zones:
                return f"Invalid zone '{zone}'. Valid zones: {', '.join(valid_zones)}"
            
            # Implementation
            return f"Navigating to Zone {zone}..."
        
        return navigate_to_zone
    
    def _create_lift_pallet_tool(self):
        @tool
        def lift_pallet(pallet_id: str, weight: float) -> str:
            """Lift a pallet from the ground.
            
            Args:
                pallet_id: Unique identifier for the pallet
                weight: Weight of the pallet in kg (must be < 500)
            
            Returns:
                Lift operation status
            """
            if weight > 500:
                return f"Error: Weight {weight}kg exceeds maximum 500kg"
            
            return f"Lifting pallet {pallet_id} ({weight}kg)..."
        
        return lift_pallet
    
    def _create_drop_pallet_tool(self):
        @tool
        def drop_pallet(pallet_id: str, zone: str) -> str:
            """Drop a pallet in a zone.
            
            Args:
                pallet_id: Pallet to drop
                zone: Target zone
            
            Returns:
                Drop operation status
            """
            return f"Dropping pallet {pallet_id} in Zone {zone}..."
        
        return drop_pallet
    
    def _create_check_inventory_tool(self):
        @tool
        def check_inventory(zone: str = None) -> dict:
            """Check warehouse inventory.
            
            Args:
                zone: Specific zone to check, or None for all zones
            
            Returns:
                Inventory status
            """
            if zone:
                return {"zone": zone, "items": 42, "status": "active"}
            return {"total_items": 150, "zones": 5, "status": "operational"}
        
        return check_inventory
    
    def _create_scan_qr_tool(self):
        @tool
        def scan_qr() -> str:
            """Scan QR code at current position."""
            return "QR scan: Position verified"
        
        return scan_qr
    
    def get_system_status(self) -> dict:
        """Get comprehensive warehouse robot status."""
        return {
            "battery": 85,
            "current_zone": "B",
            "current_load": 0,
            "status": "operational",
            "mode": "autonomous"
        }
```

### Exercise 1.2: Context-Aware Agent

```python
class ContextAwareAgent(ROSA):
    """Agent that changes behavior based on context."""
    
    def __init__(self):
        super().__init__(
            ros_version=1,
            llm=ChatOpenAI(model="gpt-4"),
            streaming=True
        )
        self.operation_mode = "normal"
        self.authorized_users = ["admin", "supervisor"]
    
    def set_mode(self, mode: str):
        """Change operation mode."""
        valid_modes = ["normal", "maintenance", "emergency", "training"]
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode. Choose from: {valid_modes}")
        
        self.operation_mode = mode
        
        # Update prompts based on mode
        if mode == "maintenance":
            self._enable_maintenance_mode()
        elif mode == "emergency":
            self._enable_emergency_mode()
        elif mode == "training":
            self._enable_training_mode()
    
    def _enable_maintenance_mode(self):
        """Enable diagnostic tools, disable movement."""
        self.__prompts = RobotSystemPrompts(
            critical_instructions="Maintenance mode: Diagnostic tools only"
        )
        # Update available tools
        self._update_tool_access(movement=False, diagnostics=True)
    
    def _enable_emergency_mode(self):
        """Only allow emergency tools."""
        self.__prompts = RobotSystemPrompts(
            critical_instructions="Emergency mode: Safety tools only"
        )
        self._update_tool_access(movement=False, diagnostics=False, emergency=True)
    
    def _enable_training_mode(self):
        """Enable all tools with explanations."""
        self.__prompts = RobotSystemPrompts(
            critical_instructions="Training mode: Explain all actions"
        )
        self._update_tool_access(all_tools=True)
    
    def _update_tool_access(self, **kwargs):
        """Update which tools are available."""
        # Implementation
        pass
```

## Part 2: Streaming and Real-Time (20 minutes)

### Exercise 2.1: Streaming Agent

```python
import asyncio
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live

class StreamingRobotAgent(ROSA):
    """Agent with rich streaming output."""
    
    def __init__(self):
        super().__init__(
            ros_version=1,
            llm=ChatOpenAI(model="gpt-4"),
            streaming=True
        )
        self.console = Console()
    
    async def run_interactive(self):
        """Run interactive streaming session."""
        self.console.print(Panel(
            "[bold blue]Robot Agent Ready[/bold blue]",
            subtitle="Type 'exit' to quit"
        ))
        
        while True:
            query = input("\n> ")
            if query.lower() == 'exit':
                break
            
            await self._stream_query(query)
    
    async def _stream_query(self, query: str):
        """Stream query with rich formatting."""
        content = ""
        
        try:
            with Live(
                Panel("", title="Response", border_style="green"),
                console=self.console,
                auto_refresh=False
            ) as live:
                async for event in self.astream(query):
                    if event["type"] == "token":
                        content += event["content"]
                        live.update(
                            Panel(Markdown(content), title="Response", border_style="green"),
                            refresh=True
                        )
                    elif event["type"] == "tool_start":
                        self.console.print(
                            f"[dim]→ Using tool: {event['name']}[/dim]"
                        )
                    elif event["type"] == "tool_end":
                        self.console.print(
                            f"[dim]← Tool result: {event['output'][:50]}...[/dim]"
                        )
        
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Interrupted[/yellow]")
```

### Exercise 2.2: Event Logging

```python
class EventLoggingAgent(ROSA):
    """Agent with comprehensive event logging."""
    
    def __init__(self):
        super().__init__(
            ros_version=1,
            llm=ChatOpenAI(model="gpt-4"),
            return_intermediate_steps=True
        )
        self.event_log = []
    
    async def invoke_with_logging(self, query: str) -> dict:
        """Execute with full event logging."""
        import datetime
        
        start_time = datetime.datetime.now()
        events = []
        
        async for event in self.astream(query):
            event["timestamp"] = datetime.datetime.now().isoformat()
            events.append(event)
        
        end_time = datetime.datetime.now()
        
        log_entry = {
            "query": query,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_ms": (end_time - start_time).total_seconds() * 1000,
            "events": events
        }
        
        self.event_log.append(log_entry)
        return log_entry
    
    def export_events(self, filepath: str):
        """Export event log to file."""
        import json
        with open(filepath, 'w') as f:
            json.dump(self.event_log, f, indent=2)
```

## Part 3: Production Configuration (25 minutes)

### Exercise 3.1: Production Agent

```python
class ProductionRobotAgent(ROSA):
    """Production-ready robot agent with monitoring and safety."""
    
    def __init__(self):
        # Production LLM configuration
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,
            max_retries=5,
            request_timeout=30
        )
        
        # Production prompts
        prompts = RobotSystemPrompts(
            embodiment_and_persona="Production warehouse robot",
            critical_instructions=(
                "1. Log all actions\n"
                "2. Require confirmation for destructive operations\n"
                "3. Report errors immediately\n"
                "4. Maintain audit trail"
            ),
            constraints_and_guardrails=(
                "- Max speed: 1.5 m/s\n"
                "- Max payload: 500kg\n"
                "- Operating hours only\n"
                "- Safety zones enforced"
            )
        )
        
        super().__init__(
            ros_version=1,
            llm=llm,
            prompts=prompts,
            blacklist=[
                "emergency_stop",
                "motor_kill",
                "override_safety",
                "delete_param",
                "shutdown",
                "reboot"
            ],
            streaming=False,  # Better for production
            verbose=False,     # Clean logs
            accumulate_chat_history=False,  # Stateless
            max_iterations=30,
            return_intermediate_steps=False
        )
        
        # Production monitoring
        self.action_count = 0
        self.error_count = 0
    
    def invoke(self, query: str) -> str:
        """Override to add production monitoring."""
        try:
            self.action_count += 1
            
            # Log action
            self._log_action(query)
            
            # Execute
            result = super().invoke(query)
            
            # Log result
            self._log_result(result)
            
            return result
            
        except Exception as e:
            self.error_count += 1
            self._log_error(e)
            return f"Error: {str(e)}"
    
    def _log_action(self, query: str):
        """Log incoming action."""
        import logging
        logging.info(f"Action {self.action_count}: {query}")
    
    def _log_result(self, result: str):
        """Log action result."""
        import logging
        logging.info(f"Result: {result[:100]}...")
    
    def _log_error(self, error: Exception):
        """Log error."""
        import logging
        logging.error(f"Error: {str(error)}")
    
    def get_stats(self) -> dict:
        """Get production statistics."""
        return {
            "total_actions": self.action_count,
            "total_errors": self.error_count,
            "error_rate": self.error_count / max(self.action_count, 1),
            "uptime": "calculated"
        }
```

### Exercise 3.2: Safety System

```python
class SafetyEnhancedAgent(ROSA):
    """Agent with comprehensive safety system."""
    
    def __init__(self):
        super().__init__(
            ros_version=1,
            llm=ChatOpenAI(model="gpt-4"),
            blacklist=["emergency_stop"]
        )
        self.safety_checks = []
        self.emergency_contacts = []
    
    def add_safety_check(self, check_func):
        """Add a safety check function."""
        self.safety_checks.append(check_func)
    
    def check_safety(self, query: str, response: str) -> bool:
        """Run all safety checks."""
        for check in self.safety_checks:
            if not check(query, response):
                return False
        return True
    
    def invoke(self, query: str) -> str:
        """Override to add safety checks."""
        response = super().invoke(query)
        
        if not self.check_safety(query, response):
            return "Safety check failed. Operation aborted."
        
        return response
```

## Part 4: Testing and Validation (20 minutes)

### Exercise 4.1: Agent Testing

```python
import unittest
from warehouse_agent import WarehouseRobotAgent

class TestWarehouseAgent(unittest.TestCase):
    def setUp(self):
        self.agent = WarehouseRobotAgent()
    
    def test_basic_query(self):
        response = self.agent.invoke("What is your status?")
        self.assertIsNotNone(response)
        self.assertIsInstance(response, str)
    
    def test_zone_navigation(self):
        response = self.agent.invoke("Navigate to Zone A")
        self.assertIn("Zone A", response)
    
    def test_safety_limit(self):
        response = self.agent.invoke("Lift pallet weighing 600kg")
        self.assertIn("Error", response) or self.assertIn("exceeds", response)
    
    def test_system_status(self):
        status = self.agent.get_system_status()
        self.assertIn("battery", status)
        self.assertIn("status", status)

if __name__ == '__main__':
    unittest.main()
```

## What's Next?

- **Researcher Guide** - Academic and research applications
- **Code Examples** - Practical implementations
- **Troubleshooting** - Production issues

## Summary

In this tutorial, you:
- ✅ Created custom agent classes
- ✅ Implemented context-aware behavior
- ✅ Added streaming and real-time features
- ✅ Configured production-ready agents
- ✅ Built comprehensive safety systems
- ✅ Wrote agent tests

**Key Takeaways**:
- Extend ROSA class for specialized robots
- Use RobotSystemPrompts for behavior customization
- Implement safety checks at multiple levels
- Monitor and log all operations in production
- Test agents thoroughly before deployment
