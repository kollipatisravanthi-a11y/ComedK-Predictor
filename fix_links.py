import re

input_file = r'c:\Projects\COMEDK_DTL\backend\college_details_data.py'

# Read the file
with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Function to process the dictionary content matches
# We look for: 'code': { ... 'placement': 'URL', ... }
# This is a bit complex to regex replace safely in one go for a huge dict.

# Alternative: We can locate the `college_links_data = {` block and process it line by line.

lines = content.split('\n')
new_lines = []
in_links_dict = False
current_base_url = ""

for line in lines:
    if "college_links_data = {" in line:
        in_links_dict = True
        new_lines.append(line)
        continue
    
    if in_links_dict and line.strip() == "}":
        in_links_dict = False
        new_lines.append(line)
        continue

    if in_links_dict:
        # Check if this line defines a college block start like "    'E001': {"
        # or if it defines a key-value pair like "        'placement': '...',"
        
        # Simple heuristic: specific fixes for known common colleges or generic fix
        
        # Detect placement lines
        if "'placement':" in line:
            # Extract URL
            match = re.search(r"'placement':\s*'([^']*)'", line)
            if match:
                url = match.group(1)
                # If url ends with .in or .com or .org or is just the base, append /placements
                # Check if it looks like a root url (no segments after tld)
                # primitive check: count slashes after protocol
                clean_url = url.rstrip('/')
                if clean_url.count('/') < 3: # e.g. https://site.com is 2 slashes. https://site.com/ is 3.
                     new_url = clean_url + "/placements"
                     line = line.replace(url, new_url)
                elif url.endswith(('.in', '.com', '.org', '.edu', '.ac.in')):
                     new_url = url.rstrip('/') + "/placements"
                     line = line.replace(url, new_url)

        # Detect hostel lines
        if "'hostel':" in line:
             match = re.search(r"'hostel':\s*'([^']*)'", line)
             if match:
                url = match.group(1)
                clean_url = url.rstrip('/')
                if clean_url.count('/') < 3: 
                     new_url = clean_url + "/facilities/hostel"
                     line = line.replace(url, new_url)
                elif url.endswith(('.in', '.com', '.org', '.edu', '.ac.in')):
                     new_url = url.rstrip('/') + "/facilities/hostel"
                     line = line.replace(url, new_url)

    new_lines.append(line)

output_content = '\n'.join(new_lines)

with open(input_file, 'w', encoding='utf-8') as f:
    f.write(output_content)

print("Updated links in college_details_data.py")
