# Installation Issues

Common installation problems and solutions.

## Quick Diagnostics

Run these checks first:

```bash
# Check Python version
python3 --version  # Should be 3.9+

# Check pip
pip --version

# Check virtual environment
which python3
```

## Common Problems

### Problem: pip install fails

**Symptoms**:
```
ERROR: Could not find a version that satisfies the requirement jpl-rosa
```

**Solutions**:

1. **Update pip**:
```bash
pip install --upgrade pip
```

2. **Use Python 3.9+**:
```bash
python3.9 -m pip install jpl-rosa
```

3. **Check Python path**:
```bash
python3 -c "import sys; print(sys.executable)"
```

### Problem: Dependency conflicts

**Symptoms**:
```
ERROR: ResolutionImpossible
```

**Solutions**:

1. **Use fresh virtual environment**:
```bash
python3 -m venv rosa-fresh
source rosa-fresh/bin/activate
pip install jpl-rosa
```

2. **Install with no deps** (not recommended):
```bash
pip install jpl-rosa --no-deps
# Then manually install dependencies
```

### Problem: tiktoken build fails

**Symptoms**:
```
error: can't find Rust compiler
```

**Solutions**:

1. **Install Rust**:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

2. **Pre-built wheel**:
```bash
pip install tiktoken --only-binary :all:
```

### Problem: Permission denied

**Symptoms**:
```
PermissionError: [Errno 13] Permission denied
```

**Solutions**:

1. **Use user install**:
```bash
pip install --user jpl-rosa
```

2. **Fix permissions**:
```bash
sudo chown -R $USER:$USER ~/.local
```

### Problem: Import errors after installation

**Symptoms**:
```python
ModuleNotFoundError: No module named 'rosa'
```

**Solutions**:

1. **Verify installation**:
```bash
pip show jpl-rosa
```

2. **Check Python path**:
```python
import sys
print(sys.path)
```

3. **Reinstall**:
```bash
pip uninstall jpl-rosa
pip install jpl-rosa
```

## Docker Installation

### Problem: Docker not found

**Solution**:
```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Add user to docker group
sudo usermod -aG docker $USER
```

### Problem: Container won't start

**Solution**:
```bash
# Check Docker status
sudo systemctl status docker

# Start Docker
sudo systemctl start docker
```

## Environment Setup

### Problem: Can't find ROS packages

**Solution**:
```bash
# Source ROS environment
source /opt/ros/noetic/setup.bash  # ROS1
source /opt/ros/humble/setup.bash   # ROS2

# Verify
roscore  # ROS1
ros2 doctor  # ROS2
```

### Problem: Python can't find ROS modules

**Solution**:
```bash
# Add ROS to PYTHONPATH
export PYTHONPATH="/opt/ros/$ROS_DISTRO/lib/python3/dist-packages:$PYTHONPATH"

# Or source setup
source /opt/ros/$ROS_DISTRO/setup.bash
```

## Verification Checklist

After installation, verify:

- [ ] Python 3.9+ installed
- [ ] pip works
- [ ] ROS installed and sourced
- [ ] jpl-rosa installed
- [ ] Can import rosa
- [ ] LLM API key set (if using cloud models)
- [ ] Can create ROSA instance
- [ ] Basic query works

## Still Having Issues?

1. Check [GitHub Issues](https://github.com/nasa-jpl/rosa/issues)
2. Review [Installation Guide](../core/installation.md)
3. Ask in community forums

## Next Steps

- [ROS Connection Problems](ros-connection-problems.md)
- [LLM Provider Issues](llm-provider-issues.md)
- [Configuration Guide](../core/configuration.md)
