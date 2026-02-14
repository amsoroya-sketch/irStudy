#!/bin/bash
# Ralph Template Engine
# Handles template loading, variable substitution, and PRD generation

set -euo pipefail

# Global configuration
DEFAULT_TEMPLATE_DIR="templates/ralph-templates"
CUSTOM_TEMPLATE_DIR=".ralph/templates/custom"

# List all available templates in a directory
# Usage: list_templates [template_dir] [fallback_dir]
list_templates() {
    local template_dir="${1:-$DEFAULT_TEMPLATE_DIR}"
    local fallback_dir="${2:-}"

    # Check if template directory exists
    if [ ! -d "$template_dir" ]; then
        # Try fallback if provided
        if [ -n "$fallback_dir" ] && [ -d "$fallback_dir" ]; then
            template_dir="$fallback_dir"
        else
            echo "ERROR: Template directory not found: $template_dir" >&2
            return 1
        fi
    fi

    # Find all JSON template files
    find "$template_dir" -type f -name "*.json" 2>/dev/null | while read -r file; do
        basename "$file" .json
    done

    return 0
}

# Load a template file and return JSON content
# Usage: load_template <template_file>
load_template() {
    local template_file="$1"

    # Check if file exists
    if [ ! -f "$template_file" ]; then
        echo "ERROR: Template file not found: $template_file" >&2
        return 1
    fi

    # Validate JSON syntax
    if ! jq empty "$template_file" 2>/dev/null; then
        echo "ERROR: Invalid JSON in template file: $template_file" >&2
        return 1
    fi

    # Return template content
    cat "$template_file"

    return 0
}

# Validate template structure (has required $template field)
# Usage: validate_template_structure <template_json>
validate_template_structure() {
    local template="$1"

    # Check for required $template field
    if ! echo "$template" | jq -e 'has("$template")' > /dev/null 2>&1; then
        echo "ERROR: Template missing required '\$template' field" >&2
        return 1
    fi

    # Check for $variables field (recommended)
    if ! echo "$template" | jq -e 'has("$variables")' > /dev/null 2>&1; then
        echo "WARNING: Template missing '\$variables' field (optional)" >&2
    fi

    return 0
}

# Extract variables from template
# Usage: extract_variables <template_json>
extract_variables() {
    local template="$1"

    # Extract variable names from $variables field
    echo "$template" | jq -r '.$variables | keys[]' 2>/dev/null || echo ""
}

# Get default value for a variable
# Usage: get_variable_default <template_json> <variable_name>
get_variable_default() {
    local template="$1"
    local var_name="$2"

    echo "$template" | jq -r ".\$variables[\"$var_name\"] // \"\"" 2>/dev/null
}

# Substitute a single variable in template
# Usage: substitute_variable <template_json> <var_name> <var_value>
substitute_variable() {
    local template="$1"
    local var_name="$2"
    local var_value="$3"

    # Calculate transformed values
    local snake_case=$(echo "$var_value" | tr ' ' '_' | tr '[:upper:]' '[:lower:]')
    local upper=$(echo "$var_value" | tr '[:lower:]' '[:upper:]')

    # Escape special characters for JSON strings
    # Must escape: backslash (\), double quote ("), newline (\n), tab (\t)
    escape_for_json() {
        local str="$1"
        # Escape backslashes first (must be first!)
        str="${str//\\/\\\\}"
        # Escape double quotes
        str="${str//\"/\\\"}"
        # Escape newlines
        str="${str//$'\n'/\\n}"
        # Escape tabs
        str="${str//$'\t'/\\t}"
        echo "$str"
    }

    local escaped_value=$(escape_for_json "$var_value")
    local escaped_snake=$(escape_for_json "$snake_case")
    local escaped_upper=$(escape_for_json "$upper")

    # Escape backslashes again for awk (awk interprets backslashes in -v arguments)
    escaped_value="${escaped_value//\\/\\\\}"
    escaped_snake="${escaped_snake//\\/\\\\}"
    escaped_upper="${escaped_upper//\\/\\\\}"

    # Convert template to compact JSON string
    local template_str=$(echo "$template" | jq -c '.')

    # Use awk for safe string replacement
    template_str=$(echo "$template_str" | awk -v var="{{$var_name}}" -v val="$escaped_value" '{gsub(var, val); print}')
    template_str=$(echo "$template_str" | awk -v var="{{${var_name^^}_SNAKE_CASE}}" -v val="$escaped_snake" '{gsub(var, val); print}')
    template_str=$(echo "$template_str" | awk -v var="{{${var_name^^}_UPPER}}" -v val="$escaped_upper" '{gsub(var, val); print}')

    echo "$template_str"
}

