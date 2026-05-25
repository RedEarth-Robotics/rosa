# Experiment Templates

Standard templates for conducting research with ROSA.

## Template 1: Comparative Study

Compare ROSA against traditional interfaces.

```python
"""
Comparative Study Template
Compare natural language (ROSA) vs traditional GUI control
"""

from rosa import ROSA
from langchain_openai import ChatOpenAI
import json
import datetime

class ComparativeStudy:
    def __init__(self, num_participants=20):
        self.num_participants = num_participants
        self.results = {
            "natural_language": [],
            "traditional_gui": []
        }
    
    def run_trial(self, participant_id, condition, task):
        """Run a single trial.
        
        Args:
            participant_id: Unique participant identifier
            condition: "natural_language" or "traditional_gui"
            task: Task description
        """
        if condition == "natural_language":
            rosa = self._create_rosa_agent()
            start_time = datetime.datetime.now()
            
            # Participant uses natural language
            response = rosa.invoke(task)
            
            end_time = datetime.datetime.now()
            
            result = {
                "participant_id": participant_id,
                "condition": condition,
                "task": task,
                "response": response,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": (end_time - start_time).total_seconds()
            }
            
            self.results["natural_language"].append(result)
        
        else:
            # Traditional GUI control
            # Implement your GUI control measurement
            pass
    
    def _create_rosa_agent(self):
        """Create standardized ROSA agent."""
        llm = ChatOpenAI(model="gpt-4", temperature=0)
        return ROSA(ros_version=1, llm=llm)
    
    def export_results(self, filepath):
        """Export results to JSON."""
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)

# Usage
study = ComparativeStudy(num_participants=20)

# Run trials
for i in range(20):
    # Natural language condition
    study.run_trial(
        participant_id=f"p{i+1}",
        condition="natural_language",
        task="Navigate to the kitchen and pick up the red box"
    )
    
    # Traditional GUI condition
    study.run_trial(
        participant_id=f"p{i+1}",
        condition="traditional_gui",
        task="Navigate to the kitchen and pick up the red box"
    )

study.export_results("comparative_study.json")
```

## Template 2: A/B Testing LLMs

Compare different LLM providers.

```python
"""
LLM Comparison Template
A/B test different language models with ROSA
"""

from rosa import ROSA
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

class LLMComparisonStudy:
    def __init__(self):
        self.models = {
            "gpt4": ChatOpenAI(model="gpt-4", temperature=0),
            "claude": ChatAnthropic(model="claude-3-opus", temperature=0),
            "gpt35": ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        }
        self.results = {name: [] for name in self.models}
    
    def evaluate_model(self, model_name, llm, test_queries):
        """Evaluate a single model.
        
        Args:
            model_name: Identifier for the model
            llm: LangChain LLM instance
            test_queries: List of test queries
        """
        rosa = ROSA(ros_version=1, llm=llm, streaming=False)
        
        for query in test_queries:
            import time
            start = time.time()
            response = rosa.invoke(query)
            duration = time.time() - start
            
            result = {
                "model": model_name,
                "query": query,
                "response": response,
                "response_length": len(response),
                "duration_seconds": duration,
                "tools_used": self._extract_tools(response)
            }
            
            self.results[model_name].append(result)
    
    def run_comparison(self, test_queries):
        """Run comparison across all models."""
        for model_name, llm in self.models.items():
            print(f"Evaluating {model_name}...")
            self.evaluate_model(model_name, llm, test_queries)
    
    def _extract_tools(self, response):
        """Extract tool usage from response (simplified)."""
        # Implement based on your logging needs
        return []
    
    def generate_report(self):
        """Generate comparison report."""
        report = {}
        
        for model_name, results in self.results.items():
            total_duration = sum(r["duration_seconds"] for r in results)
            total_tokens = sum(r["response_length"] for r in results)
            
            report[model_name] = {
                "avg_duration": total_duration / len(results),
                "avg_response_length": total_tokens / len(results),
                "total_queries": len(results)
            }
        
        return report

# Standard test queries for robotics
test_queries = [
    "List all nodes and explain their functions",
    "Move the robot forward 2 meters and report position",
    "What topics have no subscribers and why?",
    "Check if the system is healthy",
    "Navigate to coordinates (5, 3) avoiding obstacles"
]

# Run comparison
study = LLMComparisonStudy()
study.run_comparison(test_queries)
report = study.generate_report()

print("Comparison Results:")
for model, metrics in report.items():
    print(f"\n{model}:")
    print(f"  Average duration: {metrics['avg_duration']:.2f}s")
    print(f"  Average response length: {metrics['avg_response_length']:.0f} chars")
```

