#!/bin/bash

PLUGIN_DIR="$HOME/Documents/SwiftBar_Plugins"
PYTHON_SCRIPT="agy_usage.30s.py"
BASH_SCRIPT="get_agy_usage.sh"

echo "🗑️ Removing SwiftBar widget..."

# Remove symlinks
rm -f "$PLUGIN_DIR/$PYTHON_SCRIPT"
rm -f "$PLUGIN_DIR/$BASH_SCRIPT"

# Refresh SwiftBar plugins to apply changes without restarting
open "swiftbar://refreshallplugins" 2>/dev/null

echo "✅ Widget removed successfully."
