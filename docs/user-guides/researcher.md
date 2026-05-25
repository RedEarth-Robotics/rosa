# Researcher Guide

This guide is designed for academic researchers and scientists using ROSA in research projects, experiments, and publications.

## Learning Objectives

By the end of this guide, you will:
- Understand how to use ROSA for research applications
- Know how to design reproducible experiments with ROSA
- Be able to properly cite and document ROSA in publications
- Understand advanced features for research use cases

**Estimated Time**: 60 minutes  
**Prerequisites**: Research background, ROS experience, ROSA installed

## ROSA for Research

### Research Applications

ROSA is particularly useful for research in:

- **Human-Robot Interaction (HRI)**: Natural language interfaces for robot control
- **Cognitive Robotics**: LLM reasoning in robotic systems
- **Explainable AI**: Transparent decision-making in robot agents
- **Robot Learning**: Language-guided skill acquisition
- **Multi-modal Systems**: Integration of language, vision, and action

### Why Use ROSA in Research?

1. **Natural Language Interface**: Enables non-technical participants to interact with robots
2. **Reproducible Interactions**: Consistent tool execution across experiments
3. **Explainable Actions**: Agent reasoning visible through intermediate steps
4. **Easy Customization**: Adapt to specific research scenarios
5. **Open Source**: Transparent, auditable, and extensible

## Experiment Design

### Standard Experiment Setup

```python
from rosa import ROSA
from rosa.prompts import RobotSystemPrompts
import json
import datetime

class ResearchROSA(ROSA):
    """ROSA configured for research use."""
    
    def __init__(self, condition: str = "control"):
        self.condition = condition
        self.experiment_id = datetime.datetime.now().isoformat()
        
        prompts = RobotSystemPrompts(
            embodiment_and_persona="Research robot platform",
            mission_and_objectives="Assist with research tasks accurately",
            environment_variables={"condition": condition, "experiment_id": self.experiment_id}
        )
        
        super().__init__(
            ros_version=1,
            llm=get_llm(),
            prompts=prompts,
            streaming=False,  # Consistent for experiments
            return_intermediate_steps=True,  # Full traceability
            accumulate_chat_history=False  # Independent trials
        )
        
        self.results_log = []
    
    def invoke_with_logging(self, query: str, participant_id: str = None) -> dict:
        """Execute query with full logging for research."""
        start_time = datetime.datetime.now()
        
        response = self.invoke(query)
        
        end_time = datetime.datetime.now()
        
        log_entry = {
            "experiment_id": self.experiment_id,
            "participant_id": participant_id,
            "condition": self.condition,
            "query": query,
            "response": response,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_ms": (end_time - start_time).total_seconds() * 1000,
            "chat_history_length": len(self.chat_history),
        }
        
        self.results_log.append(log_entry)
        return log_entry
```

### A/B Testing Different LLMs

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# Define experimental conditions
conditions = {
    "gpt4": ChatOpenAI(model="gpt-4", temperature=0),
    "claude": ChatAnthropic(model="claude-3-opus", temperature=0),
    "gpt3": ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
}

# Run experiments
results = {}
for condition_name, llm in conditions.items():
    rosa = ROSA(ros_version=1, llm=llm)
    
    # Standardized test queries
    test_queries = [
        "List all nodes and explain their functions",
        "What topics have no subscribers?",
        "Check if the system is healthy"
    ]
    
    condition_results = []
    for query in test_queries:
        response = rosa.invoke(query)
        condition_results.append({
            "query": query,
            "response": response
        })
    
    results[condition_name] = condition_results

# Compare results
for condition, condition_results in results.items():
    print(f"\n=== {condition} ===")
    for r in condition_results:
        print(f"Query: {r['query'][:50]}...")
        print(f"Response length: {len(r['response'])}")
