# Script to fix the info bar by removing the justification code

with open(r'f:\trae_projects\Subnet_Planner\windows_app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the start and end of the justification code block
start_line = 3993  # Line after "lines.append(current_line)"
end_line = 4036    # Line before "return "\n".join(lines)"

# Remove the justification code block
fixed_lines = lines[:start_line] + lines[end_line+1:]

# Write the fixed content back to the file
with open(r'f:\trae_projects\Subnet_Planner\windows_app.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("Info bar fixed successfully! Justification code removed.")