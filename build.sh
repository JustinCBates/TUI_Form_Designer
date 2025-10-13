#!/bin/bash
# Build script for TUI Form Designer packages

set -e

echo "🏗️  Building TUI Form Designer Packages"
echo "======================================="

# Clean any existing builds
rm -rf dist/ build/ *.egg-info/

# Function to build a package
build_package() {
    local package_name=$1
    local config_file=$2
    local readme_file=$3
    
    echo ""
    echo "📦 Building $package_name..."
    echo "Using config: $config_file"
    echo "Using README: $readme_file"
    
    # Copy the specific README for this package
    cp "$readme_file" README.md
    
    # Build using the specific config
    python -m build --config-setting build-frontend=build-mode=$package_name -C--global-option=--config-settings="tool.hatch.build.targets.wheel.sources=[\"$config_file\"]"
    
    echo "✅ $package_name built successfully"
}

# Build engine package (production runtime)
echo ""
echo "🔧 Building TUI Form Engine (Production Runtime)"
cp pyproject-engine.toml pyproject.toml
cp README-engine.md README.md
python -m build
mv dist/tui_form_engine*.whl dist/engine/ 2>/dev/null || mkdir -p dist/engine && mv dist/tui_form_engine*.whl dist/engine/
mv dist/tui_form_engine*.tar.gz dist/engine/ 2>/dev/null || mv dist/tui_form_engine*.tar.gz dist/engine/

# Build editor package (development tools)  
echo ""
echo "🎨 Building TUI Form Editor (Development Tools)"
cp pyproject-editor.toml pyproject.toml
cp README-editor.md README.md
python -m build
mv dist/tui_form_editor*.whl dist/editor/ 2>/dev/null || mkdir -p dist/editor && mv dist/tui_form_editor*.whl dist/editor/
mv dist/tui_form_editor*.tar.gz dist/editor/ 2>/dev/null || mv dist/tui_form_editor*.tar.gz dist/editor/

# Restore original structure
cp pyproject-engine.toml pyproject.toml  # Default to engine config
cp README-engine.md README.md           # Default to engine README

echo ""
echo "🎉 Build Complete!"
echo "=================="
echo "📁 Engine package:  dist/engine/"
echo "📁 Editor package:  dist/editor/"
echo ""
echo "📋 Installation Commands:"
echo "  Production:   pip install dist/engine/tui_form_engine-*.whl"
echo "  Development:  pip install dist/editor/tui_form_editor-*.whl"
echo ""
echo "📋 PyPI Upload Commands:"
echo "  Engine:  twine upload dist/engine/*"
echo "  Editor:  twine upload dist/editor/*"