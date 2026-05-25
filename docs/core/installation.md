# Installation & Setup

This guide covers all methods to install and configure ROSA for your environment.

## Prerequisites

- **Python**: 3.9 or higher, < 4.0
- **ROS**: Noetic (ROS1) or Humble/Iron/Jazzy (ROS2)
- **Operating System**: Linux (Ubuntu recommended), macOS, or Windows with WSL2

## Installation Methods

### Method 1: pip (Recommended)

```bash
pip3 install jpl-rosa
```

For optional LLM providers:
```bash
# Anthropic Claude support
pip3 install jpl-rosa[anthropic]

# Ollama local models
pip3 install jpl-rosa[ollama]

# All extras
pip3 install jpl-rosa[all]
```

### Method 2: From Source

```bash
git clone https://github.com/nasa-jpl/rosa.git
cd rosa
pip3 install -e .
```

### Method 3: Docker (For Demo)

```bash
docker pull ros:noetic-desktop
```

## ROS Environment Setup

### ROS1 (Noetic)

```bash
# Install ROS Noetic (Ubuntu 20.04)
sudo apt update
sudo apt install ros-noetic-desktop-full

# Source ROS environment
echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc
source ~/.bashrc

# Verify installation
roscore
```

### ROS2 (Humble)

```bash
# Install ROS2 Humble (Ubuntu 22.04)
sudo apt update
sudo apt install ros-humble-desktop

# Source ROS2 environment
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc

# Verify installation
ros2 doctor
```

## Verification Steps

After installation, verify ROSA is properly installed:

```python
# Verify import
python3 -c "from rosa import ROSA; print('ROSA installed successfully')"

# Check version
python3 -c "import rosa; print(rosa.__version__)"
```

## LLM Provider Setup

### OpenAI

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Anthropic

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Azure OpenAI

```bash
export AZURE_OPENAI_API_KEY="your-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
export AZURE_OPENAI_API_VERSION="2024-02-01"
```

### Ollama (Local)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3.1

# Verify
ollama list
```

## Common Installation Issues

### Issue: `pip install` fails with dependency conflicts

**Solution**: Use a virtual environment
```bash
python3 -m venv rosa-env
source rosa-env/bin/activate
pip install jpl-rosa
```

### Issue: ROS not found after installation

**Solution**: Source ROS environment
```bash
source /opt/ros/$ROS_DISTRO/setup.bash
```

### Issue: `ModuleNotFoundError: No module named 'rospy'`

**Solution**: Ensure ROS Python packages are in PYTHONPATH
```bash
export PYTHONPATH="/opt/ros/$ROS_DISTRO/lib/python3/dist-packages:$PYTHONPATH"
```

### Issue: tiktoken build fails (Rust dependency)

**Solution**: Install Rust
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
pip install --force-reinstall tiktoken
```

## Next Steps

- [Quick Start Tutorial](../tutorials/quick-start.md) - Get started in 15 minutes
- [Configuration Guide](configuration.md) - Configure ROSA for your setup
- [API Reference](api-reference.md) - Explore ROSA capabilities
