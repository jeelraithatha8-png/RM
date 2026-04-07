import os
import re

# Update HTML files for Vercel
files_to_update = ['complete_index.html', 'dashboard.html']

for filename in files_to_update:
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            content = file.read()
        
        # Replace localhost URLs with relative paths
        content = content.replace('http://localhost:8000', '')
        content = content.replace("const API_URL = 'http://localhost:8000'", "const API_URL = ''")
        
        with open(filename, 'w') as file:
            file.write(content)
        
        print(f"✅ Updated {filename} for Vercel")

print("✅ All files updated for Vercel deployment")