```

### Data Collection Protocol

```python
class ExperimentDataCollector:
    """Standardized data collection for ROSA experiments."""
    
    def __init__(self, experiment_name: str):
        self.experiment_name = experiment_name
        self.data = {
            "metadata": {
                "experiment_name": experiment_name,
                "start_time": datetime.datetime.now().isoformat(),
                "rosa_version": "1.0.10",
            },
            "trials": []
        }
    
    def record_trial(self, trial_data: dict):
        """Record a single trial."""
        trial_data["timestamp"] = datetime.datetime.now().isoformat()
        self.data["trials"].append(trial_data)
    
    def export(self, filepath: str):
        """Export experiment data to JSON."""
        with open(filepath, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_summary(self) -> dict:
        """Get experiment summary statistics."""
        return {
            "total_trials": len(self.data["trials"]),
            "experiment_duration": (
                datetime.datetime.now() - 
                datetime.datetime.fromisoformat(self.data["metadata"]["start_time"])
            ).total_seconds()
        }

# Usage
collector = ExperimentDataCollector("hri_study_2024")
rosa = ROSA(ros_version=1, llm=llm)

# Run trials
for i in range(10):
    response = rosa.invoke(f"Task {i}: Describe the current robot state")
    collector.record_trial({
        "trial_number": i,
        "query": f"Task {i}",
        "response": response,
        "success": len(response) > 0
    })

# Export
collector.export("experiment_data.json")
print(collector.get_summary())
```

## Paper Integration

### Citing ROSA

When using ROSA in research, cite the original paper:

```bibtex
@article{rosa2024,
  title={ROSA: Robot Operating System Agent for Natural Language Robotics},
  author={Royce, Rob and et al.},
  journal={arXiv preprint},
  year={2024},
  url={https://arxiv.org/abs/2410.06472}
}
```

### Describing ROSA Methodology

**Example for methods section**:

```
We used ROSA (v1.0.10), an open-source LLM-based agent for ROS, 
to provide natural language interfaces for robot control. ROSA 
uses LangChain to orchestrate tool calling, enabling the LLM to 
invoke ROS commands based on natural language queries. For our 
experiments, we used [LLM model] with temperature=0 for 
deterministic responses. Custom tools were developed for 
[specific tasks], following the ROSA tool development patterns. 
All interactions were logged for reproducibility analysis.
```

### Reproducible Research Practices

```python
import os
import hashlib

def create_experiment_manifest(
    rosa_version: str,
    llm_model: str,
    ros_version: int,
    tools_used: List[str],
    custom_tools_hash: str = None
) -> dict:
    """Create reproducibility manifest."""
    
    # Get environment hash
    env_vars = {k: v for k, v in os.environ.items() 
                if k.startswith(('ROS', 'OPENAI', 'ANTHROPIC'))}
    env_hash = hashlib.md5(str(env_vars).encode()).hexdigest()
    
    return {
        "rosa_version": rosa_version,
        "llm_model": llm_model,
        "ros_version": ros_version,
        "tools_used": tools_used,
        "custom_tools_hash": custom_tools_hash,
        "environment_hash": env_hash,
        "python_version": os.sys.version
    }

# Usage
manifest = create_experiment_manifest(
    rosa_version="1.0.10",
    llm_model="gpt-4",
    ros_version=1,
    tools_used=["rostopic_list", "rosnode_info", "custom_nav_tool"]
)

with open("experiment_manifest.json", 'w') as f:
    json.dump(manifest, f, indent=2)
```

## Advanced Features for Research

### Custom Evaluation Metrics

```python
class ROSEvaluator:
    """Evaluate ROSA responses for research."""
    
    def evaluate_correctness(self, query: str, response: str, ground_truth: str) -> float:
        """Evaluate response correctness against ground truth."""
        # Implement domain-specific evaluation
        pass
    
    def evaluate_safety(self, response: str) -> dict:
        """Evaluate safety of proposed actions."""
        safety_checks = {
            "no_emergency_commands": "emergency" not in response.lower(),
            "explanations_present": "because" in response.lower() or "to" in response.lower(),
            "warnings_included": "warning" in response.lower() or "caution" in response.lower()
        }
        return safety_checks
    
    def evaluate_efficiency(self, response: str, tools_used: List[str]) -> dict:
        """Evaluate response efficiency."""
        return {
            "tools_used": len(tools_used),
            "response_length": len(response),
            "avg_tool_efficiency": len(response) / max(len(tools_used), 1)
        }
```

### Human-Robot Interaction Studies

```python
class HRIStudy:
    """Framework for HRI studies using ROSA."""
    
    def __init__(self, rosa: ROSA):
        self.rosa = rosa
        self.interaction_log = []
    
    def participant_task(self, task_description: str, participant_id: str):
        """Execute a participant task and collect metrics."""
        
        print(f"Task: {task_description}")
        print("You can ask the robot anything in natural language.")
        print("Type 'done' when finished.")
        
        while True:
            query = input("> ")
            if query.lower() == 'done':
                break
            
            start = time.time()
            response = self.rosa.invoke(query)
            duration = time.time() - start
            
            self.interaction_log.append({
                "participant_id": participant_id,
                "query": query,
                "response": response,
                "duration": duration,
                "timestamp": datetime.datetime.now().isoformat()
            })
            
            print(response)
        
        return self.interaction_log
```

## Case Studies

### Example 1: Multi-Robot Coordination Study

```python
# Study: Natural language coordination of multiple robots

class MultiRobotStudy:
    def __init__(self, num_robots: int = 3):
        self.robots = {}
        for i in range(num_robots):
            # Each robot gets its own ROSA instance
            self.robots[f"robot_{i}"] = ROSA(
                ros_version=1,
                llm=llm,
                prompts=RobotSystemPrompts(
                    embodiment_and_persona=f"Robot {i} in multi-robot team",
                    mission_and_objectives="Coordinate with team members"
                )
            )
    
    def coordinate_task(self, task: str):
        """Coordinate multiple robots for a task."""
        results = {}
        for name, rosa in self.robots.items():
            response = rosa.invoke(f"{name}: {task}")
            results[name] = response
        return results
```

### Example 2: Explainable AI Experiment

```python
# Study: Comparing explainable vs non-explainable agent responses

class ExplainabilityStudy:
    def __init__(self):
        # Explainable condition: verbose with reasoning
        self.explainable_rosa = ROSA(
            ros_version=1,
            llm=llm,
            verbose=True,
            prompts=RobotSystemPrompts(
                critical_instructions="Always explain your reasoning before taking action"
            )
        )
        
        # Non-explainable condition: direct responses
        self.direct_rosa = ROSA(
            ros_version=1,
            llm=llm,
            verbose=False,
            prompts=RobotSystemPrompts(
                critical_instructions="Respond directly without explanations"
            )
        )
    
    def run_comparison(self, queries: List[str]):
        results = {
            "explainable": [],
            "direct": []
        }
        
        for query in queries:
            results["explainable"].append(
                self.explainable_rosa.invoke(query)
            )
            results["direct"].append(
                self.direct_rosa.invoke(query)
            )
        
        return results
```

## Data Availability

When publishing research using ROSA:

```python
def prepare_data_availability_statement(experiment_data: dict) -> str:
    """Generate data availability statement."""
    
    return f"""
    Data Availability Statement
    
    All data collected during this study is available at:
    [Repository URL]
    
    The dataset includes:
    - {experiment_data['num_queries']} natural language queries
    - {experiment_data['num_responses']} agent responses
    - {experiment_data['num_participants']} participants
    - Intermediate step traces for {experiment_data['num_traces']} interactions
    
    ROSA version: {experiment_data['rosa_version']}
    LLM model: {experiment_data['llm_model']}
    ROS version: {experiment_data['ros_version']}
    
    Custom tools and experiment code are available at:
    [Code Repository URL]
    """
```

## Next Steps

- [Research Hub](../research/) - Templates, case studies, and academic resources
- [Advanced Agent Customization Tutorial](../tutorials/advanced-agent-customization.md) - Production agents
- [Paper Integration Guide](../research/paper-integration.md) - Detailed citation and documentation
