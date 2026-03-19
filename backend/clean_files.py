files_to_clean = ['requirements.txt', 'vercel.json']

for filename in files_to_clean:
    try:
        # Read with BOM handling
        with open(filename, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # Write back without BOM
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f" Cleaned {filename}")
    except FileNotFoundError:
        print(f" {filename} not found")

print("Done! Files cleaned of BOM characters.")