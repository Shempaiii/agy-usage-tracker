#!/bin/bash

# Configuration
PLUGIN_DIR="$HOME/Documents/SwiftBar_Plugins"
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="agy_usage.30s.py"
BASH_SCRIPT="get_agy_usage.sh"

echo "🚀 Starting SwiftBar and Agy Widget Setup..."

# 1. Install SwiftBar if not installed
if ! osascript -e 'id of application "SwiftBar"' &> /dev/null; then
    echo "📦 SwiftBar is not installed. Attempting to install via Homebrew..."
    if command -v brew &> /dev/null; then
        brew install --cask swiftbar
    else
        echo "❌ Homebrew is not installed. Please install Homebrew or manually download SwiftBar."
        exit 1
    fi
else
    echo "✅ SwiftBar is already installed."
fi

# 2. Create Plugin Directory
if [ ! -d "$PLUGIN_DIR" ]; then
    echo "📁 Creating SwiftBar plugins directory at $PLUGIN_DIR"
    mkdir -p "$PLUGIN_DIR"
else
    echo "✅ Plugin directory already exists at $PLUGIN_DIR"
fi

# 3. Configure SwiftBar to use this directory
echo "⚙️ Configuring SwiftBar to use the plugin directory..."
killall SwiftBar 2>/dev/null
sleep 1
defaults write com.ameba.SwiftBar PluginDirectory -string "$PLUGIN_DIR"

# 4. Create an auto-cleaning proxy script in the Plugin Directory
echo "📋 Creating proxy script in $PLUGIN_DIR..."

PROXY_SCRIPT="$PLUGIN_DIR/agy_usage.30s.sh"

# Remove old python symlink if it exists
rm -f "$PLUGIN_DIR/$PYTHON_SCRIPT"

cat << EOF > "$PROXY_SCRIPT"
#!/bin/bash
ORIGINAL_SCRIPT="$CURRENT_DIR/$PYTHON_SCRIPT"

if [ -f "\$ORIGINAL_SCRIPT" ]; then
    exec "\$ORIGINAL_SCRIPT"
else
    # The brew formula was uninstalled, clean up and refresh
    rm -f "\$0"
    open "swiftbar://refreshallplugins" 2>/dev/null
fi
EOF

# Make sure proxy script is executable
chmod +x "$PROXY_SCRIPT"

# 5. Configure Auto-Start and Open SwiftBar
echo "🔄 Configuring SwiftBar to start at login..."
osascript -e 'tell application "System Events" to make login item at end with properties {path:"/Applications/SwiftBar.app", hidden:false}' 2>/dev/null || true

echo "🔄 Starting SwiftBar..."
open -a SwiftBar

echo "============================================================"
echo "⚠️  IMPORTANT: macOS Security Popup"
echo "If SwiftBar prompts you to 'Set SwiftBar Plugins Location',"
echo "you MUST click 'OK' and select the SwiftBar_Plugins folder."
echo "This is required by macOS security so SwiftBar can read it."
echo "============================================================"
echo ""
echo "🎉 Setup complete! The widget should now appear in your menu bar."
