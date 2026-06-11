#!/bin/bash
# 🛠️ AppleScript Launcher Compiler for OmniDrive
# Compiles AppleScript source into a native macOS app bundle.

APP_PATH="/Users/jack/Applications/OmniDrive.app"
TEMP_AS="/tmp/omnidrive_launcher.applescript"

echo "🎨 Preparing AppleScript source code..."

cat << 'EOF' > "$TEMP_AS"
try
	do shell script "hdiutil attach ~/OmniDrive_System/OmniDrive_Jack.sparsebundle.sparseimage > /dev/null 2>&1"
end try
delay 0.5
tell application "Finder"
	if exists POSIX file "/Volumes/OmniDrive" then
		open POSIX file "/Volumes/OmniDrive"
		activate
	end if
end tell
EOF

echo "⚙️  Compiling launcher applet using osacompile..."
mkdir -p "$(dirname "$APP_PATH")"

# Remove existing app bundle if it exists
if [ -d "$APP_PATH" ]; then
    rm -rf "$APP_PATH"
fi

osacompile -o "$APP_PATH" "$TEMP_AS"

if [ $? -eq 0 ]; then
    echo "✅ Launcher compiled successfully at: $APP_PATH"
    echo "🚀 You can launch it using 'open $APP_PATH' or find it on your Desktop/Applications!"
else
    echo "❌ Error: Failed to compile AppleScript launcher."
fi

# Clean up temp file
rm -f "$TEMP_AS"