## Template 3: Longitudinal Study

Track performance over time.

```python
"""
Longitudinal Study Template
Track ROSA performance over extended period
"""

from rosa import ROSA
from langchain_openai import ChatOpenAI
import datetime
import json

class LongitudinalStudy:
    def __init__(self, duration_days=30):
        self.duration_days = duration_days
        self.data = []
        self.start_date = datetime.datetime.now()
    
    def record_daily_session(self, queries, responses):
        """Record a daily interaction session.
        
        Args:
            queries: List of queries asked
            responses: List of responses received
        """
        session = {
            "date": datetime.datetime.now().isoformat(),
            "day": (datetime.datetime.now() - self.start_date).days,
            "num_queries": len(queries),
            "queries": queries,
            "responses": responses,
            "avg_response_length": sum(len(r) for r in responses) / len(responses)
        }
        
        self.data.append(session)
    
    def export_timeseries(self, filepath):
        """Export time series data."""
        with open(filepath, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def analyze_trends(self):
        """Analyze performance trends over time."""
        days = [d["day"] for d in self.data]
        query_counts = [d["num_queries"] for d in self.data]
        response_lengths = [d["avg_response_length"] for d in self.data]
        
        return {
            "total_sessions": len(self.data),
            "avg_queries_per_session": sum(query_counts) / len(query_counts),
            "response_length_trend": "increasing" if response_lengths[-1] > response_lengths[0] else "stable",
            "data": self.data
        }
```

## Template 4: Human-Robot Interaction

Study human-robot interaction using ROSA.

```python
"""
HRI Study Template
Human-Robot Interaction study framework
"""

from rosa import ROSA
from langchain_openai import ChatOpenAI

class HRIStudy:
    def __init__(self):
        self.rosa = ROSA(
            ros_version=1,
            llm=ChatOpenAI(model="gpt-4"),
            streaming=False
        )
        self.interactions = []
    
    def run_interaction(self, participant_id, task_list):
        """Run interaction session with a participant.
        
        Args:
            participant_id: Unique participant ID
            task_list: List of tasks to complete
        """
        session = {
            "participant_id": participant_id,
            "tasks": [],
            "satisfaction_score": None,
            "notes": ""
        }
        
        for task in task_list:
            print(f"\nTask: {task}")
            print("Participant, please describe what you want the robot to do:")
            
            # Participant gives natural language command
            query = input("> ")
            
            # Execute through ROSA
            response = self.rosa.invoke(query)
            
            task_result = {
                "task": task,
                "query": query,
                "response": response,
                "success": self._evaluate_success(task, response)
            }
            
            session["tasks"].append(task_result)
            print(f"Response: {response}")
        
        # Collect satisfaction score
        session["satisfaction_score"] = self._collect_satisfaction()
        
        self.interactions.append(session)
        return session
    
    def _evaluate_success(self, task, response):
        """Evaluate if task was completed successfully."""
        # Implement your evaluation criteria
        return "success" in response.lower() or "completed" in response.lower()
    
    def _collect_satisfaction(self):
        """Collect satisfaction score from participant."""
        while True:
            try:
                score = int(input("Satisfaction (1-5): "))
                if 1 <= score <= 5:
                    return score
            except ValueError:
                pass
            print("Please enter a number between 1 and 5")

# Usage
study = HRIStudy()

tasks = [
    "Move the robot to the kitchen",
    "Pick up the red box",
    "Return to the starting position",
    "Describe the current environment"
]

# Run with multiple participants
for i in range(5):
    print(f"\n{'='*50}")
    print(f"Participant {i+1}")
    print(f"{'='*50}")
    study.run_interaction(f"p{i+1}", tasks)
```

## Next Steps

- [Case Studies](case-studies.md) - Published research using ROSA
- [Paper Integration Guide](paper-integration.md) - Citation and documentation
- [Academic Resources](academic-resources.md) - Additional resources
