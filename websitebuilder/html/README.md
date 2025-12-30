# HTML Folder Structure Creator

This folder contains `create_html_structure.ps1`, a PowerShell script that will create the directory structure and placeholder HTML files used in this project.

How to run (PowerShell):

```powershell
Set-Location 'c:\coding\github\Generic-projects\html'
.\create_html_structure.ps1
```

What it does:
- Creates subfolders (e.g., `Automotive`, `ecommerce`, `Education`, ...).
- Creates placeholder `.html` files in each subfolder if they do not already exist.
- Generates `structure_tree.txt` inside the `html` folder with a listing of folders/files.

Notes:
- Running the script again will not overwrite existing files; it only creates missing items.
- If you want empty files removed or updated, edit the script accordingly.