# Substitute multiple variables in template
# Usage: substitute_variables <template_json> <var1_name> <var1_value> [var2_name] [var2_value] ...
substitute_variables() {
    local template="$1"
    shift

    # Process variable pairs
    while [ $# -ge 2 ]; do
        local var_name="$1"
        local var_value="$2"
        shift 2

        template=$(substitute_variable "$template" "$var_name" "$var_value")
    done

    echo "$template"
}

# Substitute variables with defaults for missing values
# Usage: substitute_variables_with_defaults <template_json> <var_name> <var_value> <default_value>
substitute_variables_with_defaults() {
    local template="$1"
    local var_name="$2"
    local var_value="$3"
    local default_value="$4"

    # Use default if value is empty
    if [ -z "$var_value" ]; then
        var_value="$default_value"
    fi

    substitute_variable "$template" "$var_name" "$var_value"
}

# Generate next task ID based on existing PRDs
# Usage: generate_task_id <prds_directory>
generate_task_id() {
    local prds_dir="${1:-prds}"

    # Find highest existing task ID
    local max_id=0

    if [ -d "$prds_dir" ]; then
        shopt -s nullglob  # Don't expand globs if no match
        for file in "$prds_dir"/TASK-*.json "$prds_dir"/TEST-*.json; do
            if [ -f "$file" ]; then
                # Extract numeric ID from filename
                local id=$(basename "$file" .json | sed 's/^[A-Z]*-0*//')
                if [ "$id" -gt "$max_id" ] 2>/dev/null; then
                    max_id=$id
                fi
            fi
        done
        shopt -u nullglob  # Restore default
    fi

    # Increment and format with leading zeros
    local new_id=$((max_id + 1))
    printf "%03d" "$new_id"
}

# Replace {{AUTO_INCREMENT}} placeholder with next task ID
# Usage: substitute_auto_increment <template_json> <prds_directory>
substitute_auto_increment() {
    local template="$1"
    local prds_dir="${2:-prds}"

    local task_id=$(generate_task_id "$prds_dir")

    echo "$template" | sed "s|{{AUTO_INCREMENT}}|${task_id}|g"
}

# Remove template metadata fields ($template, $variables)
# Usage: finalize_template <template_json>
finalize_template() {
    local template="$1"

    echo "$template" | jq 'del(.["$template"], .["$variables"])'
}

# Find template file by name
# Usage: find_template <template_name> [custom_dir] [default_dir]
find_template() {
    local template_name="$1"
    local custom_dir="${2:-$CUSTOM_TEMPLATE_DIR}"
    local default_dir="${3:-$DEFAULT_TEMPLATE_DIR}"

    # Try custom directory first
    if [ -f "$custom_dir/${template_name}.json" ]; then
        echo "$custom_dir/${template_name}.json"
        return 0
    fi

    # Try default directory
    if [ -f "$default_dir/${template_name}.json" ]; then
        echo "$default_dir/${template_name}.json"
        return 0
    fi

    # Template not found
    echo "ERROR: Template not found: $template_name" >&2
    return 1
}

# Functions are available after sourcing this script
# No need to export when sourcing
