# Paper Integration Guide

How to properly cite, document, and integrate ROSA into academic publications.

## Citation

### BibTeX Entry

```bibtex
@article{rosa2024,
  title={ROSA: Robot Operating System Agent for Natural Language Robotics},
  author={Royce, Rob and et al.},
  journal={arXiv preprint},
  year={2024},
  url={https://arxiv.org/abs/2410.06472},
  note={JPL Technical Report}
}
```

### APA Style

```
Royce, R., et al. (2024). ROSA: Robot Operating System Agent for 
Natural Language Robotics. arXiv preprint. 
https://arxiv.org/abs/2410.06472
```

### IEEE Style

```
R. Royce et al., "ROSA: Robot Operating System Agent for Natural 
Language Robotics," arXiv preprint, 2024. [Online]. Available: 
https://arxiv.org/abs/2410.06472
```

## Methods Section Template

### Describing ROSA in Methods

```markdown
## Natural Language Robot Interface

We used ROSA (v1.0.10) [1], an open-source LLM-based agent for ROS, 
to provide natural language interfaces for robot control. ROSA uses 
LangChain [2] to orchestrate tool calling, enabling the LLM to invoke 
ROS commands based on natural language queries.

### Configuration
- LLM: [Model name] (temperature=0 for deterministic responses)
- ROS Version: [1 or 2]
- Tools: [List of tools used]
- Custom Tools: [Description of custom tools]

### Integration
ROSA was integrated with the [robot name] platform through [method]. 
Custom tools were developed for [specific tasks] following the ROSA 
tool development patterns [1].

### Experimental Protocol
Participants interacted with the robot using natural language 
commands through ROSA. All interactions were logged for reproducibility 
analysis. The agent was configured with [specific prompts] for 
[experimental condition].
```

## Reproducibility Checklist

### Software Environment

- [ ] ROSA version documented
- [ ] Python version documented
- [ ] ROS distribution documented
- [ ] LLM model documented
- [ ] All dependencies listed
- [ ] Custom tools code available
- [ ] Configuration files included

### Experimental Setup

- [ ] Hardware specifications documented
- [ ] Sensor configurations documented
- [ ] Robot platform documented
- [ ] Environment description included
- [ ] Baseline conditions defined
- [ ] Experimental conditions defined

### Data Collection

- [ ] Data collection protocol documented
- [ ] Logging mechanisms described
- [ ] Data format specified
- [ ] Storage location documented
- [ ] Privacy considerations addressed

### Analysis

- [ ] Statistical methods documented
- [ ] Evaluation metrics defined
- [ ] Comparison methods described
- [ ] Significance thresholds stated

## Data Availability Statement Template

```markdown
## Data Availability

The data collected during this study is available at [repository URL]. 
The dataset includes:

- [Number] natural language queries
- [Number] agent responses
- [Number] participant interactions
- [Number] intermediate step traces
- System logs and configurations

Software:
- ROSA version: [version]
- LLM model: [model]
- ROS version: [version]
- Custom tools: [repository]

All code for reproducing the experiments is available at [code URL].
```

## Experiment Documentation

### Experiment Manifest

```python
{
  "experiment_id": "hri_study_2024_001",
  "title": "Natural Language Robot Control Study",
  "rosa_version": "1.0.10",
  "llm_model": "gpt-4",
  "llm_temperature": 0,
  "ros_version": 1,
  "ros_distribution": "noetic",
  "python_version": "3.9.0",
  "custom_tools": [
    "navigate_to",
    "grasp_object",
    "read_sensors"
  ],
  "prompts": {
    "embodiment": "Mobile manipulation robot",
    "constraints": "Max speed 0.5 m/s"
  },
  "participants": 20,
  "conditions": ["natural_language", "traditional_gui"],
  "start_date": "2024-01-15",
  "end_date": "2024-02-28"
}
```

## Publishing Guidelines

### Journals Suitable for ROSA Research

- **Robotics**: IEEE Transactions on Robotics, ICRA, IROS
- **AI**: AAAI, NeurIPS, ICML
- **HRI**: ACM/IEEE HRI Conference, THRI Journal
- **Software**: Journal of Open Source Software

### Conference Presentations

When presenting ROSA at conferences:

1. **Demonstrate Live**: Show real-time interaction
2. **Explain Architecture**: Highlight the tool-based design
3. **Show Extensibility**: Demonstrate custom tools
4. **Discuss Safety**: Emphasize built-in safety features
5. **Share Code**: Provide links to repositories

### Video Supplements

Consider creating:
- **Demo Videos**: 2-3 minute interaction demos
- **Tutorial Videos**: Setup and basic usage
- **Technical Videos**: Architecture explanation

## Licensing and Attribution

### ROSA License

ROSA is released under the Apache 2.0 License:

```
Copyright (c) 2024. Jet Propulsion Laboratory. All rights reserved.

Licensed under the Apache License, Version 2.0.
```

### Your Research Code

When publishing code that uses ROSA:

1. **Include ROSA License**: Reference Apache 2.0
2. **Acknowledge JPL**: "Developed at NASA Jet Propulsion Laboratory"
3. **Cite Paper**: Reference the arXiv preprint
4. **Share Improvements**: Consider contributing back

## Next Steps

- [Experiment Templates](experiment-templates.md)
- [Case Studies](case-studies.md)
- [Academic Resources](academic-resources.md)
- [Researcher Guide](../user-guides/researcher.md)
